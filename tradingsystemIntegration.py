class TradingSystem(PerformanceAnalyzer):
    def __init__(self):
        super().__init__()
        self.real_time_metrics = {}
        
    def on_trade_update(self, trade_data):
        self._update_trade_db(trade_data)
        
        self.real_time_metrics = self.generate_performance_report()
        
        self._update_dashboard()

    def _update_dashboard(self):
        print(f"\n=== Real-Time Metrics ===")
        print(f"Current PnL: ${self.real_time_metrics['pnl']:,.2f}")
        print(f"Win Rate: {self.real_time_metrics['win_rate']:.1%}")
        print(f"Sortino Ratio: {self.real_time_metrics['sortino']:.2f}")
        print(f"Max Drawdown: {self.real_time_metrics['max_drawdown']:.1%}")
        print(f"Avg Slippage: {self.real_time_metrics['slippage']['average_slippage']:.2%}")

    def historical_analysis(self):
        df = pd.read_sql('''
            SELECT *,
                   (exit_price - entry_price)/entry_price AS return,
                   julianday(exit_time) - julianday(entry_time) AS duration_days
            FROM trades
        ''', self.trades_conn)
        
        token_stats = df.groupby('token_address').agg({
            'return': ['mean', 'std', 'count'],
            'duration_days': 'mean'
        })
        
        df['hour'] = pd.to_datetime(df['entry_time']).dt.hour
        time_stats = df.groupby('hour').agg({
            'return': 'mean',
            'slippage': 'mean'
        })
        
        return {
            'token_analysis': token_stats,
            'time_analysis': time_stats,
            'correlation_matrix': df[['return', 'slippage', 'latency']].corr()
        }
