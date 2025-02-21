    def generate_report(self, output_format='html'):
        report_data = {
            'performance_metrics': self.calculate_performance(),
            'strategy_comparison': self.analyze_strategies(),
            'recent_trades': pd.read_sql('SELECT * FROM trades ORDER BY entry_time DESC LIMIT 10', self.conn)
        }
        
        if output_format == 'html':
            return report_data['performance_metrics'].to_html()
        elif output_format == 'csv':
            return report_data['performance_metrics'].to_csv()
        elif output_format == 'console':
            return report_data['performance_metrics'].to_string()
