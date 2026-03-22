import { useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Check } from "lucide-react";

const featuresList = [
  "Unlimited AI chart analysis",
  "Swing & scalp trading patterns",
  "Advanced risk management",
  "Trade journaling system",
  "Learning resources center",
  "Priority support",
];

const Pricing = () => {
  const [annual, setAnnual] = useState(true);

  return (
    <section id="pricing" className="section-block">
      <div className="section-header">
        <p className="section-tag">Pricing Plans</p>
        <h2 className="section-title">Plans for all sizes</h2>
        <p className="section-desc">Simple, transparent pricing that grows with you</p>

        <div className="pricing-toggle">
          <button
            className={`pricing-toggle-btn ${!annual ? "active" : ""}`}
            onClick={() => setAnnual(false)}
          >
            Monthly
          </button>
          <button
            className={`pricing-toggle-btn ${annual ? "active" : ""}`}
            onClick={() => setAnnual(true)}
          >
            Yearly
          </button>
        </div>
        {annual && (
          <span style={{
            display: "inline-block",
            marginTop: 12,
            fontSize: 12,
            fontWeight: 600,
            color: "hsl(152, 60%, 35%)",
            background: "hsl(152, 60%, 45%, 0.1)",
            padding: "4px 12px",
            borderRadius: 100,
          }}>
            Save 58%
          </span>
        )}
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        className="pricing-card"
      >
        <h3 style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: 22, fontWeight: 700, color: "hsl(215, 30%, 14%)" }}>Pro</h3>
        <p style={{ fontSize: 14, color: "hsl(215, 12%, 52%)", marginTop: 4 }}>Everything you need to trade smarter</p>
        <div style={{ marginTop: 24 }}>
          <span className="pricing-amount">${annual ? "8.33" : "19.99"}</span>
          <span className="pricing-period"> /Month</span>
        </div>
        <Link to="/dashboard" className="btn-primary-custom" style={{ width: "100%", justifyContent: "center", marginTop: 24, textDecoration: "none", display: "inline-flex", alignItems: "center" }}>
          Get Started
        </Link>
        <ul className="pricing-features">
          {featuresList.map((f) => (
            <li key={f}>
              <Check style={{ width: 16, height: 16, color: "hsl(172, 66%, 40%)", flexShrink: 0 }} />
              {f}
            </li>
          ))}
        </ul>
        <p style={{ fontSize: 12, color: "hsl(215, 12%, 60%)", textAlign: "center", marginTop: 20 }}>Cancel anytime</p>
      </motion.div>
    </section>
  );
};

export default Pricing;
