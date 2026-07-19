# annotation_index.py
import json
import os
from typing import List, Dict
from config import Config

class AnnotationIndex:
    def __init__(self, storage_dir=Config.INDEX_DIR):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        self.documents = {}
        self.attributes = {}
        self.schemas = {}
        self.virtual_fields = {}
        self.field_count = {}

    def build(self, documents: List[Dict], schemas: Dict):
        self.schemas = schemas
        for doc in documents:
            doc_id = doc['doc_id']
            self.documents[doc_id] = doc['content']
            self.attributes[doc_id] = {}
            # If ground truth attributes are present, store them
            if 'attributes' in doc:
                self.attributes[doc_id] = doc['attributes']
        self.virtual_fields = {doc_id: {} for doc_id in self.documents}
        self._persist()

    def _persist(self):
        data = {
            "documents": self.documents,
            "attributes": self.attributes,
            "schemas": self.schemas,
            "virtual_fields": self.virtual_fields,
            "field_count": self.field_count
        }
        with open(os.path.join(self.storage_dir, "index.json"), "w") as f:
            json.dump(data, f)

    def load(self):
        with open(os.path.join(self.storage_dir, "index.json"), "r") as f:
            data = json.load(f)
            self.documents = data["documents"]
            self.attributes = data["attributes"]
            self.schemas = data["schemas"]
            self.virtual_fields = data.get("virtual_fields", {})
            self.field_count = data.get("field_count", {})

    def filter(self, predicates: List[Dict]) -> List[str]:
        doc_ids = list(self.documents.keys())
        for pred in predicates:
            attr = pred['attribute']
            op = pred['operator']
            value = pred['value']
            new_ids = []
            for doc_id in doc_ids:
                val = self.attributes.get(doc_id, {}).get(attr)
                if val is None:
                    val = self.virtual_fields.get(doc_id, {}).get(attr)
                if val is not None:
                    if op == 'eq' and str(val) == str(value):
                        new_ids.append(doc_id)
                    elif op == 'lt' and float(val) < float(value):
                        new_ids.append(doc_id)
                    elif op == 'gt' and float(val) > float(value):
                        new_ids.append(doc_id)
                    elif op == 'le' and float(val) <= float(value):
                        new_ids.append(doc_id)
                    elif op == 'ge' and float(val) >= float(value):
                        new_ids.append(doc_id)
                    elif op == 'ne' and str(val) != str(value):
                        new_ids.append(doc_id)
            doc_ids = new_ids
        return doc_ids

    def get_document(self, doc_id):
        return self.documents.get(doc_id, "")

    def add_virtual_field(self, doc_id, field, value):
        if doc_id not in self.virtual_fields:
            self.virtual_fields[doc_id] = {}
        self.virtual_fields[doc_id][field] = value
        self.field_count[field] = self.field_count.get(field, 0) + 1
        self._persist()

    def promote_virtual_field(self, field):
        if self.field_count.get(field, 0) >= Config.REUSE_THRESHOLD:
            for table in self.schemas.get('row_schemas', {}):
                if field not in self.schemas['row_schemas'][table]:
                    self.schemas['row_schemas'][table].append(field)
            for doc_id, fields in self.virtual_fields.items():
                if field in fields:
                    self.attributes[doc_id][field] = fields[field]
                    del self.virtual_fields[doc_id][field]
            self._persist()
            return True
        return False