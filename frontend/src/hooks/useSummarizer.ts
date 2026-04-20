import { useEffect, useState } from "react";
import { fetchLLMs, fetchModels, summarize } from "../api";
import type { LLMOption, SummaryResult } from "../types";

interface UseSummarizerReturn {
  url: string;
  llm: string;
  model: string;
  language: string;
  llmOptions: LLMOption[];
  modelOptions: string[];
  modelsLoading: boolean;
  loading: boolean;
  error: string | null;
  result: SummaryResult | null;
  setUrl: (url: string) => void;
  setLlm: (llm: string) => void;
  setModel: (model: string) => void;
  setLanguage: (language: string) => void;
  handleSubmit: (e: React.FormEvent) => void;
}

const useSummarizer = (): UseSummarizerReturn => {
  const [url, setUrl] = useState("");
  const [llm, setLlm] = useState("");
  const [model, setModel] = useState("");
  const [language, setLanguage] = useState("English");
  const [llmOptions, setLlmOptions] = useState<LLMOption[]>([]);
  const [modelOptions, setModelOptions] = useState<string[]>([]);
  const [modelsLoading, setModelsLoading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<SummaryResult | null>(null);

  useEffect(() => {
    fetchLLMs()
      .then((opts) => {
        setLlmOptions(opts);
        if (opts.length > 0) setLlm(opts[opts.length - 1].value);
      })
      .catch(() => setError("Could not reach the API. Is the server running?"));
  }, []);

  useEffect(() => {
    if (!llm) return;
    setModelsLoading(true);
    setModel("");
    fetchModels(llm)
      .then((models) => {
        setModelOptions(models);
        if (models.length > 0) setModel(models[0]);
      })
      .finally(() => setModelsLoading(false));
  }, [llm]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setResult(null);
    setLoading(true);
    try {
      const data = await summarize(url, llm, language.trim().toLowerCase(), model || null);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  return {
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
  };
};

export default useSummarizer;
