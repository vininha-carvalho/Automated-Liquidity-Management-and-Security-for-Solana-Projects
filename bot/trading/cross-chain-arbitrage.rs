// Arbitration between Solana and Ethereum via Wormhole
pub async fn cross_chain_arbitrage(
    sol_price: f64,
    eth_price: f64,
    amount: u64,
) -> Result<(), Box<dyn Error>> {
    // 1. Spread check (>2%)
    let spread = (sol_price - eth_price).abs() / eth_price;
    if spread < 0.02 {
        return Err("Spread too small".into());
    }

    // 2. Translation via Wormhole
    let wormhole_msg = if sol_price > eth_price {
        // Купить на Ethereum, продать на Solana
        wormhole::lock_eth(amount).await?;
        wormhole::mint_sol(amount).await?;
    } else {
        // Buy on Solana, sell on Ethereum
        wormhole::lock_sol(amount).await?;
        wormhole::mint_eth(amount).await?;
    };

    // 3. Transaction confirmation
    confirm_wormhole_transaction(wormhole_msg).await?;
    Ok(())
}
