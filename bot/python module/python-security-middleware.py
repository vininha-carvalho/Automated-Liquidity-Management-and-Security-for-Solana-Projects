# Verification of signed Phantom transactions
from solders.signature import Signature
from solana.rpc.async_api import AsyncClient

async def verify_phantom_tx(tx_signature: str, public_key: str) -> bool:
    client = AsyncClient("https://api.mainnet-beta.solana.com")
    sig = Signature.from_string(tx_signature)
    
    # 1. Receiving a transaction
    tx_info = await client.get_transaction(sig)
    if not tx_info:
        return False
        
    # 2. Signature verification
    tx = tx_info.transaction
    if public_key not in [str(pubkey) for pubkey in tx.message.account_keys]:
        return False
    
    # 3. Checking the RPC node
    if tx_info.meta.pre_balances[0] - tx_info.meta.post_balances[0] > 0.1 * 1e9:  # Max 0.1 SOL fee
        return False
        
    return True
