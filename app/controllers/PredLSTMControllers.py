import torch
import joblib
import os
import numpy as np
from app.MLearning.LSTM_Model.model import LSTM_Production_Model

class PredLSTMController:
    def __init__(self):
        # Define absolute paths based on project structure
        self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Primary model path
        self.model_path = os.path.join(self.base_path, 'app', 'models', 'lstm_model.pth')
        self.scaler_path = os.path.join(self.base_path, 'app', 'MLearning', 'preprocessing', 'artifacts', 'scaler.pkl')
        
        # Load the fitted scaler
        try:
            self.scaler = joblib.load(self.scaler_path)
        except Exception as e:
            print(f"Warning: Failed to load scaler from {self.scaler_path}: {e}")
            self.scaler = None

        # Initialize the model architecture and load weights
        try:
            self.model = LSTM_Production_Model(input_size=21, hidden_size=128, num_layers=3, dropout=0.3)
            # map_location='cpu' ensures it works even if trained on GPU
            self.model.load_state_dict(torch.load(self.model_path, map_location=torch.device('cpu')))
            self.model.eval() # Set to evaluation mode for inference
        except Exception as e:
            print(f"Warning: Failed to load model weights from {self.model_path}: {e}")
            self.model = None

    def predict(self, features: list, threshold: float = 0.5) -> dict:
        """
        Runs inference on the LSTM model.
        Expects a list of 21 features (single time step) or a list of lists (sequence).
        """
        if self.model is None or self.scaler is None:
            return {"status": False, "error": "Model or scaler not properly loaded during initialization."}
            
        try:
            data = np.array(features, dtype=np.float32)
            
            # Adapt shape for scaler and PyTorch
            # The model expects input shape: (batch_size, sequence_length, features)
            if len(data.shape) == 1 and data.shape[0] == 21:
                # Single sequence step: shape (21,) -> (1, 21) for scaler
                data_scaled = self.scaler.transform(data.reshape(1, -1))
                # Tensor shape -> (1, 1, 21) -> (batch=1, seq_len=1, features=21)
                tensor_data = torch.tensor(data_scaled, dtype=torch.float32).unsqueeze(1)
            elif len(data.shape) == 2 and data.shape[1] == 21:
                # Multiple sequence steps: shape (seq_len, 21)
                data_scaled = self.scaler.transform(data)
                # Tensor shape -> (1, seq_len, 21)
                tensor_data = torch.tensor(data_scaled, dtype=torch.float32).unsqueeze(0)
            else:
                return {"status": False, "error": f"Invalid input shape {data.shape}. Expected 21 features per step."}

            # Forward pass (Inference)
            with torch.no_grad():
                prediction_tensor = self.model(tensor_data)
                probability = prediction_tensor.item() # Extract float probability
            
            # Generate actionable signal based on probability and threshold
            signal = "BUY" if probability > threshold else "SELL"
            
            return {
                "status": True,
                "probability": round(probability, 4),
                "signal": signal,
                "threshold_used": threshold
            }
            
        except Exception as e:
            return {"status": False, "error": f"Error during prediction: {str(e)}"}

# Instantiate a singleton to be used across the FastApi runtime
lstm_controller = PredLSTMController()
