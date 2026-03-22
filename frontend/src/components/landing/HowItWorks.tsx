import { motion } from "framer-motion";
import { Upload, Cpu, Target } from "lucide-react";

const steps = [
  { num: "01", icon: Upload, title: "Upload Your Chart", desc: "Upload your chart or connect your favorite trading platform for instant access to analytics." },
  { num: "02", icon: Cpu, title: "AI Analysis", desc: "Our AI scans for proven patterns and key support/resistance levels in seconds." },
  { num: "03", icon: Target, title: "Get Your Trade Plan", desc: "Get actionable entries, exits, and risk management suggestions tailored to your style." },
];

const HowItWorks = () => (
  <div className="section-block-alt">
    <div className="section-block-alt-inner">
      <div className="section-header">
        <p className="section-tag">How It Works</p>
        <h2 className="section-title">Three Simple Steps</h2>
      </div>
      <div className="steps-grid">
        {steps.map((s, i) => (
          <motion.div
            key={s.num}
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.15 }}
            className="step-card"
          >
            <span className="step-num">{s.num}</span>
            <div className="step-icon">
              <s.icon style={{ width: 24, height: 24, color: "hsl(172, 66%, 40%)" }} />
            </div>
            <h3 className="step-title">{s.title}</h3>
            <p className="step-desc">{s.desc}</p>
          </motion.div>
        ))}
      </div>
    </div>
  </div>
);

export default HowItWorks;
