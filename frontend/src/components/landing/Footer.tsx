import { TrendingUp } from "lucide-react";

const Footer = () => (
  <footer className="site-footer">
    <div className="footer-inner">
      <div className="nav-logo">
        <div className="nav-logo-icon" style={{ width: 30, height: 30 }}>
          <TrendingUp style={{ width: 16, height: 16, color: "white" }} />
        </div>
        <span className="logo-text" style={{ fontSize: 22 }}>
          Vibe Trade
        </span>
      </div>
      <p className="footer-copy">© 2026 Vibe Trade. All rights reserved.</p>
    </div>
  </footer>
);

export default Footer;
