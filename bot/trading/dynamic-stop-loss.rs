#[program]
pub mod dynamic_stoploss {
    use super::*;
    
    // Update stop price based on volatility
    pub fn update_stoploss(ctx: Context<UpdateStopLoss>, volatility: f64) -> Result<()> {
        let state = &mut ctx.accounts.state;
        
        // Formula: stoploss = current price - (3 * ATR)
        let new_stoploss = state.current_price - (3.0 * volatility);
        state.stoploss = new_stoploss;

        // Logging in PDA
        emit!(StopLossUpdated {
            user: ctx.accounts.user.key(),
            new_stoploss
        });
        
        Ok(())
    }

    #[derive(Accounts)]
    pub struct UpdateStopLoss<'info> {
        #[account(mut, seeds = [b"stoploss", user.key.as_ref()], bump)]
        pub state: Account<'info, StopLossState>,
        #[account(signer)]
        pub user: AccountInfo<'info>,
        pub system_program: Program<'info, System>,
    }
}
