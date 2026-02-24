import type { TimeStats } from "../types";
import { formatTime } from "../utils";
import TimeBar from "./TimeBar";

interface TimeStatsCardProps {
  timeStats: TimeStats;
}

const TimeStatsCard = ({ timeStats: ts }: TimeStatsCardProps) => {
  const videoTimeStr = formatTime(
    ts.video_length_minutes,
    ts.video_length_seconds
  );
  const readingTimeStr = formatTime(
    ts.reading_time_minutes,
    ts.reading_time_seconds
  );

  const stats = [
    { value: videoTimeStr, label: "Video length" },
    { value: readingTimeStr, label: "Reading time" },
    {
      value: `${ts.percentage_saved.toFixed(0)}%`,
      label: "Time saved",
      highlight: true,
    },
    { value: String(ts.word_count), label: "Words in summary" },
  ];

  return (
    <div className="card mb-3">
      <div className="card-body">
        <h6 className="text-uppercase text-muted small mb-3 letter-spacing">
          Time Saved
        </h6>
        <div className="row g-2 mb-4">
          {stats.map(({ value, label, highlight }) => (
            <div className="col-6 col-md-3" key={label}>
              <div className="text-center p-3 rounded bg-body-secondary h-100">
                <div
                  className={`fs-4 fw-bold ${highlight ? "text-success" : ""}`}
                >
                  {value}
                </div>
                <div className="text-muted small text-uppercase">{label}</div>
              </div>
            </div>
          ))}
        </div>
        <TimeBar
          label="Video"
          filled={ts.video_length_minutes}
          total={ts.video_length_minutes}
          timeStr={videoTimeStr}
          color="var(--bs-primary)"
        />
        <TimeBar
          label="Reading"
          filled={ts.reading_time_minutes}
          total={ts.video_length_minutes}
          timeStr={readingTimeStr}
          color="var(--bs-success)"
        />
      </div>
    </div>
  );
};

export default TimeStatsCard;
