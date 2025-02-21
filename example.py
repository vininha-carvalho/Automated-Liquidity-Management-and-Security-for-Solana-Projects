if __name__ == "__main__":
    analyzer = TradeAnalyzer()
    
    analyzer.log_trade(
        token_address="0xabc...",
        entry_price=150.50,
        amount_usd=1000,
        wallet_percentage=5.0,
        strategy="mean_reversion",
        fees=2.50
    )
    
    analyzer.update_trade(
        trade_id=1,
        exit_price=165.20,
        slippage=0.3,
        pnl=((165.20 - 150.50)/150.50)*100 - 0.3
    )
    
    print(analyzer.calculate_performance())
    
    # Анализ стратегий
    print(analyzer.analyze_strategies().sort_values('win_rate', ascending=False))
    
    # Запуск реалтайм ленты
    analyzer.live_performance_tape(update_interval=30)
