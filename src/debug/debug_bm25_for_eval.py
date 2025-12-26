import json
from loguru import logger

from src.vector_store.bm25_store import BM25Store
from src.search.expand_bm25_context import expand_bm25_context
from src.search.merge_expanded_blocks import merge_expanded_blocks
from src.search.faiss_on_expanded_blocks import faiss_select_from_blocks
from config.config import Config
from src.embeddings.embedder import Embedder

EVAL_FILE = 'data/eval/gold_queries.json'
TOP_K = 5


def load_eval_queries(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    logger.info("START DEBUG BM25 CONTEXT EXPANSION")

    config = Config()

    bm25 = BM25Store()
    embedder = Embedder()
    bm25.load(config.paths['bm25_index'])

    all_chunks = bm25.documents

    eval_data = load_eval_queries(EVAL_FILE)

    for item in eval_data:
        print("\n" + "=" * 100)
        print(f"TOPIC: {item['id']} - {item['topic']}")
        print("=" * 100)

        for q_idx, query in enumerate(item["queries"], start=1):
            print(f"\nQUERY {q_idx}: {query}")
            print("-" * 100)

            # 🔹 1. BM25 якоря
            bm25_hits = bm25.search(query, top_k=TOP_K)

            if not bm25_hits:
                print("NO BM25 RESULTS")
                continue

            # 🔹 2. Расширяем контекст
            expanded_blocks = expand_bm25_context(
                bm25_hits=bm25_hits,
                all_chunks=all_chunks,
                window_before=4,
                window_after=15,
            )
            merged_blocks = merge_expanded_blocks(expanded_blocks)


            texts = [b["text"] for b in merged_blocks]
            embs = embedder.embed(texts)
            q_emb = embedder.embed([query])[0]

            faiss_blocks = faiss_select_from_blocks(
                                query_embedding=q_emb,
                                blocks=merged_blocks,
                                block_embeddings=embs,
                                top_k=3)

            for rank, block in enumerate(faiss_blocks, start=1):
                print(f"\nRANK {rank}")
                print(f"BM25_SCORE: {block['bm25_score']:.3f}")
                print(f"PATH: {block['path']}")
                print(f"PAGES: {block.get('page')}")
                print(f"CHUNK_INDICES: {block['chunk_indices']}")
                print("-" * 60)
                print(block["text"][:1200])

        input("\nPress ENTER to continue to next topic...")


if __name__ == "__main__":
    main()
