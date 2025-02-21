class LiquidityAnalyzer:
    def __init__(self, fetcher: SolanaDataFetcher):
        self.fetcher = fetcher
        self.liquidity_cache = {}
        
    async def calculate_slippage_curve(self, pool_address: Pubkey, amounts: List[float]):
        pool_state = await self.fetcher.fetch_pool_state(pool_address)
        return {
            amount: self._simulate_swap(pool_state, amount)
            for amount in amounts
        }

    def _simulate_swap(self, pool_state, amount_in):
        if pool_state is None:
            return 0.0
            
        initial_price = pool_state.quote_liquidity / pool_state.base_liquidity
        new_base = pool_state.base_liquidity + amount_in
        new_quote = (pool_state.base_liquidity * pool_state.quote_liquidity) / new_base
        amount_out = pool_state.quote_liquidity - new_quote
        effective_price = amount_out / amount_in
        
        return {
            'slippage': (effective_price - initial_price) / initial_price * 100,
            'price_impact': (pool_state.quote_liquidity - new_quote) / pool_state.quote_liquidity * 100
        }

    async def monitor_liquidity_changes(self, pool_address: Pubkey):
        prev_state = await self.fetcher.fetch_pool_state(pool_address)
        while True:
            await asyncio.sleep(5)
            current_state = await self.fetcher.fetch_pool_state(pool_address)
            
            liquidity_change = {
                'base_delta': current_state.base_liquidity - prev_state.base_liquidity,
                'quote_delta': current_state.quote_liquidity - prev_state.quote_liquidity
            }
            
            if abs(liquidity_change['base_delta']) > prev_state.base_liquidity * 0.01:
                yield self._analyze_liquidity_event(liquidity_change)
                
            prev_state = current_state

    def _analyze_liquidity_event(self, change):
        return {
            'event_type': 'liquidity_change',
            'magnitude': (abs(change['base_delta']) + abs(change['quote_delta'])) / 2,
            'direction': 'add' if change['base_delta'] > 0 else 'remove'
        }
