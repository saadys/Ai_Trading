import torch
import torch.nn as nn
from .Config import Config

class LSTM_Production_Model(nn.Module):
    def __init__(self, input_size: int, hidden_size: int = 128, num_layers: int = 3, dropout: float = 0.2):
        super(LSTM_Production_Model, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # Unified LSTM with multiple layers and dropout
        self.lstm = nn.LSTM(
            input_size=input_size, 
            hidden_size=hidden_size, 
            num_layers=num_layers, 
            batch_first=True,
            dropout=dropout
        )
        
        # Output Layer
        self.fc = nn.Linear(hidden_size, 1)
        
    def forward(self, x):
        # x shape: (Batch, Seq, Input)
        
        # LSTM output: (Batch, Seq, Hidden)
        out, _ = self.lstm(x)
        
        # We only care about the last time step for prediction
        # last_step shape: (Batch, Hidden)
        last_step_feature = out[:, -1, :]
        
        # Dense Output
        prediction = self.fc(last_step_feature)
        
        return prediction
