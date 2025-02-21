class MarketEventDetector:
    def __init__(self, processor: MarketDataProcessor):
        self.processor = processor
        self.subscribers = []
        
    def register_subscriber(self, callback):
        self.subscribers.append(callback)
    
    async def start_detection(self):
        for pool_address in self.processor.pools:
            asyncio.create_task(self._monitor_pool_events(pool_address))
    
    async def _monitor_pool_events(self, pool_address):
        async for signal in self.processor.process_realtime_data(pool_address):
            for event in self._detect_events(signal):
                for callback in self.subscribers:
                    await callback(event)
    
    def _detect_events(self, signals):
        events = []
        
        if signals.get('volume_spike'):
            events.append({'type': 'volume_spike', 'data': signals})
            
        return events
