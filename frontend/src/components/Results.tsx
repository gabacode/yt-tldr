import type { SummaryResult } from "../types";
import VideoHeader from "./VideoHeader";
import SummaryCard from "./SummaryCard";
import TimeStatsCard from "./TimeStatsCard";
import ChatCard from "./ChatCard";
import TranscriptCard from "./TranscriptCard";

interface ResultsProps {
  result: SummaryResult;
  llm: string;
  model: string;
}

const Results = ({ result, llm, model }: ResultsProps) => (
  <div>
    <VideoHeader
      title={result.video_title}
      url={result.video_url}
      llmUsed={result.llm_used}
      language={result.language}
    />
    <TimeStatsCard timeStats={result.time_stats} />
    <SummaryCard summary={result.summary} />
    <ChatCard transcript={result.transcript} llm={llm} model={model} />
    <TranscriptCard transcript={result.transcript} />
  </div>
);

export default Results;
