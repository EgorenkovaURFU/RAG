import json
from loguru import logger

from src.llm.rag_pipeline import RAGPipeline

EVAL_FILE = 'data/eval/gold_queries.json'
TOP_K = 10


def load_eval_queries(path):
    with open(path, 'r', encoding="utf-8") as f:
        return json.load(f)
    

def main():
    logger.info("START DEBUG CHUNKS FOR EVAL")

    pipeline  = RAGPipeline(top_k=10)
    eval_data = load_eval_queries(EVAL_FILE)

    for item in eval_data:
        print("\n" + "=" * 100)
        print(f'TOPIC: {item['id']} - {item['topic']}')
        print("=" * 100)

        for q_idx, query in enumerate(item['queries'], start=1):
            print(f'\nQUERY {q_idx}: {query}')
            print('-' * 100)

            docs, metas = pipeline.retrieve(query=query)

            if not docs:
                print("NO RESULTS")
                continue

            for rank, (text, meta) in enumerate(zip(docs, metas), start=1):
                print(f'\nRANK {rank}')
                print(f'CHUNK_ID: {meta.get('chunk_id')}')
                print(f'PAGE: {meta.get('page')}')
                print(f'PATH: {meta.get('path')}')
                print('-' * 60)
                print(text[:500])

        input('\nPress ENTER to continue to next topic...')


if __name__=='__main__':
    main()

