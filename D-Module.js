import { CrossChainManager } from 'liquidity-guardian-suite';

const crossChain = new CrossChainManager({
  chains: ['Solana', 'Ethereum'],
  bridge: 'Wormhole',
});

crossChain.on('arbitrage', (opportunity) => {
  console.log('Arbitrage opportunity:', opportunity);
});

crossChain.start();
