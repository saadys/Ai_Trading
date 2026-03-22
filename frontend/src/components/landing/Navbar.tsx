import { useState } from "react";
import { Link } from "react-router-dom";
import { Menu, X, TrendingUp } from "lucide-react";
import MarketTicker from "./MarketTicker";

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="fixed top-0 left-0 right-0 z-50 bg-background/95 backdrop-blur-md shadow-sm border-b border-border">
      {/* Navbar Principale */}
      <nav className="h-[72px] flex items-center justify-between max-w-[1400px] mx-auto px-6 w-full">
        <div className="nav-logo" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <img src="/logo.png" alt="Vibe Trade Logo" className="w-[42px] h-[42px] object-contain rounded-xl shadow-sm" />
          <span className="logo-text" style={{ fontSize: 32, fontWeight: 600, color: '#0b0f2b', letterSpacing: '-1px' }}>
            Vibe Trade
          </span>
        </div>

        <ul className="nav-links" style={{ display: 'flex', gap: 32, listStyle: 'none' }}>
          <li><a href="#features" style={{ fontSize: 14, fontWeight: 500, color: 'hsl(215, 12%, 52%)', textDecoration: 'none' }}>Features</a></li>
          <li><a href="#pricing" style={{ fontSize: 14, fontWeight: 500, color: 'hsl(215, 12%, 52%)', textDecoration: 'none' }}>Pricing</a></li>
          <li><a href="#faq" style={{ fontSize: 14, fontWeight: 500, color: 'hsl(215, 12%, 52%)', textDecoration: 'none' }}>FAQ</a></li>
          <li><a href="#testimonials" style={{ fontSize: 14, fontWeight: 500, color: 'hsl(215, 12%, 52%)', textDecoration: 'none' }}>Reviews</a></li>
        </ul>

        <div className="nav-actions" style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
          <button className="btn-outline-custom" style={{ padding: "8px 18px", fontSize: 13 }}>Sign In</button>
          <Link to="/dashboard" className="btn-primary-custom" style={{ padding: "8px 20px", fontSize: 13, textDecoration: "none", display: "inline-flex", alignItems: "center", justifyContent: "center" }}>Start Free</Link>
        </div>
      </nav>

      {/* Sous-Navbar des cotations */}
      <MarketTicker />
    </div>
  );
};

export default Navbar;
