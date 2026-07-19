# data_loader.py
import os
import pandas as pd
from typing import List, Dict, Optional
from config import Config

class DataLoader:
    @staticmethod
    def load_documents(dataset_name: str) -> List[Dict]:
        """
        Load all .txt files from data/raw/{dataset_name}/
        Returns list of dicts: [{"doc_id": str, "content": str}, ...]
        """
        doc_dir = os.path.join(Config.RAW_DIR, dataset_name)
        if not os.path.exists(doc_dir):
            raise FileNotFoundError(f"Document directory not found: {doc_dir}")
        docs = []
        for filename in os.listdir(doc_dir):
            if filename.endswith(".txt"):
                doc_id = filename[:-4]   # strip .txt
                with open(os.path.join(doc_dir, filename), "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                docs.append({"doc_id": doc_id, "content": content})
        return docs

    @staticmethod
    def load_ground_truth(dataset_name: str) -> Optional[pd.DataFrame]:
        """
        Load ground truth CSV from data/ground_truth/{dataset_name}.csv
        Expected columns: doc_id, attr1, attr2, ...
        """
        gt_path = os.path.join(Config.GROUND_TRUTH_DIR, f"{dataset_name}.csv")
        if os.path.exists(gt_path):
            return pd.read_csv(gt_path)
        return None

    @staticmethod
    def load_queries(dataset_name: str) -> List[str]:
        """
        Load queries from data/queries/{dataset_name}.txt
        One SQL query per line; lines starting with '...' or '--' are ignored.
        """
        q_path = os.path.join(Config.QUERY_DIR, f"{dataset_name}.txt")
        if not os.path.exists(q_path):
            raise FileNotFoundError(f"Query file not found: {q_path}")
        with open(q_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith("...") and not line.startswith("--")]
        return lines