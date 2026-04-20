import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface SummaryCardProps {
  summary: string;
}

const SummaryCard = ({ summary }: SummaryCardProps) => (
  <div className="card mb-3">
    <div className="card-body">
      <h6 className="text-uppercase text-muted small mb-3 letter-spacing">
        Summary
      </h6>
      <div className="markdown-body">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{summary}</ReactMarkdown>
      </div>
    </div>
  </div>
);

export default SummaryCard;
