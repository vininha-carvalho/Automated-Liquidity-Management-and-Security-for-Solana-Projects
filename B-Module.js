import { SecurityMonitor } from 'liquidity-guardian-suite';

const monitor = new SecurityMonitor({
  threshold: 10000, // $10k threshold for alerts
  notify: ['telegram', 'discord'], // Send alerts to Telegram and Discord
});

monitor.on('suspiciousActivity', (transaction) => {
  console.log('Suspicious transaction detected:', transaction);
});

monitor.start();
