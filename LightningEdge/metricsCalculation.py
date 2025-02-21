import numpy as np
import pandas as pd
from datetime import datetime

class PerformanceAnalyzer:
    def __init__(self, trades_db='trades.db', price_history_db='prices.db'):
        self.trades_conn = sqlite3.connect(trades_db)
        self.prices_conn = sqlite3.connect(price_history_db)
        
    def calculate_pnl(self, include_open=True):
        query = '''
            SELECT token_address, entry_price, exit_price, amount_usd, status 
            FROM trades
        ''' + (" WHERE status='closed'" if not include_open else "")
        
        df = pd.read_sql(query, self.trades_conn)
        
        df['realized_pnl'] = np.where(
            df['status'] == 'closed',
            (df['exit_price'] - df['entry_price']) / df['entry_price'] * df['amount_usd'],
            0
        )
        
        current_prices = self._get_current_prices()
        df['unrealized_pnl'] = np.where(
            df['status'] == 'open',
            (current_prices[df['token_address']] - df['entry_price']) / df['entry_price'] * df['amount_usd'],
            0
        )
        
        return df['realized_pnl'].sum() + df['unrealized_pnl'].sum()

    def win_rate_profit_factor(self):
        df = pd.read_sql('''
            SELECT amount_usd, entry_price, exit_price, fees 
            FROM trades WHERE status='closed'
        ''', self.trades_conn)
        
        df['profit'] = (df['exit_price'] - df['entry_price']) * (df['amount_usd'] / df['entry_price'])
        df['gross_profit'] = df[df['profit'] > 0]['profit'].sum()
        df['gross_loss'] = abs(df[df['profit'] < 0]['profit'].sum())
        
        win_rate = len(df[df['profit'] > 0]) / len(df)
        profit_factor = df['gross_profit'] / df['gross_loss'] if df['gross_loss'] != 0 else np.inf
        
        return win_rate, profit_factor

    def sortino_ratio(self, risk_free_rate=0):
        returns = self._get_returns_series()
        downside_returns = returns[returns < risk_free_rate]
        downside_deviation = downside_returns.std()
        
        if downside_deviation == 0:
            return np.inf
            
        excess_returns = returns.mean() - risk_free_rate
        return excess_returns / downside_deviation

    def max_drawdown(self):
        portfolio_values = self._get_portfolio_timeseries()
        peak = portfolio_values.cummax()
        drawdown = (peak - portfolio_values) / peak
        return drawdown.max()

    def _get_returns_series(self):

        df = pd.read_sql('''
            SELECT entry_time, exit_time, entry_price, exit_price 
            FROM trades WHERE status='closed'
        ''', self.trades_conn)
        
        df['duration'] = (pd.to_datetime(df['exit_time']) - pd.to_datetime(df['entry_time'])).dt.total_seconds()
        df['return'] = (df['exit_price'] / df['entry_price']) - 1
        return df.set_index('exit_time')['return']

    def _get_portfolio_timeseries(self):
        pass
    def calculate_gas_metrics(self):
        df = pd.read_sql('''
            SELECT SUM(gas_fees) as total_gas, 
                   AVG(gas_fees) as avg_gas,
                   COUNT(*) as trades_count
            FROM trades
        ''', self.trades_conn)
        
        return {
            'total_gas': df['total_gas'][0],
            'avg_gas_per_trade': df['avg_gas'][0],
            'gas_percentage': df['total_gas'][0] / self.calculate_pnl()
        }

    def slippage_analysis(self):
        df = pd.read_sql('''
            SELECT AVG(slippage) as avg_slippage,
                   AVG(price_impact) as avg_price_impact
            FROM trades
        ''', self.trades_conn)
        
        return {
            'average_slippage': df['avg_slippage'][0],
            'average_price_impact': df['avg_price_impact'][0]
        }

    def latency_metrics(self):
        df = pd.read_sql('''
            SELECT AVG(latency) as avg_latency,
                   MAX(latency) as max_latency
            FROM trades
        ''', self.trades_conn)
        
        return {
            'average_latency': df['avg_latency'][0],
            'worst_latency': df['max_latency'][0]
        }

    def vs_buy_and_hold(self):
        prices = pd.read_sql('''
            SELECT token_address, date, price 
            FROM price_history
        ''', self.prices_conn)
        
        algo_returns = self._get_returns_series()
        
        bh_returns = prices.groupby('token_address').apply(
            lambda x: x['price'].iloc[-1] / x['price'].iloc[0] - 1
        )
        
        return {
            'algorithm_return': algo_returns.mean(),
            'bh_return': bh_returns.mean(),
            'outperformance': algo_returns.mean() - bh_returns.mean()
        }

    def generate_performance_report(self):

        return {
            'pnl': self.calculate_pnl(),
            'win_rate': self.win_rate_profit_factor()[0],
            'profit_factor': self.win_rate_profit_factor()[1],
            'sortino': self.sortino_ratio(),
            'max_drawdown': self.max_drawdown(),
            'gas_metrics': self.calculate_gas_metrics(),
            'slippage': self.slippage_analysis(),
            'latency': self.latency_metrics(),
            'vs_bh': self.vs_buy_and_hold()
        }
