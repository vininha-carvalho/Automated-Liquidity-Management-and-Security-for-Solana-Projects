//! Secure Execution Engine for Solana AlphaBot

use solana_client::rpc_client::RpcClient;
use solana_sdk::signer::keypair::Keypair;
use crate::{config::Config, risk_management::validate_transaction};

mod dex;
mod arbitrage;
mod auth;
mod error;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // 1. Load Encrypted Config
    let config = Config::from_file("config.yaml", env!("DECRYPTION_KEY"))?;
    
    // 2. Hardware Wallet Init
    let ledger = auth::LedgerSigner::new(&config.wallets.derivation_path)
        .await
        .map_err(|e| format!("Ledger Error: {}", e))?;

    // 3. RPC Clients
    let rpc = RpcClient::new_with_commitment(
        config.network.rpc.primary.clone(),
        config.network.commitment
    );

    // 4. Risk Engine
    let portfolio = Portfolio::load(&ledger, &rpc).await?;
    let risk_engine = RiskEngine::new(config.trading.risk_management, portfolio);

    // 5. Main Event Loop
    let (tx, mut rx) = tokio::sync::mpsc::channel(100);
    
    // Price Feeds
    tokio::spawn(feeds::start_price_stream(tx.clone()));
    
    // Arbitrage Engine
    tokio::spawn(arbitrage::start_engine(
        rpc.clone(),
        ledger.clone(),
        risk_engine.clone()
    ));

    // Process Events
    while let Some(event) = rx.recv().await {
        if !risk_engine.validate(&event).await? {
            log::warn!("Risk check failed for {:?}", event);
            continue;
        }
        
        let tx_builder = dex::TransactionBuilder::new(event);
        let unsigned_tx = tx_builder.build(&rpc).await?;
        
        // Ledger Signature
        let signed_tx = ledger.sign_transaction(unsigned_tx).await?;
        
        // Final Check
        if validate_transaction(&signed_tx, &risk_engine).is_ok() {
            rpc.send_and_confirm_transaction(&signed_tx).await?;
            log::info!("Executed: {}", signed_tx.signatures[0]);
        }
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use solana_sdk::signature::Signer;

    #[tokio::test]
    async fn test_ledger_init() {
        let cfg = Config::default();
        let ledger = auth::LedgerSigner::new(&cfg.wallets.derivation_path)
            .await
            .unwrap();
        assert!(ledger.pubkey().is_on_curve());
    }
}
