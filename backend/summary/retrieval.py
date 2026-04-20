from rank_bm25 import BM25Okapi


def chunk_transcript(text: str, size: int = 150, overlap: int = 20) -> list[str]:
    words = text.split()
    chunks, i = [], 0
    while i < len(words):
        chunks.append(" ".join(words[i:i + size]))
        i += size - overlap
    return chunks


def retrieve_relevant_chunks(transcript: str, query: str, top_k: int = 3) -> str:
    chunks = chunk_transcript(transcript)
    if not chunks:
        return transcript
    bm25 = BM25Okapi([c.lower().split() for c in chunks])
    scores = bm25.get_scores(query.lower().split())
    top_idx = sorted(sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k])
    return "\n\n".join(chunks[i] for i in top_idx)
