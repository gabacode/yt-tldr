import type { LLMOption } from "../types";

interface SummarizeFormProps {
  url: string;
  llm: string;
  model: string;
  language: string;
  llmOptions: LLMOption[];
  modelOptions: string[];
  modelsLoading: boolean;
  loading: boolean;
  onUrlChange: (url: string) => void;
  onLlmChange: (llm: string) => void;
  onModelChange: (model: string) => void;
  onLanguageChange: (language: string) => void;
  onSubmit: (e: React.FormEvent) => void;
}

const SummarizeForm = ({
  url,
  llm,
  model,
  language,
  llmOptions,
  modelOptions,
  modelsLoading,
  loading,
  onUrlChange,
  onLlmChange,
  onModelChange,
  onLanguageChange,
  onSubmit,
}: SummarizeFormProps) => (
  <form className="card mb-4" onSubmit={onSubmit}>
    <div className="card-body d-flex flex-column gap-3">
      <div>
        <label htmlFor="url" className="form-label text-muted small">
          YouTube URL
        </label>
        <input
          id="url"
          type="url"
          className="form-control"
          placeholder="https://www.youtube.com/watch?v=..."
          value={url}
          onChange={(e) => onUrlChange(e.target.value)}
          required
          disabled={loading}
        />
      </div>

      <div className="row g-3">
        <div className="col-sm-4">
          <label htmlFor="llm" className="form-label text-muted small">
            Provider
          </label>
          <select
            id="llm"
            className="form-select"
            value={llm}
            onChange={(e) => onLlmChange(e.target.value)}
            disabled={loading}
          >
            {llmOptions.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.name}
              </option>
            ))}
          </select>
        </div>

        <div className="col-sm-4">
          <label htmlFor="model" className="form-label text-muted small">
            Model
          </label>
          <select
            id="model"
            className="form-select"
            value={model}
            onChange={(e) => onModelChange(e.target.value)}
            disabled={loading || modelsLoading || modelOptions.length === 0}
          >
            {modelsLoading && <option value="">Loading…</option>}
            {!modelsLoading && modelOptions.length === 0 && (
              <option value="">Default</option>
            )}
            {modelOptions.map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
        </div>

        <div className="col-sm-4">
          <label htmlFor="language" className="form-label text-muted small">
            Language
          </label>
          <input
            id="language"
            type="text"
            className="form-control"
            value={language}
            onChange={(e) => onLanguageChange(e.target.value)}
            disabled={loading}
          />
        </div>
      </div>

      <div>
        <button
          type="submit"
          className="btn btn-primary"
          disabled={loading || !url}
        >
          {loading ? (
            <>
              <span className="spinner-border spinner-border-sm me-2" />
              Processing…
            </>
          ) : (
            "Summarize"
          )}
        </button>
      </div>
    </div>
  </form>
);

export default SummarizeForm;
