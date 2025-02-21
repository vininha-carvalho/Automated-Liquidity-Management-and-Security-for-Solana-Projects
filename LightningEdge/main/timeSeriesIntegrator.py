class TimeSeriesManager:
    def __init__(self):
        self.series = {}
        
    def create_series(self, name: str, window_size: int):
        self.series[name] = {
            'data': [],
            'window': window_size,
            'aggregations': {}
        }
    
    def update_series(self, name: str, value: float):
        if name not in self.series:
            raise KeyError(f"Series {name} not initialized")
            
        series = self.series[name]
        series['data'].append({
            'timestamp': time.time(),
            'value': value
        })
        
        if len(series['data']) > series['window']:
            series['data'].pop(0)
            
        values = [item['value'] for item in series['data']]
        series['aggregations'] = {
            'mean': sum(values)/len(values),
            'max': max(values),
            'min': min(values),
            'std': np.std(values) if len(values) > 1 else 0
        }
    
    def get_aggregations(self, name: str):
        return self.series.get(name, {}).get('aggregations', {})
