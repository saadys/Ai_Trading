import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine, ReferenceDot } from "recharts";

const data = [
  { time: "9:30", price: 413.63 },
  { time: "9:40", price: 414.10 },
  { time: "9:50", price: 414.80 },
  { time: "10:00", price: 415.50 },
  { time: "10:10", price: 416.80 },
  { time: "10:20", price: 418.20 },
  { time: "10:30", price: 419.50 },
  { time: "10:40", price: 419.80 },
  { time: "10:50", price: 419.40 },
  { time: "11:00", price: 418.60 },
  { time: "11:10", price: 417.20 },
  { time: "11:20", price: 415.50 },
  { time: "11:30", price: 413.00 },
  { time: "11:40", price: 411.50 },
  { time: "11:50", price: 410.20 },
  { time: "12:00", price: 409.50 },
  { time: "12:10", price: 409.80 },
  { time: "12:20", price: 410.60 },
  { time: "12:30", price: 412.00 },
  { time: "12:40", price: 413.50 },
  { time: "12:50", price: 415.20 },
  { time: "13:00", price: 416.80 },
  { time: "13:10", price: 418.00 },
  { time: "13:20", price: 419.50 },
  { time: "13:30", price: 420.40 },
  { time: "13:40", price: 421.00 },
  { time: "13:45", price: 421.67 },
  { time: "13:50", price: 423.50 },
  { time: "14:00", price: 426.00 },
  { time: "14:10", price: 429.50 },
  { time: "14:20", price: 432.00 },
  { time: "14:30", price: 434.50 },
];

const signalIndex = 17; // 13:45
const signalPoint = data[signalIndex];

const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="hero-chart-tooltip">
        <p className="hero-chart-tooltip-time">Time: {payload[0].payload.time}</p>
        <p className="hero-chart-tooltip-price">Price: ${payload[0].value.toFixed(2)}</p>
        <p className="hero-chart-tooltip-signal">Buy Signal</p>
      </div>
    );
  }
  return null;
};

const HeroChart = () => {
  return (
    <div className="hero-chart-card">
      <div className="hero-chart-container">
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={data} margin={{ top: 20, right: 30, left: 10, bottom: 5 }}>
            <XAxis
              dataKey="time"
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 12, fill: "#9ca3af" }}
              interval={4}
            />
            <YAxis
              domain={[405, 436]}
              ticks={[405.63, 413.63, 421.63, 435.21]}
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 12, fill: "#9ca3af" }}
              tickFormatter={(v) => v.toFixed(2)}
              width={55}
            />
            <Tooltip content={<CustomTooltip />} />
            <ReferenceLine
              x={signalPoint.time}
              stroke="#22c55e"
              strokeDasharray="6 4"
              strokeWidth={2}
            />
            <Line
              type="monotone"
              dataKey="price"
              stroke="#6c3aed"
              strokeWidth={3}
              dot={false}
              activeDot={{ r: 5, fill: "#6c3aed", stroke: "#fff", strokeWidth: 2 }}
            />
            <ReferenceDot
              x={signalPoint.time}
              y={signalPoint.price}
              r={6}
              fill="#6c3aed"
              stroke="#fff"
              strokeWidth={3}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div className="hero-chart-footer">
        <div className="hero-chart-footer-left">
          <p className="hero-chart-label">SPY Daily Chart</p>
          <p className="hero-chart-signal">
            <span className="hero-chart-signal-dot" />
            Buy Signal Detected
          </p>
        </div>
        <div className="hero-chart-confidence">87% Confidence</div>
      </div>
    </div>
  );
};

export default HeroChart;
