import torch
import torch.nn as nn
import torch.nn.functional as F

class BayesianLSTM(nn.Module):
    """
    Bayesian LSTM using Monte Carlo Dropout (MC Dropout) to capture epistemic uncertainty.
    
    This architecture mirrors strict interface compatibility with the existing V1 model,
    but treats Dropout not just as a regularization technique, but as a Bayesian approximation.
    """
    def __init__(self, input_size: int = 21, hidden_size: int = 128, num_layers: int = 3, dropout: float = 0.2):
        super(BayesianLSTM, self).__init__()
        
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.dropout_p = dropout
        
        # Unified LSTM with multiple layers
        # Note: internal dropout is only applied between layers (if num_layers > 1).
        # We enable it here, but we also enforce training mode in prediction for MC effect.
        self.lstm = nn.LSTM(
            input_size=input_size, 
            hidden_size=hidden_size, 
            num_layers=num_layers, 
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0
        )
        
        # Fully Connected Layer (Output)
        self.fc = nn.Linear(hidden_size, 1)
        
        # Initialize weights for stability
        self._init_weights()
        
    def _init_weights(self):
        """
        Apply Xavier (Glorot) & Kaiming (He) initialization to stabilize learning
        and prevent gradient vanishing/exploding at start.
        """
        for name, param in self.lstm.named_parameters():
            if 'weight_ih' in name:
                # Xavier for Input-Hidden weights (Sigmoid/Tanh activations inside LSTM)
                nn.init.xavier_uniform_(param.data)
            elif 'weight_hh' in name:
                # Orthogonal for Hidden-Hidden to preserve gradient norm
                nn.init.orthogonal_(param.data)
            elif 'bias' in name:
                param.data.fill_(0)
                # Initialize forget gate bias to 1 to help long-term memory
                # Bias layout in PyTorch LSTM: (input, forget, cell, output)
                n = param.size(0)
                start, end = n//4, n//2
                param.data[start:end].fill_(1.)

        # Kaiming for the Linear layer (often follows ReLU-like behavior, 
        # though here it's raw regression, Kaiming is robust)
        nn.init.kaiming_normal_(self.fc.weight, mode='fan_in', nonlinearity='linear')
        if self.fc.bias is not None:
             self.fc.bias.data.fill_(0.01)
        
    def forward(self, x):
        # x shape: (Batch, Seq, Feature)
        
        # 1. LSTM Forward
        # To strictly enforce MC Dropout within LSTM (between layers), 
        # the model must be in training mode or checking self.training.
        # Generally, we control this via predict_with_uncertainty().
        out, _ = self.lstm(x)
        
        # 2. Extract Last Time Step
        # out shape: (Batch, Seq, Hidden)
        last_step_feature = out[:, -1, :]
        
        # 3. MC Dropout before Dense Layer
        # Crucial: training=True forces dropout mask even during eval loops.
        dropped_feature = F.dropout(last_step_feature, p=self.dropout_p, training=True)
        
        # 4. Final Prediction
        prediction = self.fc(dropped_feature)
        
        return prediction

    def predict_with_uncertainty(self, x, n_iter=50):
        """
        Perform Monte Carlo Dropout Prediction.
        
        Args:
            x (Tensor): Input tensor (Batch, Seq, Feature).
            n_iter (int): Number of stochastic forward passes.
            
        Returns:
            mean_pred (Tensor): The average prediction (Batch, 1).
            std_pred (Tensor): The uncertainty (Standard Deviation) (Batch, 1).
        """
        # Enforce Training Mode for the LSTM internal dropout layers
        # This ensures the 'dropout' arg in nn.LSTM is respected during inference steps.
        original_mode = self.training
        self.train()
        
        predictions = []
        
        # No grad context for efficiency (we just want forward sampling)
        with torch.no_grad():
            for _ in range(n_iter):
                # Each forward call generates a unique dropout mask
                pred = self.forward(x)
                predictions.append(pred)
        
        # Restore original mode (e.g., if it was in eval for other reasons)
        self.train(original_mode)
        
        # Stack predictions: (n_iter, Batch, 1)
        predictions = torch.stack(predictions)
        
        # Calculate Mean (Expected Value) and Std (Uncertainty)
        mean_pred = predictions.mean(dim=0)
        std_pred = predictions.std(dim=0)
        
        return mean_pred, std_pred