const MarketChart = () => {
  return (
    <div className="bg-card text-card-foreground rounded-xl border border-border overflow-hidden shadow-sm">
      <div className="p-6 border-b border-border/50 bg-muted/20">
        <h2 className="text-xl font-semibold">Live Market Data (BTC/USDT)</h2>
      </div>
      <div className="tradingview-widget-container" style={{ height: 450, width: "100%" }}>
        <iframe
          src="https://s.tradingview.com/widgetembed/?hideideas=1&overrides=%7B%7D&enabled_features=%5B%5D&disabled_features=%5B%5D#%7B%22symbol%22%3A%22BINANCE%3ABTCUSDT%22%2C%22frameElementId%22%3A%22tradingview_01697%22%2C%22interval%22%3A%2230%22%2C%22hide_top_toolbar%22%3A%220%22%2C%22hide_side_toolbar%22%3A%220%22%2C%22save_image%22%3A%221%22%2C%22studies%22%3A%22%5B%5D%22%2C%22theme%22%3A%22light%22%2C%22style%22%3A%221%22%2C%22timezone%22%3A%22Etc%2FUTC%22%2C%22studies_overrides%22%3A%22%7B%7D%22%2C%22utm_source%22%3A%22gptchart.ai%22%2C%22utm_medium%22%3A%22widget%22%2C%22utm_campaign%22%3A%22chart%22%2C%22utm_term%22%3A%22BINANCE%3ABTCUSDT%22%2C%22page-uri%22%3A%22gptchart.ai%2F%22%7D"
          style={{ width: "100%", height: "100%", border: "none" }}
          allowFullScreen
        />
      </div>
    </div>
  );
};

export default MarketChart;
