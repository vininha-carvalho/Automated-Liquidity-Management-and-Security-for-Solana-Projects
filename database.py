import sqlite3
import pandas as pd
from datetime import datetime

class TradeAnalyzer:
    def __init__(self, db_path='trading_performance.db'):
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY,
                token_address TEXT NOT NULL,
                entry_time DATETIME NOT NULL,
                exit_time DATETIME,
                entry_price REAL,
                exit_price REAL,
                amount_usd REAL,
                wallet_percentage REAL,
                strategy_name TEXT,
                fees REAL,
                slippage REAL,
                pnl REAL,
                status TEXT CHECK(status IN ('open', 'closed'))
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strategies (
                strategy_id INTEGER PRIMARY KEY,
                strategy_name TEXT UNIQUE,
                parameters TEXT,
                win_rate REAL,
                avg_profit REAL,
                last_used DATETIME)
        ''')
        
        self.conn.commit()
