"""Milestone 4: measure real retrieval distances without spending model calls.

Run after committing criteria and building the index: python calibrate.py
The complete retrieved text is saved so someone else can inspect the evidence.
This is calibration on the development questions, not the Unit 2 evaluation.
"""

import json
import os
from dataclasses import asdict

import config
from questions import OUT_OF_SCOPE, QUESTIONS
from store import search


def main():
    if os.getenv("AI201_FAKE_EMBEDDINGS") == "1":
        raise SystemExit("Calibration requires real embeddings. Unset AI201_FAKE_EMBEDDINGS.")
    if len(QUESTIONS) != 5 or len(OUT_OF_SCOPE) != 5:
        raise SystemExit("Provide exactly five in-corpus and five out-of-scope questions.")
    if any(not item.get("question") or not item.get("expects") for item in QUESTIONS):
        raise SystemExit("Every in-corpus question needs question and expects text.")

    rows = []
    for in_corpus, group in ((True, QUESTIONS), (False, [{"question": q} for q in OUT_OF_SCOPE])):
        for item in group:
            hits = search(item["question"], corpus=config.CORPUS, top_k=config.TOP_K)
            if not hits:
                raise SystemExit("No results: build the index before calibrating.")
            rows.append({**item, "in_corpus": in_corpus,
                         "best_distance": min(hit.distance for hit in hits),
                         "results": [asdict(hit) for hit in hits]})
            print(f"{'IN ' if in_corpus else 'OUT'} {rows[-1]['best_distance']:.6f}  {item['question']}")

    evidence = {"corpus": config.CORPUS, "embedding_model": config.EMBEDDING_MODEL,
                "metric": "cosine", "top_k": config.TOP_K,
                "chunk_size": config.CHUNK_SIZE, "body_overlap": config.CHUNK_OVERLAP,
                "questions": rows}
    config.RESULTS_DIR.mkdir(exist_ok=True)
    path = config.RESULTS_DIR / "unit1_retrieval.json"
    path.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nFull retrieved chunks: {path.relative_to(config.ROOT)}")
    print("\nInspecting the first three test questions:")
    for row in rows[:3]:
        print(f"\nQuestion: {row['question']}")
        for hit in row["results"]:
            print(f"\n{hit['label']} | distance {hit['distance']:.6f}\n{hit['text']}")


if __name__ == "__main__":
    main()
