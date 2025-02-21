import React, { useState, useEffect, useRef } from 'react';
import './App.css';

const tokenDefaults = Array(5).fill(''); // for 5 token input fields

// SettingsPanel component: inputs for tokens, interval and allocation percentage.
const SettingsPanel = ({ tokens, setTokens, interval, setIntervalVal, allocation, setAllocation }) => {
  const intervals = ["1s", "5s", "15s", "30s", "1m", "2m", "3m", "5m"];

  const handleTokenChange = (index, value) => {
    const newTokens = [...tokens];
    newTokens[index] = value;
    setTokens(newTokens);
  };

  return (
    <div className="settings-panel">
      <h2>Trading Settings</h2>
      <div className="input-group">
        <label>Token Contract Addresses:</label>
        {tokens.map((token, index) => (
          <input
            key={index}
            type="text"
            placeholder={`Token ${index + 1}`}
            value={token}
            onChange={(e) => handleTokenChange(index, e.target.value)}
          />
        ))}
      </div>
      <div className="input-group">
        <label>Data Interval:</label>
        <select value={interval} onChange={(e) => setIntervalVal(e.target.value)}>
          {intervals.map((opt, idx) => (
            <option key={idx} value={opt}>{opt}</option>
          ))}
        </select>
      </div>
      <div className="input-group">
        <label>Allocation (% of balance):</label>
        <input
          type="number"
          value={allocation}
          onChange={(e) => setAllocation(e.target.value)}
        />
      </div>
    </div>
  );
};

// MetricsPanel component: displays live trading metrics.
const MetricsPanel = ({ metrics }) => {
  return (
    <div className="metrics-panel">
      <h2>Live Metrics</h2>
      <pre>{JSON.stringify(metrics, null, 2)}</pre>
    </div>
  );
};

// OrderHistory component: displays a table of executed orders.
const OrderHistory = ({ orders }) => {
  return (
    <div className="order-history">
      <h2>Order History</h2>
      <table>
        <thead>
          <tr>
            <th>Time</th>
            <th>Action</th>
            <th>Token</th>
            <th>Quantity</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {orders.map((order, idx) => (
            <tr key={idx}>
              <td>{order.time}</td>
              <td>{order.action}</td>
              <td>{order.token}</td>
              <td>{order.quantity}</td>
              <td>{order.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

// Main TradingTerminal component that ties everything together.
const TradingTerminal = () => {
  const [tokens, setTokens] = useState(tokenDefaults);
  const [intervalVal, setIntervalVal] = useState("1s");
  const [allocation, setAllocation] = useState(10);
  const [metrics, setMetrics] = useState({});
  const [orders, setOrders] = useState([]);
  const [trading, setTrading] = useState(false);
  const tradingIntervalRef = useRef(null);

  // Simulated trading loop that updates metrics and adds order entries.
  const startTrading = () => {
    setTrading(true);
    tradingIntervalRef.current = setInterval(() => {
      const timestamp = new Date().toLocaleTimeString();
      // Simulate updating metrics
      setMetrics(prev => ({
        ...prev,
        pnl: (prev.pnl || 0) + (Math.random() - 0.5) * 10,
        trades: (prev.trades || 0) + 1,
        lastUpdate: timestamp
      }));
      // Simulate a new order entry
      setOrders(prev => ([
        {
          time: timestamp,
          action: Math.random() > 0.5 ? "Buy" : "Sell",
          token: tokens.find(t => t !== "") || "N/A",
          quantity: (allocation / 100 * 1000).toFixed(4),
          status: "Executed"
        },
        ...prev
      ]));
    }, 1000); // Adjust interval as needed (simulate every second)
  };

  const stopTrading = () => {
    setTrading(false);
    if (tradingIntervalRef.current) {
      clearInterval(tradingIntervalRef.current);
    }
  };

  return (
    <div className="terminal-container">
      <h1>Crypto Trading Terminal MVP</h1>
      <SettingsPanel
        tokens={tokens}
        setTokens={setTokens}
        interval={intervalVal}
        setIntervalVal={setIntervalVal}
        allocation={allocation}
        setAllocation={setAllocation}
      />
      <div className="button-group">
        <button onClick={startTrading} disabled={trading}>Start Trading</button>
        <button onClick={stopTrading} disabled={!trading}>Kill Switch</button>
      </div>
      <MetricsPanel metrics={metrics} />
      <OrderHistory orders={orders} />
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <TradingTerminal />
    </div>
  );
}

export default App;
