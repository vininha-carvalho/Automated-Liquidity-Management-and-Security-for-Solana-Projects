import aiohttp
import asyncio
import pandas as pd
from typing import Dict, List, Optional
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
import time

class SolanaDataFetcher:
    def __init__(self, rpc_url: str, helius_api_key: str):
        self.rpc_client = AsyncClient(rpc_url)
        self.helius_headers = {"Content-Type": "application/json", "X-API-Key": helius_api_key}
        self.cache = {}
        self.session = aiohttp.ClientSession()
        
    async def fetch_pool_state(self, pool_address: Pubkey):
        cache_key = f"pool_{pool_address}"
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        try:
            pool_data = await self.rpc_client.get_account_info(pool_address)
            parsed_data = LiquidityPool.parse(pool_data.value.data)
            self.cache[cache_key] = parsed_data
            return parsed_data
        except Exception as e:
            print(f"Error fetching pool {pool_address}: {str(e)}")
            return None

    async def fetch_historical_prices(self, token_mint: Pubkey, timespan: str):
        resolution_map = {
            '1s': 1, '5s': 5, '15s': 15, '30s': 30,
            '1m': 60, '2m': 120, '3m': 180, '5m': 300
        }
        async with self.session.get(
            f"https://api.helius.xyz/v0/token-price/history?mint={token_mint}&resolution={resolution_map[timespan]}"
        ) as resp:
            return await resp.json()

    async def fetch_realtime_orderbook(self, pool_address: Pubkey):
        async with self.session.ws_connect(
            f"wss://api.helius.xyz/v0/ws/orderbook?pool={pool_address}"
        ) as ws:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    yield msg.json()

    async def fetch_insider_activity(self, token_mint: Pubkey):
        query = {
            "query": {
                "token_mint": str(token_mint),
                "transaction_types": ["SWAP"],
                "account_changes": {"direction": "out", "amount": {">=": 1000}}
            }
        }
        async with self.session.post(
            "https://api.helius.xyz/v0/transactions/search",
            json=query,
            headers=self.helius_headers
        ) as resp:
            return await resp.json()

    async def fetch_mev_analysis(self, pool_address: Pubkey):
        async with self.session.get(
            f"https://api.helius.xyz/v0/mev/pool/{pool_address}",
            headers=self.helius_headers
        ) as resp:
            return await resp.json()

    async def close(self):
        await self.session.close()
        await self.rpc_client.close()
