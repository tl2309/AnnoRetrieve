import os
import json
import numpy as np
from collections import defaultdict, Counter
from sklearn.cluster import KMeans
from sklearn.metrics import mutual_info_score
from fp_growth_impl import find_frequent_itemsets
from config import SCHEMA_CONFIG, DATA_PATHS

class SchemaBoot:
    def __init__(self):
        self.config = SCHEMA_CONFIG
        self.schemas = {}
        self.document_clusters = {}
        
    def load_documents(self, document_paths):
        """Load document content"""
        documents = {}
        for doc_path in document_paths:
            doc_id = os.path.basename(doc_path).split('.')[0]
            with open(doc_path, 'r', encoding='utf-8') as f:
                documents[doc_id] = f.read()
        return documents
    
    def cluster_documents(self, documents, n_clusters=5):
        """Cluster documents"""
        # Simple clustering implementation, more complex algorithms can be used in practical applications
        doc_ids = list(documents.keys())
        n_clusters = min(n_clusters, len(doc_ids))
        
        # Random clustering is used here as an example, content-based clustering should be used in practice
        clusters = defaultdict(list)
        for i, doc_id in enumerate(doc_ids):
            cluster_id = i % n_clusters
            clusters[cluster_id].append(doc_id)
        
        self.document_clusters = clusters
        return clusters
    
    def extract_frequent_patterns(self, cluster_docs, documents, min_support=0.3):
        """Extract frequent patterns using FP-Growth algorithm"""
        # Simple implementation, extracting keywords from documents as frequent items
        all_terms = []
        for doc_id in cluster_docs:
            text = documents[doc_id]
            # Simple tokenization, more complex NLP processing should be used in practice
            terms = set(text.lower().split())
            all_terms.append(list(terms))
        
        # Extract frequent itemsets using FP-Growth algorithm
        frequent_patterns = []
        for itemsets in find_frequent_itemsets(all_terms, min_support * len(cluster_docs)):
            frequent_patterns.append(itemsets)
        
        return frequent_patterns
    
    def build_concept_hierarchy(self, terms):
        """Build concept hierarchy"""
        # Simple implementation, should combine WordNet and domain dictionaries in practice
        concept_hierarchy = {
            'root': {
                'children': {
                    'technical': {'children': {}},
                    'methodological': {'children': {}},
                    'results': {'children': {}}
                }
            }
        }
        
        for term in terms:
            # Simple classification, more complex semantic analysis should be used in practice
            if any(keyword in term for keyword in ['tech', 'algorithm', 'model']):
                concept_hierarchy['root']['children']['technical']['children'][term] = {}
            elif any(keyword in term for keyword in ['method', 'approach', 'framework']):
                concept_hierarchy['root']['children']['methodological']['children'][term] = {}
            else:
                concept_hierarchy['root']['children']['results']['children'][term] = {}
        
        return concept_hierarchy
    
    def generate_schema_versions(self, cluster_id, frequent_patterns, concept_hierarchy):
        """Generate multi-version schemas"""
        # Extract candidate fields
        candidate_fields = set()
        for pattern in frequent_patterns:
            for item in pattern:
                if len(item) > 3:  # Filter short words
                    candidate_fields.add(item)
        
        candidate_fields = list(candidate_fields)[:20]  # Maximum 20 candidate fields
        
        # Get base fields for three-layer structure
        layers = self.config['layers']
        base_fields = layers['fast_filter'] + layers['semantic_match'] + layers['fine_grained']
        
        # Generate multi-version schemas
        schemas = {
            'lite': [],
            'standard': [],
            'full': []
        }
        
        # Lite version: core fields
        schemas['lite'] = base_fields[:self.config['schema_versions']['lite']['max_fields']]
        
        # Standard version: 8-12 fields
        standard_fields = base_fields + candidate_fields[:8]
        schemas['standard'] = standard_fields[:self.config['schema_versions']['standard']['max_fields']]
        
        # Full version: 15-20 fields, including nested structures
        full_fields = base_fields + candidate_fields
        schemas['full'] = full_fields[:self.config['schema_versions']['full']['max_fields']]
        
        # Add nested structure example
        schemas['full'].append({
            'name': 'metadata',
            'type': 'object',
            'properties': {
                'source': 'string',
                'language': 'string',
                'word_count': 'integer'
            }
        })
        
        return schemas
    
    def evaluate_schema_quality(self, schema, documents, queries=None):
        """Evaluate schema quality"""
        # Calculate coverage (Coverage)
        coverage = self._calculate_coverage(schema, documents)
        
        # Calculate discrimination (Discrimination)
        discrimination = self._calculate_discrimination(schema, documents)
        
        # Calculate consistency (Consistency)
        consistency = self._calculate_consistency(schema, documents)
        
        # Calculate query match (QueryMatch)
        query_match = self._calculate_query_match(schema, queries) if queries else 0.5
        
        # Calculate comprehensive quality score
        weights = self.config['quality_weights']
        quality = (
            weights['alpha'] * coverage +
            weights['beta'] * discrimination +
            weights['gamma'] * consistency +
            weights['delta'] * query_match
        )
        
        return {
            'coverage': coverage,
            'discrimination': discrimination,
            'consistency': consistency,
            'query_match': query_match,
            'quality': quality
        }
    
    def _calculate_coverage(self, schema, documents):
        """Calculate the proportion of documents covered by schema"""
        # Simple implementation, should be based on whether fields can be extracted from documents in practice
        return min(1.0, len(schema) / 20.0)  # Assuming maximum 20 fields
    
    def _calculate_discrimination(self, schema, documents):
        """Calculate the discrimination ability of schema"""
        # Simple implementation, based on field count and diversity
        return min(1.0, len(schema) / 15.0)
    
    def _calculate_consistency(self, schema, documents):
        """Calculate the consistency of schema"""
        # Simple implementation, assuming more regular schema structure means higher consistency
        return 0.8  # Example value
    
    def _calculate_query_match(self, schema, queries):
        """Calculate the match degree between schema and queries"""
        if not queries:
            return 0.5
        
        # Simple implementation, calculate the overlap between query terms and schema fields
        schema_terms = set()
        for field in schema:
            if isinstance(field, dict):
                schema_terms.add(field['name'])
            else:
                schema_terms.add(field)
        
        match_count = 0
        for query in queries:
            query_terms = set(query.lower().split())
            if schema_terms.intersection(query_terms):
                match_count += 1
        
        return match_count / len(queries)
    
    def optimize_schema(self, candidate_schemas, documents, queries=None):
        """Select optimal schema using multi-objective optimization"""
        # Simple implementation, select the schema with the highest quality
        best_schema = None
        best_score = 0
        
        for schema_type, schema in candidate_schemas.items():
            quality = self.evaluate_schema_quality(schema, documents, queries)
            if quality['quality'] > best_score:
                best_score = quality['quality']
                best_schema = {
                    'type': schema_type,
                    'schema': schema,
                    'quality': quality
                }
        
        return best_schema
    
    def run_schema_boot(self, documents, queries=None):
        """Run SchemaBoot algorithm"""
        # 1. Document clustering
        clusters = self.cluster_documents(documents)
        
        # 2. Generate schemas for each cluster
        all_schemas = {}
        for cluster_id, cluster_docs in clusters.items():
            # Extract frequent patterns
            frequent_patterns = self.extract_frequent_patterns(cluster_docs, documents)
            
            # Build concept hierarchy
            terms = [item for pattern in frequent_patterns for item in pattern]
            concept_hierarchy = self.build_concept_hierarchy(terms)
            
            # Generate multi-version schemas
            schemas = self.generate_schema_versions(cluster_id, frequent_patterns, concept_hierarchy)
            
            # Optimize and select the best schema
            best_schema = self.optimize_schema(schemas, documents, queries)
            all_schemas[cluster_id] = best_schema
        
        # Save generated schemas
        self.save_schemas(all_schemas)
        
        return all_schemas
    
    def save_schemas(self, schemas):
        """Save generated schemas to file"""
        os.makedirs(DATA_PATHS['schemas'], exist_ok=True)
        with open(os.path.join(DATA_PATHS['schemas'], 'generated_schemas.json'), 'w', encoding='utf-8') as f:
            json.dump(schemas, f, indent=2, ensure_ascii=False)
    
    def load_schemas(self):
        """Load schemas from file"""
        schema_path = os.path.join(DATA_PATHS['schemas'], 'generated_schemas.json')
        if os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8') as f:
                self.schemas = json.load(f)
            return self.schemas
        return None
