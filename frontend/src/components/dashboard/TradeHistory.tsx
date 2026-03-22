const trades = [
  { id: 1, type: "BUY", price: 62000, amount: 0.1, time: "2024-03-21 10:30" },
  { id: 2, type: "SELL", price: 63500, amount: 0.1, time: "2024-03-21 16:45" },
  { id: 3, type: "BUY", price: 61800, amount: 0.05, time: "2024-03-20 08:15" },
];

const TradeHistory = () => {
  return (
    <div className="bg-card text-card-foreground rounded-xl border border-border p-6 shadow-sm">
      <h2 className="text-xl font-semibold mb-4">Recent Trades (Simulated)</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left">
          <thead className="text-xs text-muted-foreground uppercase bg-muted/50 rounded-md">
            <tr>
              <th className="px-4 py-3 rounded-tl-md">Type</th>
              <th className="px-4 py-3">Price</th>
              <th className="px-4 py-3">Amount</th>
              <th className="px-4 py-3 rounded-tr-md">Time</th>
            </tr>
          </thead>
          <tbody>
            {trades.map((trade) => (
              <tr key={trade.id} className="border-b border-border/50 last:border-0 hover:bg-muted/20 transition-colors">
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${trade.type === 'BUY' ? 'bg-green-500/20 text-green-500' : 'bg-red-500/20 text-red-500'}`}>
                    {trade.type}
                  </span>
                </td>
                <td className="px-4 py-3 font-medium">${trade.price.toLocaleString()}</td>
                <td className="px-4 py-3">{trade.amount} BTC</td>
                <td className="px-4 py-3 text-muted-foreground">{trade.time}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default TradeHistory;
