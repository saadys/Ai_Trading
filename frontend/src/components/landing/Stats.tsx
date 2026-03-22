import { motion } from "framer-motion";

const stats = [
  { value: "10,000+", label: "Active Traders" },
  { value: "1M+", label: "Charts Analyzed" },
  { value: "<3 sec", label: "Analysis Time" },
  { value: "4.8", label: "User Rating" },
];

const Stats = () => (
  <section className="stats-section">
    {stats.map((s, i) => (
      <motion.div
        key={s.label}
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ delay: i * 0.1 }}
        className="stat-item"
      >
        <p className="stat-value">{s.value}</p>
        <p className="stat-label">{s.label}</p>
      </motion.div>
    ))}
  </section>
);

export default Stats;
