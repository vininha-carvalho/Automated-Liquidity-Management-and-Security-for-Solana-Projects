import matplotlib.pyplot as plt
import seaborn as sns

class PerformanceVisualizer:
    @staticmethod
    def plot_equity_curve(analyzer):
        portfolio = analyzer._get_portfolio_timeseries()
        plt.figure(figsize=(12,6))
        plt.plot(portfolio)
        plt.title("Equity Curve")
        plt.xlabel("Date")
        plt.ylabel("Portfolio Value ($)")
        plt.show()
        
    @staticmethod
    def plot_strategy_heatmap(analyzer):

        df = analyzer.historical_analysis()['token_analysis']
        plt.figure(figsize=(15,8))
        sns.heatmap(df[['return_mean', 'duration_days_mean']], annot=True)
        plt.title("Token Performance Heatmap")
        plt.show()

    @staticmethod
    def export_to_excel(analyzer, filename):
        with pd.ExcelWriter(filename) as writer:
            pd.DataFrame([analyzer.generate_performance_report()]).to_excel(
                writer, sheet_name='Summary')
            
            pd.read_sql('SELECT * FROM trades', analyzer.trades_conn).to_excel(
                writer, sheet_name='Trades')
            
            analyzer.historical_analysis()['token_analysis'].to_excel(
                writer, sheet_name='Token Stats')
