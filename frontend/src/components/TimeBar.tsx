interface TimeBarProps {
  label: string;
  filled: number;
  total: number;
  timeStr: string;
  color: string;
}

const TimeBar = ({ label, filled, total, timeStr, color }: TimeBarProps) => {
  const pct = total > 0 ? Math.min((filled / total) * 100, 100) : 0;
  return (
    <div className="d-flex align-items-center gap-2 mb-2">
      <span className="text-muted time-bar-label">{label}</span>
      <div className="flex-grow-1 time-bar-track rounded">
        <div
          className="time-bar-fill rounded"
          style={{ width: `${pct}%`, background: color }}
        />
      </div>
      <span className="text-muted time-bar-value">{timeStr}</span>
    </div>
  );
};

export default TimeBar;
