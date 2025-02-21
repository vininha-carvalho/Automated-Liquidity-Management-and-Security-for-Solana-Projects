import asyncio
import numpy as np
import pandas as pd
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.responses import HTMLResponse
from datetime import datetime
from typing import List, Dict, Optional
import logging
from binance import AsyncClient as BinanceAsyncClient, BinanceSocketManager
import ccxt.async_support as ccxt  # Async CCXT for CEX trading
import plotly.express as px

from solana.rpc.async_api import AsyncClient as SolanaAsyncClient
from solana.transaction import Transaction
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solana.rpc.types import TxOpts
from raydium.sdk import create_swap_instruction, LiquidityPool
from spl.token.instructions import get_associated_token_address
from spl.token.constants import TOKEN_PROGRAM_ID

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("trading_system.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql+asyncpg://user:password@localhost/trading"
engine = create_async_engine(DATABASE_URL)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

class Trade(Base):
    __tablename__ = 'trades'
    id = sa.Column(sa.Integer, primary_key=True)
    token_address = sa.Column(sa.String(42), nullable=False)
    entry_time = sa.Column(sa.DateTime, nullable=False)
    exit_time = sa.Column(sa.DateTime)
    entry_price = sa.Column(sa.Float, nullable=False)
    exit_price = sa.Column(sa.Float)
    amount_usd = sa.Column(sa.Float, nullable=False)
    status = sa.Column(sa.String(10), nullable=False)
    slippage = sa.Column(sa.Float)
    latency = sa.Column(sa.Float)

class PriceHistory(Base):
    __tablename__ = 'price_history'
    id = sa.Column(sa.Integer, primary_key=True)
    token_address = sa.Column(sa.String(42), nullable=False)
    timestamp = sa.Column(sa.DateTime, nullable=False)
    price = sa.Column(sa.Float, nullable=False)

class SolanaRaydiumTrader:
    def __init__(self, private_key: str, rpc_url: str = "https://api.mainnet-beta.solana.com"):
        self.client = SolanaAsyncClient(rpc_url)
        try:
            self.wallet = Keypair.from_base58_string(private_key)
        except Exception as e:
            logger.error("Failed to load private key: %s", e)
            raise
        self.pools: Dict[str, LiquidityPool] = {}

    async def load_pool(self, pool_address: str) -> LiquidityPool:
        if pool_address not in self.pools:
            try:
                pool = await LiquidityPool.load(Pubkey.from_string(pool_address))
                self.pools[pool_address] = pool
                logger.info("Pool %s loaded successfully.", pool_address)
            except Exception as e:
                logger.error("Error loading pool %s: %s", pool_address, e)
                raise
        return self.pools[pool_address]

    async def get_token_account(self, mint: Pubkey) -> Pubkey:
        return get_associated_token_address(self.wallet.pubkey(), mint)

    async def calculate_slippage(self, pool: LiquidityPool, amount: int) -> float:
        try:
            price_before = pool.get_price()
            simulated_pool = pool.simulate_swap(amount)
            price_after = simulated_pool.get_price()
            slippage = abs((price_after - price_before) / price_before * 100)
            logger.info("Calculated slippage: %.2f%%", slippage)
            return slippage
        except Exception as e:
            logger.error("Error calculating slippage: %s", e)
            raise

    async def execute_swap(
        self,
        pool_address: str,
        amount_in: int,
        min_amount_out: int,
        slippage_tolerance: float = 0.5,
        retries: int = 3
    ) -> str:
        for attempt in range(retries):
            try:
                pool = await self.load_pool(pool_address)
                current_slippage = await self.calculate_slippage(pool, amount_in)
                if current_slippage > slippage_tolerance:
                    raise Exception(f"Slippage {current_slippage:.2f}% exceeds tolerance")
                
                input_token_account = await self.get_token_account(pool.token_a_mint)
                output_token_account = await self.get_token_account(pool.token_b_mint)

                swap_ix = create_swap_instruction(
                    pool=pool,
                    amount_in=amount_in,
                    min_amount_out=min_amount_out,
                    input_token_account=input_token_account,
                    output_token_account=output_token_account,
                    user_wallet=self.wallet.pubkey()
                )

                txn = Transaction().add(swap_ix)
                # Optionally add compute unit price for prioritization
                txn.add_compute_unit_price(self._calculate_dynamic_priority_fee())

                txn.sign(self.wallet)
                txid = await self.client.send_transaction(txn, self.wallet, opts=TxOpts(skip_preflight=True))
                await self.client.confirm_transaction(txid)
                logger.info("Swap executed successfully. TxID: %s", txid)
                return txid

            except Exception as e:
                logger.error("Swap attempt %d failed: %s", attempt + 1, e)
                if attempt == retries - 1:
                    raise
                await asyncio.sleep(1.5 ** attempt)

    def _calculate_dynamic_priority_fee(self) -> int:
        return 100_000  # microLamports; placeholder

    async def close(self):
        await self.client.close()


class CexTrader:
    def __init__(self, exchange: str, api_key: str, secret: str):
        exchange_lower = exchange.lower()
        if exchange_lower == "binance":
            self.exchange = ccxt.binance({
                'apiKey': api_key,
                'secret': secret,
                'enableRateLimit': True,
            })
        elif exchange_lower == "bybit":
            self.exchange = ccxt.bybit({
                'apiKey': api_key,
                'secret': secret,
                'enableRateLimit': True,
            })
        else:
            raise ValueError("Exchange not supported")

    async def create_order(self, symbol: str, side: str, order_type: str, amount: float, price: Optional[float] = None):
        try:
            if order_type.lower() == "market":
                order = await self.exchange.create_market_order(symbol, side, amount)
            elif order_type.lower() == "limit":
                if price is None:
                    raise ValueError("Price is required for limit orders")
                order = await self.exchange.create_limit_order(symbol, side, amount, price)
            else:
                raise ValueError("Unsupported order type")
            return order
        except Exception as e:
            logger.error("Error creating order on %s: %s", self.exchange.id, e)
            raise

    async def close(self):
        await self.exchange.close()

class AdvancedPerformanceAnalyzer:
    def __init__(self):
        self.engine = engine
        self.binance_client = None

    async def connect_binance(self):
        self.binance_client = await BinanceAsyncClient.create()
        return BinanceSocketManager(self.binance_client)

    async def calculate_pnl(self, include_open: bool = True) -> float:
        async with async_session() as session:
            query = sa.select(Trade)
            if not include_open:
                query = query.where(Trade.status == 'closed')
            result = await session.execute(query)
            trades = result.scalars().all()
            realized = sum(
                (t.exit_price - t.entry_price) / t.entry_price * t.amount_usd
                for t in trades if t.status == 'closed'
            )
            current_prices = await self._get_current_prices()
            unrealized = sum(
                (current_prices.get(t.token_address, t.entry_price) - t.entry_price) / t.entry_price * t.amount_usd
                for t in trades if t.status == 'open'
            )
            return realized + unrealized

    async def _get_current_prices(self) -> Dict[str, float]:
        return {"BTCUSDT": 30000.0, "SOLUSDT": 100.0}

    async def stream_real_time_data(self, websocket: WebSocket):
        bm = await self.connect_binance()
        ts = bm.trade_socket('BTCUSDT')
        async with ts as tscm:
            while True:
                res = await tscm.recv()
                await websocket.send_json({
                    'price': res['p'],
                    'quantity': res['q'],
                    'time': datetime.fromtimestamp(res['T'] / 1000).isoformat()
                })

    async def generate_dashboard(self):
        async with async_session() as session:
            result = await session.execute(sa.select(Trade))
            trades = result.scalars().all()
            df = pd.DataFrame([t.__dict__ for t in trades])
            fig = px.line(df, x='entry_time', y='amount_usd', color='token_address', title="Equity Curve")
            return fig.to_html()

app = FastAPI(
    title="Trading Performance Analytics",
    description="Real-time trading performance monitoring system",
    version="1.0.0"
)

@app.get("/metrics", response_model=Dict)
async def get_performance_metrics():
    analyzer = AdvancedPerformanceAnalyzer()
    pnl = await analyzer.calculate_pnl()
    return {"pnl": pnl}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    analyzer = AdvancedPerformanceAnalyzer()
    await analyzer.stream_real_time_data(websocket)

@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    analyzer = AdvancedPerformanceAnalyzer()
    return await analyzer.generate_dashboard()

@app.post("/trade/solana", response_model=Dict)
async def trade_solana(pool_address: str, amount_in: int, min_amount_out: int, private_key: str):
    trader = SolanaRaydiumTrader(private_key)
    try:
        txid = await trader.execute_swap(pool_address, amount_in, min_amount_out)
        return {"txid": txid}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        await trader.close()

@app.post("/trade/cex", response_model=Dict)
async def trade_cex(
    exchange: str,
    symbol: str,
    side: str,
    order_type: str,
    amount: float,
    price: Optional[float] = None,
    api_key: str = "",
    secret: str = ""
):
    trader = CexTrader(exchange, api_key, secret)
    try:
        order = await trader.create_order(symbol, side, order_type, amount, price)
        return {"order": order}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        await trader.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
