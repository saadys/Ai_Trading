import { motion } from "framer-motion";
import { Star } from "lucide-react";

const testimonials = [
  {
    quote: "The AI swing trading analysis identified a perfect cup and handle pattern I completely missed. Made a 15% return following its exact entry and exit points.",
    name: "Michael T.",
    role: "Swing Trader",
    initials: "MT",
    bg: "linear-gradient(135deg, hsl(172, 66%, 40%), hsl(172, 66%, 30%))",
  },
  {
    quote: "The risk management calculations have revolutionized my position sizing. My drawdowns are minimal now while my profits have increased by 28% over the last quarter.",
    name: "Sarah K.",
    role: "Day Trader",
    initials: "SK",
    bg: "linear-gradient(135deg, hsl(220, 70%, 55%), hsl(220, 70%, 45%))",
  },
  {
    quote: "As a scalp trader, timing is everything. The AI analysis gives me clear levels for quick 1:2 R:R trades. I've doubled my win rate since subscribing.",
    name: "Jason L.",
    role: "Scalp Trader",
    initials: "JL",
    bg: "linear-gradient(135deg, hsl(152, 60%, 40%), hsl(152, 60%, 30%))",
  },
];

const Testimonials = () => (
  <div id="testimonials" className="section-block-alt">
    <div className="section-block-alt-inner">
      <div className="section-header">
        <p className="section-tag">Testimonials</p>
        <h2 className="section-title">Loved by Traders</h2>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 4, marginTop: 12 }}>
          {[...Array(5)].map((_, i) => <Star key={i} style={{ width: 16, height: 16, fill: "#f59e0b", color: "#f59e0b" }} />)}
          <span style={{ fontSize: 13, color: "hsl(215, 12%, 52%)", marginLeft: 8 }}>4.8/5 from 289+ reviews</span>
        </div>
      </div>
      <div className="testimonials-grid">
        {testimonials.map((t, i) => (
          <motion.div
            key={t.name}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.1 }}
            className="testimonial-card"
          >
            <p className="testimonial-quote">"{t.quote}"</p>
            <div className="testimonial-author">
              <div className="testimonial-avatar" style={{ background: t.bg }}>
                {t.initials}
              </div>
              <div>
                <p className="testimonial-name">{t.name}</p>
                <p className="testimonial-role">{t.role}</p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  </div>
);

export default Testimonials;
