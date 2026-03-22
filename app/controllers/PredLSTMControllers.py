import logging
import os

import joblib
import numpy as np
import torch

from app.MLearning.LSTM_Model.model import LSTM_Production_Model


logger = logging.getLogger(__name__)

class PredLSTMController:
    def __init__(self):
        # Define absolute paths based on project structure
        self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        model_candidates = [
            os.path.join(self.base_path, 'models', 'lstm_model.pth'),
            os.path.join(self.base_path, 'app', 'models', 'lstm_model.pth'),
        ]
        scaler_candidates = [
            os.path.join(self.base_path, 'models', 'scaler.pkl'),
            os.path.join(self.base_path, 'app', 'MLearning', 'preprocessing', 'artifacts', 'scaler.pkl'),
        ]

        self.model_path = self._resolve_artifact_path(model_candidates)
        self.scaler_path = self._resolve_artifact_path(scaler_candidates)

        self.scaled_feature_count = 14
        self.total_feature_count = 21

        # Load the fitted scaler (required only when raw engineered features are passed)
        try:
            self.scaler = joblib.load(self.scaler_path) if self.scaler_path else None
            if self.scaler_path:
                logger.info(f"Scaler loaded from: {self.scaler_path}")
            else:
                logger.warning("No scaler file found. Preprocessed inputs are still supported.")
        except Exception as e:
            logger.warning(f"Failed to load scaler from {self.scaler_path}: {e}")
            self.scaler = None

        # Initialize the model architecture and load weights
        try:
            self.model = LSTM_Production_Model(input_size=21, hidden_size=128, num_layers=3, dropout=0.3)
            # map_location='cpu' ensures it works even if trained on GPU
            self.model.load_state_dict(torch.load(self.model_path, map_location=torch.device('cpu')))
            self.model.eval() # Set to evaluation mode for inference
            logger.info(f"LSTM model loaded from: {self.model_path}")
        except Exception as e:
            logger.warning(f"Failed to load model weights from {self.model_path}: {e}")
            self.model = None

    @staticmethod
    def _resolve_artifact_path(candidates: list) -> str | None:
        for path in candidates:
            if os.path.exists(path):
                return path
        return None

    def _scale_14_plus_7(self, feature_matrix: np.ndarray) -> np.ndarray:
        """
        Applies scaler only to the first 14 columns and keeps last 7 passthrough columns unchanged.
        Expects shape (seq_len, 21).
        """
        if self.scaler is None:
            raise RuntimeError("Scaler is not available for raw feature scaling.")

        if feature_matrix.shape[1] != self.total_feature_count:
            raise ValueError(
                f"Invalid feature width: {feature_matrix.shape[1]}. Expected {self.total_feature_count}."
            )

        scaled_part = self.scaler.transform(feature_matrix[:, :self.scaled_feature_count])
        passthrough_part = feature_matrix[:, self.scaled_feature_count:]
        return np.hstack([scaled_part, passthrough_part])

    def _prepare_tensor(self, features: list, already_preprocessed: bool) -> torch.Tensor:
        data = np.array(features, dtype=np.float32)

        # Case A: single step vector (21,)
        if data.ndim == 1 and data.shape[0] == self.total_feature_count:
            seq = data.reshape(1, self.total_feature_count)
            if not already_preprocessed:
                seq = self._scale_14_plus_7(seq)
            return torch.tensor(seq, dtype=torch.float32).unsqueeze(0)

        # Case B: sequence matrix (seq_len, 21)
        if data.ndim == 2 and data.shape[1] == self.total_feature_count:
            seq = data
            if not already_preprocessed:
                seq = self._scale_14_plus_7(seq)
            return torch.tensor(seq, dtype=torch.float32).unsqueeze(0)

        # Case C: already batched (1, seq_len, 21)
        if data.ndim == 3 and data.shape[0] == 1 and data.shape[2] == self.total_feature_count:
            if not already_preprocessed:
                seq = data[0]
                seq = self._scale_14_plus_7(seq)
                return torch.tensor(seq, dtype=torch.float32).unsqueeze(0)
            return torch.tensor(data, dtype=torch.float32)

        raise ValueError(
            f"Invalid input shape {data.shape}. Expected (21,), (seq_len,21), or (1,seq_len,21)."
        )

    def predict(self, features: list, threshold: float = 0.5, already_preprocessed: bool = True) -> dict:
        """
        Runs inference on the LSTM model.
        Expects one of the following:
        - list of 21 features
        - list[list] with shape (seq_len, 21)
        - list[list[list]] with shape (1, seq_len, 21)

        Parameters:
        - already_preprocessed=True for features generated by OnlineFeatureEngineer
          (14 features already scaled + 7 passthrough already concatenated).
        - already_preprocessed=False for raw engineered features (controller applies 14+7 logic).
        """
        if self.model is None:
            return {"status": False, "error": "Model is not properly loaded during initialization."}
            
        try:
            tensor_data = self._prepare_tensor(features, already_preprocessed=already_preprocessed)

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
                "prediction": signal,
                "threshold_used": threshold
            }
            
        except Exception as e:
            return {"status": False, "error": f"Error during prediction: {str(e)}"}

# Instantiate a singleton to be used across the FastApi runtime
lstm_controller = PredLSTMController()
