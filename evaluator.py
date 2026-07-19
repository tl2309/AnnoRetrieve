# evaluator.py
import pandas as pd
from typing import List, Dict

class Evaluator:
    @staticmethod
    def compute_f1(predicted: List[Dict], ground_truth: pd.DataFrame) -> Dict:
        gt_dict = {}
        for _, row in ground_truth.iterrows():
            doc_id = row['doc_id']
            gt_dict[doc_id] = {k: v for k, v in row.items() if k != 'doc_id'}
        pred_dict = {d['doc_id']: d['attributes'] for d in predicted}

        tp = fp = fn = 0
        for doc_id, pred_attrs in pred_dict.items():
            if doc_id in gt_dict:
                gt_attrs = gt_dict[doc_id]
                match = True
                for k, v in gt_attrs.items():
                    if k not in pred_attrs or str(pred_attrs[k]) != str(v):
                        match = False
                        break
                if match:
                    tp += 1
                else:
                    fp += 1
            else:
                fp += 1
        for doc_id in gt_dict:
            if doc_id not in pred_dict:
                fn += 1

        precision = tp / (tp+fp) if tp+fp > 0 else 0
        recall = tp / (tp+fn) if tp+fn > 0 else 0
        f1 = 2 * precision * recall / (precision+recall) if precision+recall > 0 else 0
        return {"precision": precision, "recall": recall, "f1": f1}