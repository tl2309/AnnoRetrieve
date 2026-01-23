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
        """加载文档内容"""
        documents = {}
        for doc_path in document_paths:
            doc_id = os.path.basename(doc_path).split('.')[0]
            with open(doc_path, 'r', encoding='utf-8') as f:
                documents[doc_id] = f.read()
        return documents
    
    def cluster_documents(self, documents, n_clusters=5):
        """将文档聚类"""
        # 简单的聚类实现，实际应用中可以使用更复杂的算法
        doc_ids = list(documents.keys())
        n_clusters = min(n_clusters, len(doc_ids))
        
        # 这里使用随机聚类作为示例，实际应该使用基于内容的聚类
        clusters = defaultdict(list)
        for i, doc_id in enumerate(doc_ids):
            cluster_id = i % n_clusters
            clusters[cluster_id].append(doc_id)
        
        self.document_clusters = clusters
        return clusters
    
    def extract_frequent_patterns(self, cluster_docs, documents, min_support=0.3):
        """使用FP-Growth算法提取频繁模式"""
        # 简单实现，提取文档中的关键词作为频繁项
        all_terms = []
        for doc_id in cluster_docs:
            text = documents[doc_id]
            # 简单分词，实际应用中应该使用更复杂的NLP处理
            terms = set(text.lower().split())
            all_terms.append(list(terms))
        
        # 使用FP-Growth算法提取频繁项集
        frequent_patterns = []
        for itemsets in find_frequent_itemsets(all_terms, min_support * len(cluster_docs)):
            frequent_patterns.append(itemsets)
        
        return frequent_patterns
    
    def build_concept_hierarchy(self, terms):
        """构建概念层次"""
        # 简单实现，实际应用中应该结合WordNet和领域词典
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
            # 简单分类，实际应该使用更复杂的语义分析
            if any(keyword in term for keyword in ['tech', 'algorithm', 'model']):
                concept_hierarchy['root']['children']['technical']['children'][term] = {}
            elif any(keyword in term for keyword in ['method', 'approach', 'framework']):
                concept_hierarchy['root']['children']['methodological']['children'][term] = {}
            else:
                concept_hierarchy['root']['children']['results']['children'][term] = {}
        
        return concept_hierarchy
    
    def generate_schema_versions(self, cluster_id, frequent_patterns, concept_hierarchy):
        """生成多版本schema"""
        # 提取候选字段
        candidate_fields = set()
        for pattern in frequent_patterns:
            for item in pattern:
                if len(item) > 3:  # 过滤短词
                    candidate_fields.add(item)
        
        candidate_fields = list(candidate_fields)[:20]  # 最多20个候选字段
        
        # 获取三层结构的基础字段
        layers = self.config['layers']
        base_fields = layers['fast_filter'] + layers['semantic_match'] + layers['fine_grained']
        
        # 生成多版本schema
        schemas = {
            'lite': [],
            'standard': [],
            'full': []
        }
        
        # 精简版：核心字段
        schemas['lite'] = base_fields[:self.config['schema_versions']['lite']['max_fields']]
        
        # 标准版：8-12个字段
        standard_fields = base_fields + candidate_fields[:8]
        schemas['standard'] = standard_fields[:self.config['schema_versions']['standard']['max_fields']]
        
        # 完整版：15-20个字段，含嵌套结构
        full_fields = base_fields + candidate_fields
        schemas['full'] = full_fields[:self.config['schema_versions']['full']['max_fields']]
        
        # 添加嵌套结构示例
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
        """评估模式质量"""
        # 计算覆盖度 (Coverage)
        coverage = self._calculate_coverage(schema, documents)
        
        # 计算区分度 (Discrimination)
        discrimination = self._calculate_discrimination(schema, documents)
        
        # 计算一致性 (Consistency)
        consistency = self._calculate_consistency(schema, documents)
        
        # 计算查询匹配度 (QueryMatch)
        query_match = self._calculate_query_match(schema, queries) if queries else 0.5
        
        # 计算综合质量分数
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
        """计算schema覆盖的文档比例"""
        # 简单实现，实际应该基于字段是否能从文档中提取
        return min(1.0, len(schema) / 20.0)  # 假设最多20个字段
    
    def _calculate_discrimination(self, schema, documents):
        """计算schema的区分能力"""
        # 简单实现，基于字段数量和多样性
        return min(1.0, len(schema) / 15.0)
    
    def _calculate_consistency(self, schema, documents):
        """计算schema的一致性"""
        # 简单实现，假设schema结构越规则一致性越高
        return 0.8  # 示例值
    
    def _calculate_query_match(self, schema, queries):
        """计算schema与查询的匹配度"""
        if not queries:
            return 0.5
        
        # 简单实现，计算查询词与schema字段的重叠度
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
        """使用多目标优化选择最优schema"""
        # 简单实现，选择质量最高的schema
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
        """运行SchemaBoot算法"""
        # 1. 文档聚类
        clusters = self.cluster_documents(documents)
        
        # 2. 对每个聚类生成schema
        all_schemas = {}
        for cluster_id, cluster_docs in clusters.items():
            # 提取频繁模式
            frequent_patterns = self.extract_frequent_patterns(cluster_docs, documents)
            
            # 构建概念层次
            terms = [item for pattern in frequent_patterns for item in pattern]
            concept_hierarchy = self.build_concept_hierarchy(terms)
            
            # 生成多版本schema
            schemas = self.generate_schema_versions(cluster_id, frequent_patterns, concept_hierarchy)
            
            # 优化选择最优schema
            best_schema = self.optimize_schema(schemas, documents, queries)
            all_schemas[cluster_id] = best_schema
        
        # 保存生成的schema
        self.save_schemas(all_schemas)
        
        return all_schemas
    
    def save_schemas(self, schemas):
        """保存生成的schema到文件"""
        os.makedirs(DATA_PATHS['schemas'], exist_ok=True)
        with open(os.path.join(DATA_PATHS['schemas'], 'generated_schemas.json'), 'w', encoding='utf-8') as f:
            json.dump(schemas, f, indent=2, ensure_ascii=False)
    
    def load_schemas(self):
        """从文件加载schema"""
        schema_path = os.path.join(DATA_PATHS['schemas'], 'generated_schemas.json')
        if os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8') as f:
                self.schemas = json.load(f)
            return self.schemas
        return None
