interface VideoHeaderProps {
  title: string;
  url: string;
  llmUsed: string;
  language: string;
}

const VideoHeader = ({ title, url, llmUsed, language }: VideoHeaderProps) => (
  <div className="d-flex justify-content-between align-items-start flex-wrap gap-2 mb-3">
    <h2 className="h5 mb-0">
      <a
        href={url}
        target="_blank"
        rel="noopener noreferrer"
        className="text-decoration-none text-white"
      >
        {title}
      </a>
    </h2>
    <div className="d-flex gap-1">
      <span className="badge bg-secondary">{llmUsed}</span>
      <span className="badge bg-secondary">{language}</span>
    </div>
  </div>
);

export default VideoHeader;
