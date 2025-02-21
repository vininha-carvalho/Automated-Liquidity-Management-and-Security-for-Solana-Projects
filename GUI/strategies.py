import pandas as pd

class UserStrategy:
    @staticmethod
    def momentum_strategy(data, lookback=3):
        signals = {}
        for addr, values in data.items():
            hist = pd.Series(values['price_history'])
            if hist[-1] > hist.rolling(lookback).mean()[-2]:
                signals[addr] = 'buy'
        return signals
    
    @staticmethod
    def mean_reversion_strategy(data, threshold=0.05):
        signals = {}
        for addr, values in data.items():
            ma = pd.Series(values['price_history']).mean()
            if values['price'] < ma * (1 - threshold):
                signals[addr] = 'buy'
        return signals
