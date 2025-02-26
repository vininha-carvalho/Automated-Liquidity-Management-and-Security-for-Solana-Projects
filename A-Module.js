import { LiquidityManager } from 'liquidity-guardian-suite';

const manager = new LiquidityManager({
  pools: ['Raydium', 'Orca'],
  rebalanceThreshold: 0.05, // 5% price difference
});

manager.on('rebalance', (data) => {
  console.log('Rebalanced pools:', data);
});

manager.start();
