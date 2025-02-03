import tensorflow as tf
from tensorflow.keras.layers import LSTM, Dense

class LiquidityPredictor(tf.keras.Model):
    def __init__(self):
        super().__init__()
        self.lstm1 = LSTM(64, return_sequences=True)
        self.lstm2 = LSTM(32)
        self.dense = Dense(1, activation='sigmoid')

    def call(self, inputs):
        # inputs: (batch_size, window_size, features)
        x = self.lstm1(inputs)
        x = self.lstm2(x)
        return self.dense(x)  # Прогноз ликвидности [0-1]

def calculate_risk(order_size: float, prediction: float) -> float:
    """Calculates the maximum allowable order size"""
    MAX_RISK = 0.02  # 2% от общего капитала
    return min(order_size, MAX_RISK / (1 - prediction))
