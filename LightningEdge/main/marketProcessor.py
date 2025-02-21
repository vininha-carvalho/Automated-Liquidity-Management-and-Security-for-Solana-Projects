class MarketDataProcessor:
    def __init__(self, fetcher: SolanaDataFetcher):
        self.fetcher = fetcher
        self.pools = {}
        
    async def initialize_pools(self, pool_addresses: List[Pubkey]):
        for addr in pool_addresses:
            pool_state = await self.fetcher.fetch_pool_state(addr)
            if pool_state:
                self.pools[addr] = {
                    'state': pool_state,
                    'metrics': self._calculate_initial_metrics(pool_state)
                }
    
    def _calculate_initial_metrics(self, pool_data):
        return {
            'base_volume': pool_data.base_volume,
            'quote_volume': pool_data.quote_volume,
            'price_impact': self._calculate_price_impact(pool_data),
            'fair_price': self._calculate_fair_price(pool_data)
        }
    
    def _calculate_price_impact(self, pool_data, amount=1000):
        return (amount / pool_data.base_liquidity) * 100
    
    def _calculate_fair_price(self, pool_data):
        return pool_data.quote_liquidity / pool_data.base_liquidity

    async def process_realtime_data(self, pool_address: Pubkey):
        async for update in self.fetcher.fetch_realtime_orderbook(pool_address):
            self._update_pool_state(pool_address, update)
            yield self._generate_trading_signals(pool_address)

    def _update_pool_state(self, pool_address, update):
        current_state = self.pools[pool_address]['state']
        # Обновляем биды и аски
        current_state.bids = update['bids']
        current_state.asks = update['asks']
        current_state.last_price = update['last_price']
        
        self.pools[pool_address]['metrics'] = {
            **self.pools[pool_address]['metrics'],
            'price_impact': self._calculate_price_impact(current_state),
            'volume_5m': self._calculate_rolling_volume(current_state)
        }

    def _generate_trading_signals(self, pool_address):
        metrics = self.pools[pool_address]['metrics']
        signals = {}
        
        if metrics['volume_5m'] > metrics['volume_5m_sma'] * 1.5:
            signals['volume_spike'] = True
            
        return signals
