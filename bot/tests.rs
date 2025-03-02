#[cfg(test)]
mod tests {
    use super::*;
    use solana_sdk::signer::keypair::Keypair;

    #[test]
    fn test_ledger_signature() {
        let mut tx = Transaction::new_with_payer(&[], Some(&Keypair::new().pubkey()));
        let path = "44'/501'/0'";
        assert!(sign_with_ledger(&mut tx, path).is_ok());
        assert!(tx.verify().is_ok());
    }

    #[test]
    fn test_honeypot_detection() {
        let scam_token = "HvRN...".to_string();
        assert!(is_honeypot(scam_token));
    }
}
