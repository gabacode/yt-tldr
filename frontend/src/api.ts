import type { ChatMessage, LLMOption, SummaryResult } from "./types";

const BASE = import.meta.env.VITE_API_URL as string;

export async function fetchModels(llm: string): Promise<string[]> {
  const res = await fetch(`${BASE}/models?llm=${encodeURIComponent(llm)}`);
  if (!res.ok) return [];
  const data = await res.json();
  return data.models as string[];
}

export async function fetchLLMs(): Promise<LLMOption[]> {
  const res = await fetch(`${BASE}/llms`);
  if (!res.ok) throw new Error("Failed to fetch LLM options");
  const data = await res.json();
  return data.llms as LLMOption[];
}

export async function summarize(
  url: string,
  llm: string,
  language: string,
  model: string | null,
): Promise<SummaryResult> {
  const res = await fetch(`${BASE}/summarize`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, llm, language, model }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? `Request failed: ${res.status}`);
  }
  return res.json() as Promise<SummaryResult>;
}

export async function chat(
  transcript: string,
  llm: string,
  history: ChatMessage[],
  message: string,
  model: string | null,
): Promise<string> {
  const res = await fetch(`${BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ transcript, llm, history, message, model }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? `Request failed: ${res.status}`);
  }
  const data = await res.json();
  return data.reply as string;
}
