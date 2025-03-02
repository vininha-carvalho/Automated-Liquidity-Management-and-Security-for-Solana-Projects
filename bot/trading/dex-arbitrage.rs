// Arbitrage between Raydium and Orca with minimum profit verification
use solana_client::rpc_client::RpcClient;
use solana_sdk::{signature::Keypair, pubkey::Pubkey};

pub fn dex_arbitrage(
    client: &RpcClient,
    signer: &Keypair,
    token_a: Pubkey,
    token_b: Pubkey,
    min_profit: u64, // Minimum 0.5% profit
) -> Result<(), String> {
    // 1. Obtaining prices
    let price_raydium = get_price(client, token_a, token_b, "raydium")?;
    let price_orca = get_price(client, token_a, token_b, "orca")?;

    // 2. Spread check
    let spread = if price_raydium > price_orca {
        price_raydium - price_orca
    } else {
        price_orca - price_raydium
    };

    if spread < min_profit {
        return Err("Spread too small".into());
    }

    // 3. Enforcement of arbitration
    let (buy_dex, sell_dex) = if price_raydium > price_orca {
        ("orca", "raydium")
    } else {
        ("raydium", "orca")
    };

    execute_swap(client, signer, buy_dex, token_a, token_b)?;
    execute_swap(client, signer, sell_dex, token_b, token_a)?;

    // 4. Logging
    solana_logger::info!("Arbitrage executed: profit = {}", spread);
    Ok(())
}

#[test]
fn test_arbitrage_profit() {
    let mock_client = MockRpcClient::new();
    let signer = Keypair::new();
    assert!(dex_arbitrage(&mock_client, &signer, Pubkey::new_unique(), Pubkey::new_unique(), 100).is_ok());
}
