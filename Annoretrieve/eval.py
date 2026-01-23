#!/usr/bin/env python3
"""
Evaluation module for AnnoRetrieve system
"""

import os
import json
import time
import numpy as np
from config import SCHEMA_CONFIG, DATA_PATHS
from schema_boot import SchemaBoot
from annotation_extractor import AnnotationExtractor
from structured_semantic_retrieval import StructuredSemanticRetrieval


class AnnoRetrieveEvaluator:
    def __init__(self):
        self.schema_boot = SchemaBoot()
        self.annotation_extractor = AnnotationExtractor()
        self.ssr = StructuredSemanticRetrieval()
        self.results = {}
    
    def load_dataset(self, dataset_name):
        """Load specified dataset"""
        print(f"Loading dataset: {dataset_name}")
        
        if dataset_name == 'datalake':
            # Load datalake data
            data_path = DATA_PATHS['datalake']
            doc_paths = [os.path.join(data_path, f) for f in os.listdir(data_path) if f.endswith('.htm')]
            
        elif dataset_name == 'candidate':
            # Load candidate data
            data_path = os.path.join(DATA_PATHS['candidate'], 'candi')
            doc_paths = [os.path.join(data_path, f) for f in os.listdir(data_path) if f.endswith('.txt')]
            
        elif dataset_name == 'candidate_key':
            # Load candidate/key data
            data_path = os.path.join(DATA_PATHS['candidate'], 'key')
            doc_paths = [os.path.join(data_path, f) for f in os.listdir(data_path) if f.endswith('.txt')]
            
        else:
            raise ValueError(f"Unknown dataset: {dataset_name}")
        
        # Read document contents
        documents = {}
        for doc_path in doc_paths[:10]:  # Limit to 10 documents to avoid excessive resource usage
            doc_id = os.path.basename(doc_path).split('.')[0]
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    documents[doc_id] = content
            except Exception as e:
                print(f"Failed to load document {doc_id}: {e}")
        
        print(f"Loaded {len(documents)} documents from {dataset_name}")
        return documents
    
    def evaluate_schema_quality(self, schemas, documents, dataset_name):
        """Evaluate schema quality"""
        print(f"\nEvaluating schema quality for {dataset_name}...")
        
        schema_quality_results = {}
        for schema_type, schema in schemas.items():
            # Extract schema structure
            if isinstance(schema, dict):
                schema_structure = schema['schema']
            else:
                schema_structure = schema
            
            # Evaluate schema quality
            quality = self.schema_boot.evaluate_schema_quality(schema_structure, documents)
            schema_quality_results[schema_type] = quality
            
            print(f"  {schema_type} schema quality: {quality['quality']:.4f}")
            print(f"    Coverage: {quality['coverage']:.4f}, Discrimination: {quality['discrimination']:.4f}")
            print(f"    Consistency: {quality['consistency']:.4f}, QueryMatch: {quality['query_match']:.4f}")
        
        return schema_quality_results
    
    def evaluate_annotation_extraction(self, schemas, documents, dataset_name):
        """Evaluate annotation extraction quality"""
        print(f"\nEvaluating annotation extraction for {dataset_name}...")
        
        # Select a schema for evaluation
        selected_schema = next(iter(schemas.values()))
        
        # Extract annotations
        start_time = time.time()
        annotations = self.annotation_extractor.process_documents(schemas, documents)
        extraction_time = time.time() - start_time
        
        # Calculate annotation coverage rate
        coverage_count = 0
        total_fields = 0
        
        for doc_id, annotation in annotations.items():
            fields = annotation['fields']
            total_fields += len(fields)
            
            for field_name, field_value in fields.items():
                if field_value:
                    coverage_count += 1
        
        coverage_rate = coverage_count / total_fields if total_fields > 0 else 0
        avg_time_per_doc = extraction_time / len(documents) if documents else 0
        
        print(f"  Extracted annotations for {len(annotations)} documents")
        print(f"  Annotation coverage rate: {coverage_rate:.4f}")
        print(f"  Total extraction time: {extraction_time:.4f} seconds")
        print(f"  Average time per document: {avg_time_per_doc:.4f} seconds")
        
        return {
            'annotation_count': len(annotations),
            'coverage_rate': coverage_rate,
            'extraction_time': extraction_time,
            'avg_time_per_doc': avg_time_per_doc
        }
    
    def evaluate_retrieval(self, queries, dataset_name):
        """Evaluate retrieval performance"""
        print(f"\nEvaluating retrieval performance for {dataset_name}...")
        
        retrieval_results = {}
        
        for query in queries:
            # Execute retrieval
            start_time = time.time()
            results = self.ssr.retrieve(query, ['document_type', 'technical_details', 'methodology'])
            retrieval_time = time.time() - start_time
            
            # Simple evaluation: result count and retrieval time
            retrieval_results[query] = {
                'result_count': results['results_count'],
                'retrieval_time': retrieval_time,
                'top_results': results['top_results'][:3]  # Save only top 3 results
            }
            
            print(f"  Query: '{query}'")
            print(f"    Results: {results['results_count']}, Time: {retrieval_time:.4f} seconds")
            print(f"    Top results: {results['top_results'][:3]}")
        
        return retrieval_results
    
    def run_full_evaluation(self, datasets, queries):
        """Run full evaluation process"""
        print("=== AnnoRetrieve Evaluation ===")
        
        for dataset_name in datasets:
            print(f"\n\n--- Evaluating Dataset: {dataset_name} ---")
            
            # 1. Load dataset
            documents = self.load_dataset(dataset_name)
            
            if not documents:
                print(f"No documents found in {dataset_name}, skipping evaluation")
                continue
            
            # 2. Run SchemaBoot to generate schemas
            schemas = self.schema_boot.run_schema_boot(documents, queries)
            
            # 3. Evaluate schema quality
            schema_quality = self.evaluate_schema_quality(schemas, documents, dataset_name)
            
            # 4. Evaluate annotation extraction
            annotation_quality = self.evaluate_annotation_extraction(schemas, documents, dataset_name)
            
            # 5. Evaluate retrieval performance
            self.ssr.load_annotations()  # Ensure annotation data is loaded
            retrieval_quality = self.evaluate_retrieval(queries, dataset_name)
            
            # Save evaluation results
            self.results[dataset_name] = {
                'document_count': len(documents),
                'schema_quality': schema_quality,
                'annotation_quality': annotation_quality,
                'retrieval_quality': retrieval_quality
            }
        
        # Save all evaluation results to file
        self.save_results()
        
        # Generate evaluation report
        self.generate_report()
    
    def save_results(self):
        """Save evaluation results to file"""
        results_path = os.path.join(os.path.dirname(__file__), 'evaluation_results.json')
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\n\nEvaluation results saved to {results_path}")
    
    def generate_report(self):
        """Generate evaluation report"""
        print("\n\n=== AnnoRetrieve Evaluation Report ===")
        
        for dataset_name, dataset_results in self.results.items():
            print(f"\nDataset: {dataset_name}")
            print(f"  Documents: {dataset_results['document_count']}")
            
            # Schema quality summary
            schema_quality = dataset_results['schema_quality']
            best_schema = max(schema_quality.items(), key=lambda x: x[1]['quality'])
            print(f"  Best Schema: {best_schema[0]} (Quality: {best_schema[1]['quality']:.4f})")
            
            # Annotation extraction summary
            annotation_quality = dataset_results['annotation_quality']
            print(f"  Annotation Coverage: {annotation_quality['coverage_rate']:.4f}")
            print(f"  Avg Annotation Time: {annotation_quality['avg_time_per_doc']:.4f}s")
            
            # Retrieval performance summary
            retrieval_quality = dataset_results['retrieval_quality']
            avg_result_count = np.mean([r['result_count'] for r in retrieval_quality.values()])
            avg_retrieval_time = np.mean([r['retrieval_time'] for r in retrieval_quality.values()])
            print(f"  Avg Retrieval Results: {avg_result_count:.2f}")
            print(f"  Avg Retrieval Time: {avg_retrieval_time:.4f}s")
        
        print("\n=== Evaluation Complete ===")


if __name__ == "__main__":
    # Define datasets to evaluate
    datasets_to_evaluate = ['datalake', 'candidate', 'candidate_key']
    
    # Define test queries
    test_queries = [
        "Find documents with technical details about algorithms",
        "Find papers about natural language processing",
        "Find documents published by universities"
    ]
    
    # Create evaluator and run evaluation
    evaluator = AnnoRetrieveEvaluator()
    evaluator.run_full_evaluation(datasets_to_evaluate, test_queries)
