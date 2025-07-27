#!/usr/bin/env python3
"""
Combine, deduplicate, and embed Reddit data (daily + historical) with parallel processing.
Stores results in ChromaDB with full context and relationships.
"""
import sys
import os
import json
import argparse
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.rag_optimized_processor import RAGOptimizedProcessor
from src.rag.embeddings import EmbeddingGenerator
from src.rag.vector_store import VectorStore
from config.settings import Config

# --- Step 1: Combine and deduplicate ---
def combine_and_dedup(daily_path, historical_path, out_path):
    """Combine two Reddit .jsonl files, deduplicate by id (keep latest by ingested_at), write to out_path."""
    id_to_record = {}
    for path in [historical_path, daily_path]:  # daily last, so it wins if duplicate
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    record = json.loads(line)
                    rec_id = record['id']
                    # If duplicate, keep the one with latest ingested_at
                    if rec_id in id_to_record:
                        prev = id_to_record[rec_id]
                        if record.get('ingested_at', '') > prev.get('ingested_at', ''):
                            id_to_record[rec_id] = record
                    else:
                        id_to_record[rec_id] = record
                except Exception:
                    continue
    with open(out_path, 'w', encoding='utf-8') as f:
        for rec in id_to_record.values():
            f.write(json.dumps(rec) + '\n')
    print(f"✅ Combined and deduped: {len(id_to_record)} unique records written to {out_path}")
    return out_path

# --- Step 2: Chunk and contextify ---
def process_for_rag(file_path, chunk_size, chunk_overlap):
    """Yield RAG-optimized chunks from the combined file."""
    processor = RAGOptimizedProcessor(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    for doc in processor.process_reddit_data_rag_optimized(file_path):
        yield doc

# --- Top-level embedding function for multiprocessing ---
def embed_one(args):
    text, model = args
    from src.rag.embeddings import EmbeddingGenerator  # Import inside for multiprocessing safety
    return EmbeddingGenerator(model).get_embedding(text)

# --- Step 3: Parallel embedding ---
def embed_documents_parallel(docs, model, num_workers):
    """Embed documents in parallel using multiprocessing."""
    texts = [doc.content for doc in docs]
    args_list = [(text, model) for text in texts]
    embeddings = [None] * len(texts)
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = {executor.submit(embed_one, arg): idx for idx, arg in enumerate(args_list)}
        for f in tqdm(as_completed(futures), total=len(futures), desc="Embedding"):
            idx = futures[f]
            embeddings[idx] = f.result()
    return embeddings

# --- Step 4: Store in ChromaDB ---
def store_in_chroma(docs, embeddings, config):
    # Filter out docs with empty or invalid embeddings
    valid_docs = []
    valid_embeddings = []
    skipped = 0
    for doc, emb in zip(docs, embeddings):
        if emb and isinstance(emb, list) and len(emb) > 0:
            valid_docs.append(doc)
            valid_embeddings.append(emb)
        else:
            print(f"[SKIP] {doc.id} - empty or invalid embedding")
            skipped += 1
    print(f"✅ {len(valid_docs)} valid documents will be stored. {skipped} skipped due to empty embeddings.")
    vector_store = VectorStore(config.COLLECTION_NAME, config.VECTOR_DB_DIR)
    vector_store.add_documents(valid_docs, valid_embeddings)

# --- Main script ---
def main():
    parser = argparse.ArgumentParser(description="Combine, dedup, and embed Reddit data (daily + historical)")
    parser.add_argument('--daily', required=True, help='Path to daily Reddit .jsonl file')
    parser.add_argument('--historical', required=True, help='Path to historical Reddit .jsonl file')
    parser.add_argument('--out', default='data/processed/reddit_combined.jsonl', help='Output combined file')
    parser.add_argument('--workers', type=int, default=32, help='Number of parallel embedding workers')
    parser.add_argument('--chunk-size', type=int, default=1000)
    parser.add_argument('--chunk-overlap', type=int, default=200)
    parser.add_argument('--embedding-model', type=str, default='text-embedding-3-small')
    args = parser.parse_args()

    config = Config()
    start = time.time()

    # Step 1: Combine and dedup
    combined_path = combine_and_dedup(args.daily, args.historical, args.out)

    # Step 2: Chunk/contextify
    print("🔄 Chunking and adding context...")
    docs = list(process_for_rag(combined_path, args.chunk_size, args.chunk_overlap))
    print(f"   📄 {len(docs)} RAG-optimized chunks ready for embedding.")

    # Step 3: Parallel embedding
    print(f"⚡ Embedding with {args.workers} workers...")
    embeddings = embed_documents_parallel(docs, args.embedding_model, args.workers)

    # Step 4: Store in ChromaDB
    print("💾 Storing in ChromaDB...")
    store_in_chroma(docs, embeddings, config)

    elapsed = time.time() - start
    print(f"✅ All done! {len(docs)} documents embedded and stored in {elapsed:.1f} seconds.")

if __name__ == "__main__":
    main() 