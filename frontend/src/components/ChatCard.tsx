import { useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import useChat from "../hooks/useChat";

interface ChatCardProps {
  transcript: string;
  llm: string;
  model: string;
}

const ChatCard = ({ transcript, llm, model }: ChatCardProps) => {
  const { messages, input, loading, error, setInput, handleSend } = useChat(transcript, llm, model);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="card mb-3">
      <div className="card-body">
        <h6 className="text-uppercase text-muted small mb-3 letter-spacing">
          Chat with video
        </h6>

        <div
          style={{ height: 320, overflowY: "auto" }}
          className="mb-3 d-flex flex-column gap-2"
        >
          {messages.length === 0 && (
            <p className="text-muted small text-center mt-auto mb-auto">
              Ask a question about the video.
            </p>
          )}
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`d-flex ${msg.role === "user" ? "justify-content-end" : "justify-content-start"}`}
            >
              <div
                className={`rounded px-3 py-2 small ${
                  msg.role === "user"
                    ? "bg-primary text-white"
                    : "bg-body-secondary"
                }`}
                style={{ maxWidth: "80%" }}
              >
                {msg.role === "user" ? (
                  msg.content
                ) : (
                  <div className="markdown-body">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {msg.content}
                    </ReactMarkdown>
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div className="d-flex justify-content-start">
              <div className="rounded px-3 py-2 small bg-body-secondary text-muted">
                <span className="spinner-border spinner-border-sm me-2" role="status" />
                Thinking…
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {error && <div className="alert alert-danger py-2 small">{error}</div>}

        <div className="input-group">
          <input
            type="text"
            className="form-control"
            placeholder="Ask a question…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
          />
          <button
            className="btn btn-primary"
            onClick={handleSend}
            disabled={loading || !input.trim()}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatCard;
