import torch
import torch.nn as nn
from Config import Config

class LSTM_Production_Model(nn.Module):
    def __init__(self, input_size: int):
        super(LSTM_Production_Model, self).__init__()
        
        #First LSTM Layer
        # returns (batch, seq, hidden_size) 
        self.lstm1 = nn.LSTM(
            input_size=input_size, 
            hidden_size=Config.hidden_size.value, 
            num_layers=Config.num_layers.value, 
            batch_first=Config.batch_first.value
        )
        
        #Dropout Layer (20%)
        self.dropout = nn.Dropout(p=0.2)
        
        #Second LSTM Layer
        self.lstm2 = nn.LSTM(
            input_size=Config.hidden_size.value, 
            hidden_size=Config.hidden_size.value, 
            num_layers=Config.num_layers.value, 
            batch_first=Config.batch_first.value
        )
        
        #Dense Output Layer
        self.fc = nn.Linear(Config.hidden_size.value, 1)
        
    def forward(self, x):
        # x shape: (Batch_Size, Sequence_Length, Input_Features)

        #Layer 1
        # out1 shape: (Batch, Seq, 64)
        out1, _ = self.lstm1(x)
        
        #Dropout (20%)
        out1 = self.dropout(out1)
        
        #Layer 2: LSTM (32) 
        # out2 shape: (Batch, Seq, 32)
        out2, _ = self.lstm2(out1)
        
        # Shape becomes: (Batch, 32)
        last_step_feature = out2[:, -1, :]
        
        #Dense Output 
        # prediction shape: (Batch, 1)
        prediction = self.fc(last_step_feature)
        
        return prediction
