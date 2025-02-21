    def calculate_performance(self, token_address: str = None):
        query = '''
            SELECT 
                token_address,
                COUNT(*) AS total_trades,
                SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) AS profitable_trades,
                AVG(pnl) AS avg_pnl,
                SUM(pnl) AS total_pnl,
                AVG(fees) AS avg_fees,
                AVG(slippage) AS avg_slippage,
                AVG((julianday(exit_time) - julianday(entry_time)) * 24 AS avg_duration_hours,
                MAX(pnl) AS max_profit,
                MIN(pnl) AS max_loss
            FROM trades
            WHERE status = 'closed'
        '''
        
        if token_address:
            query += f" AND token_address = '{token_address}'"
            
        df = pd.read_sql(query, self.conn)
        
        df['win_rate'] = df['profitable_trades'] / df['total_trades']
        df['profit_factor'] = df['total_pnl'] / abs(df['total_pnl'] - df['profitable_trades'] * df['avg_pnl'])
        return df
