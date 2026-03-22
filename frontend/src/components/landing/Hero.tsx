import { motion } from "framer-motion";
import { ArrowRight, Star } from "lucide-react";
import { Link } from "react-router-dom";
import HeroChart from "./HeroChart";

const Hero = () => {
  return (
    <section className="hero-section">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7 }}
      >
        <h1 className="hero-title">
          Trade like a pro,{" "}
          <span className="hero-title-accent">without the guru.</span>
        </h1>
        <p className="hero-subtitle">
          AI-powered chart analysis that delivers actionable trade plans based on proven patterns, not personalities.
        </p>
        <div className="hero-buttons">
          <Link to="/dashboard" className="btn-primary-custom" style={{ textDecoration: "none", display: "inline-flex", alignItems: "center", justifyContent: "center" }}>
            Analyze a Chart <ArrowRight style={{ width: 16, height: 16, marginLeft: 8 }} />
          </Link>
          <button className="btn-outline-custom">View Pricing</button>
        </div>
        <div className="hero-reviews">
          {[...Array(5)].map((_, i) => (
            <Star key={i} style={{ width: 16, height: 16, fill: "#f59e0b", color: "#f59e0b" }} />
          ))}
          <span style={{ fontSize: 13, color: "hsl(215, 12%, 52%)", marginLeft: 4 }}>4.8 (289+ reviews)</span>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, x: 40 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.7, delay: 0.2 }}
      >
        <HeroChart />
      </motion.div>
    </section>
  );
};

export default Hero;
