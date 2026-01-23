#!/usr/bin/env python3
"""
Simple evaluation script for AnnoRetrieve system
Focuses on core evaluation metrics and ensures complete output
"""

import os
import sys
import json
import time
from collections import defaultdict

# 添加当前目录到Python路径
sys.path = [os.path.dirname(os.path.abspath(__file__))] + sys.path

from config import DATA_PATHS
from schema_boot import SchemaBoot
from annotation_extractor import AnnotationExtractor
from structured_semantic_retrieval import StructuredSemanticRetrieval


class SimpleEvaluator:
    def __init__(self):
        self.schema_boot = SchemaBoot()
        self.annotation_extractor = AnnotationExtractor()
        self.ssr = StructuredSemanticRetrieval()
    
    def load_documents(self, folder_path, file_extension, max_docs=5):
        """加载指定数量的文档"""
        doc_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) 
                    if f.endswith(file_extension)][:max_docs]
        
        documents = {}
        for doc_path in doc_paths:
            doc_id = os.path.basename(doc_path).split('.')[0]
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    documents[doc_id] = content[:1000]  # 只保留前1000个字符，加快处理速度
            except Exception as e:
                print(f"Failed to load {doc_id}: {e}")
        
        return documents
    
    def evaluate_schema_quality(self, schemas, documents):
        """评估schema质量"""
        results = {}
        for schema_type, schema in schemas.items():
            if isinstance(schema, dict):
                schema_structure = schema['schema']
            else:
                schema_structure = schema
            
            quality = self.schema_boot.evaluate_schema_quality(schema_structure, documents)
            results[schema_type] = quality
        
        return results
    
    def run_evaluation(self):
        """运行简化的评估流程"""
        print("=== Simple AnnoRetrieve Evaluation ===\n")
        
        # 定义要评估的数据集
        datasets = {
            'datalake': {
                'path': DATA_PATHS['datalake'],
                'extension': '.htm',
                'description': 'Main datalake documents'
            },
            'candidate': {
                'path': os.path.join(DATA_PATHS['candidate'], 'candi'),
                'extension': '.txt',
                'description': 'Candidate documents'
            },
            'candidate_key': {
                'path': os.path.join(DATA_PATHS['candidate'], 'key'),
                'extension': '.txt',
                'description': 'Key candidate documents'
            }
        }
        
        # 测试查询
        test_queries = [
            "technical algorithms",
            "natural language processing",
            "university documents"
        ]
        
        # 评估结果汇总
        summary = {}
        
        for dataset_name, dataset_info in datasets.items():
            print(f"--- {dataset_name.upper()} --- {dataset_info['description']}")
            
            # 1. 加载文档
            documents = self.load_documents(dataset_info['path'], dataset_info['extension'])
            print(f"  Loaded {len(documents)} documents")
            
            if not documents:
                print("  No documents found, skipping evaluation\n")
                continue
            
            # 2. 生成Schema
            schemas = self.schema_boot.run_schema_boot(documents, test_queries)
            print(f"  Generated schemas for {len(schemas)} clusters")
            
            # 3. 评估Schema质量
            schema_quality = self.evaluate_schema_quality(schemas, documents)
            
            # 4. 提取标注
            annotations = self.annotation_extractor.process_documents(schemas, documents)
            print(f"  Extracted annotations for {len(annotations)} documents")
            
            # 5. 评估检索性能
            self.ssr.load_annotations()
            retrieval_results = []
            
            for query in test_queries[:2]:  # 只测试前2个查询
                start_time = time.time()
                results = self.ssr.retrieve(query)
                retrieval_time = time.time() - start_time
                
                retrieval_results.append({
                    'query': query,
                    'results_count': results['results_count'],
                    'time': retrieval_time
                })
                
                print(f"  Query '{query}': {results['results_count']} results in {retrieval_time:.4f}s")
            
            # 保存数据集评估结果
            summary[dataset_name] = {
                'document_count': len(documents),
                'schema_quality': schema_quality,
                'annotation_count': len(annotations),
                'retrieval_results': retrieval_results
            }
            
            print()  # 空行分隔
        
        # 生成最终报告
        self.generate_report(summary)
    
    def generate_report(self, summary):
        """生成评估报告"""
        print("=== EVALUATION REPORT ===\n")
        
        for dataset_name, results in summary.items():
            print(f"Dataset: {dataset_name}")
            print(f"Documents: {results['document_count']}")
            
            # Schema质量
            print("Schema Quality:")
            for schema_type, quality in results['schema_quality'].items():
                print(f"  {schema_type}: {quality['quality']:.4f} (Coverage: {quality['coverage']:.4f}, Discrimination: {quality['discrimination']:.4f})")
            
            # 标注结果
            print(f"Annotations: {results['annotation_count']} documents")
            
            # 检索性能
            print("Retrieval Performance:")
            for retrieval in results['retrieval_results']:
                print(f"  Query '{retrieval['query']}': {retrieval['results_count']} results in {retrieval['time']:.4f}s")
            
            print()  # 空行分隔
        
        print("=== EVALUATION COMPLETE ===")


if __name__ == "__main__":
    import sys
    evaluator = SimpleEvaluator()
    evaluator.run_evaluation()
