const logos = ["TradingView", "Benzinga", "Bloomberg", "MarketWatch", "Yahoo Finance"];

const LogoTicker = () => (
  <section className="ticker-section">
    <p className="ticker-label">Featured in</p>
    <div style={{ position: "relative" }}>
      <div className="ticker-track animate-scroll">
        {[...logos, ...logos, ...logos].map((name, i) => (
          <span key={i} className="ticker-item">{name}</span>
        ))}
      </div>
    </div>
  </section>
);

export default LogoTicker;
