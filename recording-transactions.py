    def log_trade(self, token_address: str, entry_price: float, 
                amount_usd: float, wallet_percentage: float, 
                strategy: str, fees: float = 0):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO trades 
            (token_address, entry_time, entry_price, amount_usd,
             wallet_percentage, strategy_name, fees, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'open')
        ''', (token_address, datetime.now(), entry_price, 
              amount_usd, wallet_percentage, strategy, fees))
        self.conn.commit()
