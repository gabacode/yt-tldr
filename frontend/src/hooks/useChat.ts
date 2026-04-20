import { useState } from "react";
import { chat as apiChat } from "../api";
import type { ChatMessage } from "../types";

interface UseChatReturn {
  messages: ChatMessage[];
  input: string;
  loading: boolean;
  error: string | null;
  setInput: (value: string) => void;
  handleSend: () => void;
}

const useChat = (transcript: string, llm: string, model: string): UseChatReturn => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSend = async () => {
    const message = input.trim();
    if (!message || loading) return;

    const userMessage: ChatMessage = { role: "user", content: message };
    const nextMessages = [...messages, userMessage];
    setMessages(nextMessages);
    setInput("");
    setError(null);
    setLoading(true);

    try {
      const reply = await apiChat(transcript, llm, messages, message, model || null);
      setMessages([...nextMessages, { role: "assistant", content: reply }]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  return { messages, input, loading, error, setInput, handleSend };
};

export default useChat;
