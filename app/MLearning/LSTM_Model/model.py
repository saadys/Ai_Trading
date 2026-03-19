import torch
import torch.nn as nn
from .Config import Config

class LSTM_Production_Model(nn.Module):
    def __init__(self, input_size: int = 21, hidden_size: int = 128, num_layers: int = 3, dropout: float = 0.3):
        super(LSTM_Production_Model, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.dropout_p = dropout
        

        self.lstm = nn.LSTM(
            input_size=input_size, 
            hidden_size=hidden_size, 
            num_layers=num_layers, 
            batch_first=True,
            dropout=dropout  
        )
        

        self.batch_norm = nn.BatchNorm1d(hidden_size)
        

        self.fc1 = nn.Linear(hidden_size, 64)   
        self.relu = nn.ReLU()                   
        self.dropout_fc = nn.Dropout(0.3)       
        self.fc2 = nn.Linear(64, 1)            
        
    def forward(self, x):
        out, _ = self.lstm(x)

        last_step_feature = out[:, -1, :]

        last_step_feature = self.batch_norm(last_step_feature)

        x = self.fc1(last_step_feature)
        x = self.relu(x)                       
        x = self.dropout_fc(x)  
        
        prediction = torch.sigmoid(self.fc2(x))
        
        return prediction
