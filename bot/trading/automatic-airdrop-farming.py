# TVL distribution between Kamino, MarginFi and Parcl
def optimize_airdrop_tvl(wallet_balance: int):
    protocols = [
        {"name": "Kamino", "apr": 0.12, "min_tvl": 1000},
        {"name": "MarginFi", "apr": 0.15, "min_tvl": 2000},
        {"name": "Parcl", "apr": 0.09, "min_tvl": 500}
    ]
    
    allocated = 0
    for protocol in sorted(protocols, key=lambda x: -x["apr"]):
        if wallet_balance - allocated < protocol["min_tvl"]:
            continue
        amount = min(protocol["min_tvl"], wallet_balance - allocated)
        deposit(protocol["name"], amount)
        allocated += amount
        if allocated >= wallet_balance:
            break
