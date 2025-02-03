import asyncio
from config.config_manager import ConfigManager
from ai_module.predictor import LiquidityPredictor
from trading_engine import OrderEngine

class CryptoQuantumPro:
    def __init__(self):
        self.config = ConfigManager()
        self.predictor = LiquidityPredictor()
        self.order_engine = OrderEngine()

    async def start(self):
        """Application kernel initialization"""
        print("""
        ░█████╗░██████╗░██╗░░░██╗██████╗░████████╗██╗░░░██╗
        ██╔══██╗██╔══██╗╚██╗░██╔╝██╔══██╗╚══██╔══╝╚██╗░██╔╝
        ██║░░╚═╝██████╔╝░╚████╔╝░██████╔╝░░░██║░░░░╚████╔╝░
        ██║░░██╗██╔═══╝░░░╚██╔╝░░██╔═══╝░░░░██║░░░░░╚██╔╝░░
        ╚█████╔╝██║░░░░░░░░██║░░░██║░░░░░░░░██║░░░░░░██║░░░
        ░╚════╝░╚═╝░░░░░░░░╚═╝░░░╚═╝░░░░░░░░╚═╝░░░░░░╚═╝░░░
        """)
        
        # Module initialization
        await self.predictor.load_model()
        await self.order_engine.connect_exchanges(
            self.config.get('exchanges')
        )
        
        # Starting background tasks
        asyncio.create_task(self._monitor_market())

    async def _monitor_market(self):
        """Фоновая задача для анализа рынка"""
        while True:
            liquidity_score = await self.predictor.get_score()
            if liquidity_score > 0.8:
                self.order_engine.adjust_aggressiveness('high')
            await asyncio.sleep(60)

def cli():
    """Command line interface"""
    import argparse
    parser = argparse.ArgumentParser(prog='cqpro')
    parser.add_argument('command', choices=['start', 'config', 'version'])
    
    args = parser.parse_args()
    app = CryptoQuantumPro()
    
    match args.command:
        case 'start':
            asyncio.run(app.start())
        case 'version':
            print("CryptoQuantum Pro v0.1 (Quantum Engine)")
        case _:
            parser.print_help()

if __name__ == '__main__':
    cli()
