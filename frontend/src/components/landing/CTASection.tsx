import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";

const CTASection = () => (
  <section className="cta-section">
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      style={{ maxWidth: 600, margin: "0 auto" }}
    >
      <p className="section-tag">Start Trading Smarter</p>
      <h2 className="section-title" style={{ marginTop: 12 }}>Ready to out-trade your mentor?</h2>
      <p className="section-desc">
        Join thousands of traders making data-driven decisions with AI-powered chart analysis.
      </p>
      <Link to="/dashboard" className="btn-primary-custom" style={{ marginTop: 32, textDecoration: "none", display: "inline-flex", alignItems: "center", justifyContent: "center" }}>
        Analyze My First Chart <ArrowRight style={{ width: 16, height: 16, marginLeft: 8 }} />
      </Link>
    </motion.div>
  </section>
);

export default CTASection;
