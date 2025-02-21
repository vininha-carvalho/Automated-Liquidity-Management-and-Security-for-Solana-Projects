class AnalysisConfig:
    def __init__(self):
        self.metrics_to_show = ['win_rate', 'sortino', 'max_drawdown']
        self.alert_thresholds = {
            'max_drawdown': -15.0,
            'daily_loss_limit': -5.0
        }
        self.report_preferences = {
            'format': 'html',
            'schedule': 'daily'
        }
