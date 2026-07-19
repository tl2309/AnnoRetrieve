# main.py
import os
import json
import pandas as pd
from config import Config
from data_loader import DataLoader
from schema_induction import SchemaLoop
from annotation_index import AnnotationIndex
from query_engine import QueryEngine
from evaluator import Evaluator
from llm import init_chatgpt

def run_experiment(dataset_name):
    print(f"\n=== Running AnnoIndex on {dataset_name} ===")

    # 1. Load data
    docs = DataLoader.load_documents(dataset_name)
    print(f"  Loaded {len(docs)} documents")
    if not docs:
        print("  No documents found. Skipping.")
        return None

    # 2. Load ground truth (optional)
    gt_df = DataLoader.load_ground_truth(dataset_name)
    if gt_df is not None:
        print(f"  Loaded ground truth with {len(gt_df)} entries")
    else:
        print("  No ground truth found. Evaluation will be skipped.")

    # 3. Schema induction
    schema_loop = SchemaLoop()
    schemas = schema_loop.induce(docs)
    print(f"  Induced row schemas: {schemas['row_schemas']}")

    # 4. Build index
    index = AnnotationIndex()
    index.build(docs, schemas)
    print(f"  Built index with {len(index.documents)} documents")

    # 5. Load queries
    queries = DataLoader.load_queries(dataset_name)
    print(f"  Loaded {len(queries)} queries")

    # 6. Prepare sample data for selectivity (use first 10 docs)
    sample_df = pd.DataFrame([{'doc_id': d['doc_id'], **d.get('attributes', {})} for d in docs[:10]])
    if gt_df is not None:
        sample_df = sample_df.merge(gt_df, on='doc_id', how='left')

    # 7. Create query engine
    engine = QueryEngine(index, schemas, sample_df)

    # 8. Execute queries (limit to first 50 for demo)
    all_predicted = []
    for i, q in enumerate(queries[:50]):
        results = engine.execute(q, mode='performance')
        all_predicted.extend(results)
        print(f"  Query {i+1}: {q[:60]}... -> {len(results)} docs")

    # 9. Evaluate
    if gt_df is not None:
        metrics = Evaluator.compute_f1(all_predicted, gt_df)
        print(f"  Precision: {metrics['precision']:.3f}, Recall: {metrics['recall']:.3f}, F1: {metrics['f1']:.3f}")
        print(f"  Total LLM calls: {engine.llm_calls}")
        return metrics
    else:
        print("  Evaluation skipped.")
        return None

if __name__ == "__main__":
    # Initialize OpenAI
    init_chatgpt(Config.OPENAI_KEY)
    os.makedirs(Config.RESULT_DIR, exist_ok=True)

    results = {}
    for ds in ['lcr', 'wikitext', 'swde']:
        res = run_experiment(ds)
        if res:
            results[ds] = res

    if results:
        print("\n=== Summary ===")
        for ds, m in results.items():
            print(f"{ds}: F1={m['f1']:.3f}")
        # Save summary
        with open(os.path.join(Config.RESULT_DIR, "summary.json"), "w") as f:
            json.dump(results, f, indent=2)