    def analyze_strategies(self):
        strategy_df = pd.read_sql('''
            SELECT 
                strategy_name,
                COUNT(*) AS total_trades,
                AVG(pnl) AS avg_profit,
                (SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) * 1.0 / COUNT(*)) * 100 AS win_rate,
                MAX(pnl) AS best_trade,
                MIN(pnl) AS worst_trade,
                AVG((julianday(exit_time) - julianday(entry_time)) * 24 AS avg_duration
            FROM trades
            WHERE status = 'closed'
            GROUP BY strategy_name
            ORDER BY win_rate DESC
        ''', self.conn)
        
        for strategy in strategy_df['strategy_name']:
            trades = pd.read_sql(f'''
                SELECT pnl FROM trades 
                WHERE strategy_name = '{strategy}' AND status = 'closed'
            ''', self.conn)
            downside_risk = trades[trades['pnl'] < 0]['pnl'].std()
            strategy_df.loc[strategy_df['strategy_name'] == strategy, 'sortino'] = \
                trades['pnl'].mean() / downside_risk if downside_risk != 0 else 0
        
        return strategy_df
