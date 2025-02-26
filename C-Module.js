import { AnalyticsDashboard } from 'liquidity-guardian-suite';

const dashboard = new AnalyticsDashboard({
  metrics: ['price', 'volume', 'holderDistribution'],
});

dashboard.on('update', (data) => {
  console.log('Updated analytics:', data);
});

dashboard.start();
