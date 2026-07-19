# query_engine.py
import re
import pandas as pd
from typing import List, Dict
from llm import ask_extract_attribute
from annotation_index import AnnotationIndex
from util_order import parse_sql, extract_filter_condition
from cal_sel import cal_sel

class QueryEngine:
    def __init__(self, index: AnnotationIndex, schemas: Dict, sampled_data: pd.DataFrame):
        self.index = index
        self.schemas = schemas
        self.sampled_data = sampled_data
        self.llm_calls = 0

    def execute(self, sql_query: str, mode='performance') -> List[Dict]:
        where_clause = parse_sql(sql_query)
        filter_conditions = extract_filter_condition(where_clause)
        schema_conditions = []
        extract_conditions = []
        all_attrs = self._get_all_attrs()

        for cond in filter_conditions:
            parts = cond.split()
            if len(parts) >= 3:
                attr = parts[0]
                op = parts[1]
                val = parts[2]
                if attr in all_attrs:
                    schema_conditions.append({"attribute": attr, "operator": op, "value": val})
                else:
                    extract_conditions.append(cond)

        doc_ids = self.index.filter(schema_conditions)

        result_docs = []
        for doc_id in doc_ids:
            doc_text = self.index.get_document(doc_id)
            skip = False
            for cond in extract_conditions:
                attr = cond.split()[0]
                expected_val = cond.split()[2]
                # Determine model based on mode
                if mode == 'performance':
                    model = 'llm'
                else:
                    model = 'slm'   # economical
                extracted = self._extract_attribute(doc_id, attr, model)
                if extracted is None or str(extracted) != expected_val:
                    skip = True
                    break
                # Store for reuse
                self.index.add_virtual_field(doc_id, attr, extracted)
                self.index.promote_virtual_field(attr)
            if not skip:
                attrs = self.index.attributes.get(doc_id, {}).copy()
                virtual = self.index.virtual_fields.get(doc_id, {})
                attrs.update(virtual)
                result_docs.append({
                    "doc_id": doc_id,
                    "content": doc_text,
                    "attributes": attrs
                })
        return result_docs

    def _get_all_attrs(self):
        attrs = set()
        for table in self.schemas.get('row_schemas', {}):
            attrs.update(self.schemas['row_schemas'][table])
        return attrs

    def _extract_attribute(self, doc_id, attr, model):
        text = self.index.get_document(doc_id)
        if model == 'regex':
            pattern = rf'{attr}[:\s]+([^\s,]+)'
            m = re.search(pattern, text, re.IGNORECASE)
            return m.group(1) if m else None
        elif model == 'slm':
            # For demonstration, we use the same as LLM but with a smaller model in practice
            return self._call_llm_extract(text, attr)
        else:  # llm
            return self._call_llm_extract(text, attr)

    def _call_llm_extract(self, text, attr):
        self.llm_calls += 1
        return ask_extract_attribute(attr, text[:2000])