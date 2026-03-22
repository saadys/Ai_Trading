


class Config:
    """LSTM Configuration - alignée avec l'architecture réelle de production"""
    input_size: int = 21          # 18 New Features + 3 VMD Modes
    hidden_size: int = 128       
    num_layers: int = 3           
    batch_first: bool = True
    dropout: float = 0.3          
    
    learning_rate: float = 0.001
    weight_decay: float = 1e-5    
    max_grad_norm: float = 1.0    
    batch_size: int = 128         
    
    lookback: int = 192           
    future_window: int = 96       
    
    scheduler_factor: float = 0.5 
    scheduler_patience: int = 5   
    
    early_stopping_patience: int = 10
    
    huber_delta: float = 0.3   
