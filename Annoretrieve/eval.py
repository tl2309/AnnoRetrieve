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
        """加载指定数据集"""
        print(f"Loading dataset: {dataset_name}")
        
        if dataset_name == 'datalake':
            # 加载datalake数据
            data_path = DATA_PATHS['datalake']
            doc_paths = [os.path.join(data_path, f) for f in os.listdir(data_path) if f.endswith('.htm')]
            
        elif dataset_name == 'candidate':
            # 加载candidate数据
            data_path = os.path.join(DATA_PATHS['candidate'], 'candi')
            doc_paths = [os.path.join(data_path, f) for f in os.listdir(data_path) if f.endswith('.txt')]
            
        elif dataset_name == 'candidate_key':
            # 加载candidate/key数据
            data_path = os.path.join(DATA_PATHS['candidate'], 'key')
            doc_paths = [os.path.join(data_path, f) for f in os.listdir(data_path) if f.endswith('.txt')]
            
        else:
            raise ValueError(f"Unknown dataset: {dataset_name}")
        
        # 读取文档内容
        documents = {}
        for doc_path in doc_paths[:10]:  # 限制加载10个文档，避免资源占用过大
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
        """评估schema质量"""
        print(f"\nEvaluating schema quality for {dataset_name}...")
        
        schema_quality_results = {}
        for schema_type, schema in schemas.items():
            # 提取schema结构
            if isinstance(schema, dict):
                schema_structure = schema['schema']
            else:
                schema_structure = schema
            
            # 评估schema质量
            quality = self.schema_boot.evaluate_schema_quality(schema_structure, documents)
            schema_quality_results[schema_type] = quality
            
            print(f"  {schema_type} schema quality: {quality['quality']:.4f}")
            print(f"    Coverage: {quality['coverage']:.4f}, Discrimination: {quality['discrimination']:.4f}")
            print(f"    Consistency: {quality['consistency']:.4f}, QueryMatch: {quality['query_match']:.4f}")
        
        return schema_quality_results
    
    def evaluate_annotation_extraction(self, schemas, documents, dataset_name):
        """评估标注提取质量"""
        print(f"\nEvaluating annotation extraction for {dataset_name}...")
        
        # 选择一个schema进行评估
        selected_schema = next(iter(schemas.values()))
        
        # 提取标注
        start_time = time.time()
        annotations = self.annotation_extractor.process_documents(schemas, documents)
        extraction_time = time.time() - start_time
        
        # 计算标注覆盖率
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
        """评估检索性能"""
        print(f"\nEvaluating retrieval performance for {dataset_name}...")
        
        retrieval_results = {}
        
        for query in queries:
            # 执行检索
            start_time = time.time()
            results = self.ssr.retrieve(query, ['document_type', 'technical_details', 'methodology'])
            retrieval_time = time.time() - start_time
            
            # 简单评估：结果数量和检索时间
            retrieval_results[query] = {
                'result_count': results['results_count'],
                'retrieval_time': retrieval_time,
                'top_results': results['top_results'][:3]  # 只保存前3个结果
            }
            
            print(f"  Query: '{query}'")
            print(f"    Results: {results['results_count']}, Time: {retrieval_time:.4f} seconds")
            print(f"    Top results: {results['top_results'][:3]}")
        
        return retrieval_results
    
    def run_full_evaluation(self, datasets, queries):
        """运行完整的评估流程"""
        print("=== AnnoRetrieve Evaluation ===")
        
        for dataset_name in datasets:
            print(f"\n\n--- Evaluating Dataset: {dataset_name} ---")
            
            # 1. 加载数据集
            documents = self.load_dataset(dataset_name)
            
            if not documents:
                print(f"No documents found in {dataset_name}, skipping evaluation")
                continue
            
            # 2. 运行SchemaBoot生成schemas
            schemas = self.schema_boot.run_schema_boot(documents, queries)
            
            # 3. 评估schema质量
            schema_quality = self.evaluate_schema_quality(schemas, documents, dataset_name)
            
            # 4. 评估标注提取
            annotation_quality = self.evaluate_annotation_extraction(schemas, documents, dataset_name)
            
            # 5. 评估检索性能
            self.ssr.load_annotations()  # 确保已加载标注数据
            retrieval_quality = self.evaluate_retrieval(queries, dataset_name)
            
            # 保存评估结果
            self.results[dataset_name] = {
                'document_count': len(documents),
                'schema_quality': schema_quality,
                'annotation_quality': annotation_quality,
                'retrieval_quality': retrieval_quality
            }
        
        # 保存所有评估结果到文件
        self.save_results()
        
        # 生成评估报告
        self.generate_report()
    
    def save_results(self):
        """保存评估结果到文件"""
        results_path = os.path.join(os.path.dirname(__file__), 'evaluation_results.json')
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\n\nEvaluation results saved to {results_path}")
    
    def generate_report(self):
        """生成评估报告"""
        print("\n\n=== AnnoRetrieve Evaluation Report ===")
        
        for dataset_name, dataset_results in self.results.items():
            print(f"\nDataset: {dataset_name}")
            print(f"  Documents: {dataset_results['document_count']}")
            
            # Schema质量摘要
            schema_quality = dataset_results['schema_quality']
            best_schema = max(schema_quality.items(), key=lambda x: x[1]['quality'])
            print(f"  Best Schema: {best_schema[0]} (Quality: {best_schema[1]['quality']:.4f})")
            
            # 标注提取摘要
            annotation_quality = dataset_results['annotation_quality']
            print(f"  Annotation Coverage: {annotation_quality['coverage_rate']:.4f}")
            print(f"  Avg Annotation Time: {annotation_quality['avg_time_per_doc']:.4f}s")
            
            # 检索性能摘要
            retrieval_quality = dataset_results['retrieval_quality']
            avg_result_count = np.mean([r['result_count'] for r in retrieval_quality.values()])
            avg_retrieval_time = np.mean([r['retrieval_time'] for r in retrieval_quality.values()])
            print(f"  Avg Retrieval Results: {avg_result_count:.2f}")
            print(f"  Avg Retrieval Time: {avg_retrieval_time:.4f}s")
        
        print("\n=== Evaluation Complete ===")


if __name__ == "__main__":
    # 定义要评估的数据集
    datasets_to_evaluate = ['datalake', 'candidate', 'candidate_key']
    
    # 定义测试查询
    test_queries = [
        "Find documents with technical details about algorithms",
        "Find papers about natural language processing",
        "Find documents published by universities"
    ]
    
    # 创建评估器并运行评估
    evaluator = AnnoRetrieveEvaluator()
    evaluator.run_full_evaluation(datasets_to_evaluate, test_queries)
