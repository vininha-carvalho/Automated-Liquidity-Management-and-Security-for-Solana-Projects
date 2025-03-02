#[program]
pub mod alpha_stoploss {
    use super::*;
    
    // Anchor program for auto-stop-loss
    pub fn set_stoploss(ctx: Context<SetStopLoss>, price: u64) -> Result<()> {
        let user = &mut ctx.accounts.user;
        user.stoploss_price = price;
        
        // Signature verification via PDA
        let signer_seeds = &[b"stoploss", user.key.as_ref()];
        let pda = Pubkey::find_program_address(signer_seeds, ctx.program_id).0;
        require!(pda == ctx.accounts.pda.key, ErrorCode::InvalidPda);
        
        Ok(())
    }

    #[derive(Accounts)]
    pub struct SetStopLoss<'info> {
        #[account(mut, has_one = owner)]
        pub user: Account<'info, UserState>,
        pub owner: Signer<'info>,
        /// CHECK: PDA для верификации
        pub pda: AccountInfo<'info>,
    }
}
