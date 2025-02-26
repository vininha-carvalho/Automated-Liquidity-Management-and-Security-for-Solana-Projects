import { WhiteLabel } from 'liquidity-guardian-suite';

const whiteLabel = new WhiteLabel({
  brand: {
    logo: 'https://yourbrand.com/logo.png',
    colors: { primary: '#FF0000', secondary: '#00FF00' },
  },
});

whiteLabel.applyBranding();
