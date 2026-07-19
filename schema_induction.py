# schema_induction.py
import random
from typing import List, Dict
from config import Config
from llm import ask_completion_with_retry
from utils import Normalizer

class SchemaLoop:
    def __init__(self):
        self.dataset_schema = {}
        self.table_schemas = {}
        self.row_schemas = {}

    def induce(self, documents: List[Dict]) -> Dict:
        # Detect dataset type from first document content
        dataset_type = self._detect_dataset(documents)
        self.dataset_schema = {"domain": dataset_type, "source": "real"}

        # Group documents (here we treat all as one table)
        groups = {"all": documents}
        table_schemas = {}
        for group_name, docs in groups.items():
            summary = self._summarize(docs)
            schema = self._generate_table_schema(summary)
            schema = self._verify_and_refine(schema, docs, level="table")
            table_schemas[group_name] = schema
        self.table_schemas = table_schemas

        # Row-level schema (per table)
        row_schemas = {}
        for table_name, table_attrs in table_schemas.items():
            refined = self._generate_row_schema(table_attrs, documents)
            refined = self._verify_and_refine(refined, documents, level="row")
            row_schemas[table_name] = refined
        self.row_schemas = row_schemas

        return {
            "dataset_schema": self.dataset_schema,
            "table_schemas": self.table_schemas,
            "row_schemas": self.row_schemas
        }

    def _detect_dataset(self, docs):
        text = docs[0]['content'].lower()
        if "case" in text and "court" in text:
            return "lcr"
        elif "player" in text and "team" in text:
            return "wikitext"
        else:
            return "swde"

    def _summarize(self, docs):
        return " ".join([d['content'][:300] for d in docs[:3]])

    def _generate_table_schema(self, summary):
        prompt = f"From the following document summary, list the most common attributes (fields) that appear. Return only attribute names separated by commas.\nSummary: {summary}"
        response = ask_completion_with_retry([{"role": "user", "content": prompt}], model="gpt-4o", max_tokens=200, temperature=0)
        attrs = [a.strip() for a in response.split(",") if a.strip()]
        return attrs

    def _generate_row_schema(self, table_attrs, docs):
        # Use table attrs as baseline; could be refined
        return table_attrs

    def _verify_and_refine(self, schema, docs, level="row", max_iter=Config.MAX_SCHEMA_ITER):
        current = schema
        for _ in range(max_iter):
            sr, fe = self._compute_metrics(current, docs)
            if sr >= Config.SR_THRESHOLD and fe >= Config.FE_THRESHOLD:
                break
            # Refine
            prompt = f"Current schema: {current}. Extraction success rate = {sr:.2f}, filtering efficiency = {fe:.2f}. Suggest improvements (merge/split/rename). Return new attribute list separated by commas."
            response = ask_completion_with_retry([{"role": "user", "content": prompt}], model="gpt-4o", max_tokens=200, temperature=0)
            current = [a.strip() for a in response.split(",") if a.strip()]
        return current

    def _compute_metrics(self, schema, docs):
        sample = random.sample(docs, min(Config.SAMPLE_SIZE_FOR_VERIFICATION, len(docs)))
        total_pairs = len(sample) * len(schema)
        success = 0
        value_vectors = []
        for doc in sample:
            row = []
            for attr in schema:
                # In real system we would call LLM; here we rely on ground truth if available
                # Since we don't have ground truth during induction, we use simple pattern matching
                # For demonstration, we assume extraction success is high (simplified)
                # A better approach would be to use a small LM to extract
                val = self._mock_extract(doc['content'], attr)
                if val:
                    success += 1
                    row.append(val)
                else:
                    row.append("")
            value_vectors.append(tuple(row))
        sr = success / total_pairs if total_pairs > 0 else 0.0
        from collections import Counter
        counter = Counter(value_vectors)
        max_fraction = max(counter.values()) / len(value_vectors) if value_vectors else 0
        fe = 1 - max_fraction
        return sr, fe

    def _mock_extract(self, text, attr):
        # Simple keyword-based extraction (for verification only)
        # In practice, we would use a lightweight model
        import re
        patterns = {
            "court_name": r'court[:\s]+([^\s,]+)',
            "hearing_year": r'(\d{4})',
            "judgment_year": r'judgment[:\s]+(\d{4})',
            "verdict": r'verdict[:\s]+([^\s,]+)',
            "player_name": r'([A-Z][a-z]+ [A-Z][a-z]+)',
            "team_name": r'team[:\s]+([^\s,]+)',
            "birth_year": r'born in (\d{4})',
            "active_status": r'active[:\s]+(True|False)',
        }
        if attr in patterns:
            m = re.search(patterns[attr], text, re.IGNORECASE)
            return m.group(1) if m else ""
        return ""