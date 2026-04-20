import { useState } from "react";

interface TranscriptCardProps {
  transcript: string;
}

const TranscriptCard = ({ transcript }: TranscriptCardProps) => {
  const [show, setShow] = useState(false);

  return (
    <div className="card">
      <div className="card-body">
        <button
          className="btn btn-link text-muted p-0 text-decoration-none small"
          onClick={() => setShow((v) => !v)}
        >
          {show ? "▲ Hide transcript" : "▼ Show transcript"}
        </button>
        {show && <div className="transcript mt-3 mb-0">{transcript}</div>}
      </div>
    </div>
  );
};

export default TranscriptCard;
