    def live_performance_tape(self, update_interval=60):
        import time
        from IPython.display import clear_output
        
        while True:
            clear_output(wait=True)
            metrics = self.calculate_performance()
            print("=== Live Performance Metrics ===")
            print(metrics.to_string(index=False))
            time.sleep(update_interval)
