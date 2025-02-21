async def main():
    config = {
        'rpc_url': 'https://api.mainnet-beta.solana.com',
        'helius_key': 'your_api_key',
        'pools': [
            '7XawhbbxtsRcQA8KTkHT9f9nc6d69UwqCDh6U5EEbEmX',
            '5z3EqYQo8H4K1C4z6G5S5jJ5Z5X5Z5X5Z5X5Z5X5Z5X5'
        ]
    }
    
    fetcher = SolanaDataFetcher(config['rpc_url'], config['helius_key'])
    processor = MarketDataProcessor(fetcher)
    await processor.initialize_pools([Pubkey.from_string(addr) for addr in config['pools']])
    
    ts_manager = TimeSeriesManager()
    ts_manager.create_series('SOL_price', window_size=300)
    
    event_detector = MarketEventDetector(processor)
    event_detector.register_subscriber(lambda e: print(f"New event: {e}"))
    
    async def data_handler():
        while True:
            for pool_address in config['pools']:
                pool_state = await fetcher.fetch_pool_state(Pubkey.from_string(pool_address))
                ts_manager.update_series('SOL_price', pool_state.last_price)
                
            await asyncio.sleep(1)
    
    await asyncio.gather(
        event_detector.start_detection(),
        data_handler()
    )

if __name__ == "__main__":
    asyncio.run(main())
