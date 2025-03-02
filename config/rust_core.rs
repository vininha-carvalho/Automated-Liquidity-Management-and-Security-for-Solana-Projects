// Trusted Swap Module (Rust Core)
// Goal: Secure swap via Raydium with liquidity and slippage checks

use solana_client::rpc_client::RpcClient;
use solana_sdk::{signature::Keypair, transaction::Transaction};
use anchor_lang::prelude::*;
use spl_associated_token_account::get_associated_token_address;

#[derive(Debug)]
pub enum SwapError {
    InvalidLiquidity,
    SlippageExceeded,
    InvalidSigner,
}

// The main function of the swap
pub fn safe_raydium_swap(
    rpc_client: &RpcClient,
    signer: &Keypair,
    source_token: Pubkey,
    target_token: Pubkey,
    amount_in: u64,
    max_slippage: f64,
    allowed_pubkeys: Vec<Pubkey>,
) -> Result<(), SwapError> {
    // 1. Signature validation
    is_authorized(signer, &allowed_pubkeys)?;

    // 2. Checking the liquidity of the pool
    let pool_state = get_raydium_pool_state(rpc_client, target_token)?;
    if pool_state.liquidity < amount_in * 10 {
        return Err(SwapError::InvalidLiquidity);
    }

    // 3. Calculation of minimum amount_out
    let expected_out = calculate_swap_output(amount_in, pool_state);
    let min_out = (expected_out as f64 * (1.0 - max_slippage)) as u64;

    // 4. Creating an instruction
    let swap_ix = raydex::instruction::swap(
        &spl_token::id(),
        source_token,
        target_token,
        amount_in,
        min_out,
    )?;

    // 5. Signing and sending
    let tx = Transaction::new_signed_with_payer(
        &[swap_ix],
        Some(&signer.pubkey()),
        &[signer],
        rpc_client.get_latest_blockhash()?,
    );

    // 6. Logging
    solana_logger::setup_with_default("info");
    info!("Swap executed: {} -> {}", amount_in, min_out);

    rpc_client.send_and_confirm_transaction(&tx)?;
    Ok(())
}

// Tests for critical components
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_slippage_protection() {
        let result = calculate_min_out(100, 0.1);
        assert_eq!(result, 90);
    }

    #[test]
    fn test_unauthorized_signer() {
        let signer = Keypair::new();
        let allowed = vec![Pubkey::new_unique()];
        assert!(is_authorized(&signer, &allowed).is_err());
    }
}
