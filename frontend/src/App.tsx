import useSummarizer from "./hooks/useSummarizer";
import SummarizeForm from "./components/SummarizeForm";
import Results from "./components/Results";
import "./App.css";

const App = () => {
  const {
    url,
    llm,
    model,
    language,
    llmOptions,
    modelOptions,
    modelsLoading,
    loading,
    error,
    result,
    setUrl,
    setLlm,
    setModel,
    setLanguage,
    handleSubmit,
  } = useSummarizer();

  return (
    <div className="container py-4 py-md-5" style={{ maxWidth: 800 }}>
      <header className="text-center mb-5">
        <h1 className="gradient-title fw-bold">yt-tldr</h1>
        <p className="text-muted">YouTube summaries, powered by AI</p>
      </header>

      <SummarizeForm
        url={url}
        llm={llm}
        model={model}
        language={language}
        llmOptions={llmOptions}
        modelOptions={modelOptions}
        modelsLoading={modelsLoading}
        loading={loading}
        onUrlChange={setUrl}
        onLlmChange={setLlm}
        onModelChange={setModel}
        onLanguageChange={setLanguage}
        onSubmit={handleSubmit}
      />

      {error && <div className="alert alert-danger">{error}</div>}
      {result && <Results result={result} llm={llm} model={model} />}
    </div>
  );
};

export default App;
