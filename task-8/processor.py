import pandas as pd
from collections import deque
import numpy as np

class SensorProcessor:
    def __init__(self, window_size=60):
        self.window_size = window_size
        self.data_buffer = deque(maxlen=window_size)
    
    def process(self, value):
        self.data_buffer.append(value)
        
        # Convert to series for windowed stats
        series = pd.Series(list(self.data_buffer))
        
        moving_avg = series.mean()
        std_dev = series.std()
        
        # Z-score calculation (handle zero std_dev)
        if std_dev and not np.isnan(std_dev) and std_dev != 0:
            z_score = (value - moving_avg) / std_dev
        else:
            z_score = 0.0
            
        return {
            "value": float(value),
            "avg": float(moving_avg),
            "z_score": float(z_score),
            "status": self._get_status(value, z_score)
        }
    
    def _get_status(self, value, z_score):
        if value > 100 or abs(z_score) > 3.0:
            return "CRITICAL"
        if value > 85 or abs(z_score) > 2.0:
            return "WARNING"
        return "NORMAL"
