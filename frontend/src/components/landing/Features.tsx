import { motion } from "framer-motion";
import { BarChart3, Crosshair, Shield, BookOpen } from "lucide-react";

const features = [
  { icon: BarChart3, title: "AI Chart Analysis", desc: "Get detailed trade reviews with our AI that analyzes your chart patterns and trading decisions." },
  { icon: Crosshair, title: "Smart Entry Points", desc: "Identify optimal entry and exit points with our AI-powered pattern recognition system." },
  { icon: Shield, title: "Risk Management", desc: "Optimize your position sizes and see potential returns based on AI-calculated risk profiles." },
  { icon: BookOpen, title: "Trade Journaling", desc: "Track your trading progress with comprehensive analytics to improve consistency." },
];

const Features = () => (
  <section id="features" className="section-block">
    <div className="section-header">
      <p className="section-tag">Key Features</p>
      <h2 className="section-title">Discover Key Features</h2>
      <p className="section-desc">
        Vibe Trade combines powerful AI technology with intuitive tools to help you make better trading decisions
      </p>
    </div>
    <div className="features-grid">
      {features.map((f, i) => (
        <motion.div
          key={f.title}
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: i * 0.1 }}
          className="feature-card"
        >
          <div className="feature-icon">
            <f.icon style={{ width: 20, height: 20, color: "hsl(172, 66%, 40%)" }} />
          </div>
          <div>
            <h3 className="feature-title">{f.title}</h3>
            <p className="feature-desc">{f.desc}</p>
          </div>
        </motion.div>
      ))}
    </div>
  </section>
);

export default Features;
