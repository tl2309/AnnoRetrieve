import os
import json
import sqlite3
from config import DATA_PATHS, SSR_CONFIG

class StructuredSemanticRetrieval:
    def __init__(self):
        self.annotations = {}
        self.db_conn = None
        self._initialize_database()
    
    def _initialize_database(self):
        """初始化SQLite数据库"""
        # 创建临时数据库用于结构化查询
        self.db_conn = sqlite3.connect(':memory:')
        self._create_tables()
    
    def _create_tables(self):
        """创建数据库表"""
        cursor = self.db_conn.cursor()
        
        # 创建主文档表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                doc_id TEXT PRIMARY KEY,
                schema_type TEXT,
                document_type TEXT,
                publish_time TEXT,
                author_organization TEXT,
                topic_category TEXT,
                keywords TEXT,
                entities TEXT,
                technical_details TEXT,
                methodology TEXT,
                conclusions TEXT
            )
        ''')
        
        # 创建元数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metadata (
                doc_id TEXT PRIMARY KEY,
                source TEXT,
                language TEXT,
                word_count INTEGER,
                FOREIGN KEY (doc_id) REFERENCES documents(doc_id)
            )
        ''')
        
        self.db_conn.commit()
    
    def load_annotations(self):
        """加载标注数据"""
        annotations_path = os.path.join(DATA_PATHS['annotations'], 'all_annotations.json')
        if os.path.exists(annotations_path):
            with open(annotations_path, 'r', encoding='utf-8') as f:
                self.annotations = json.load(f)
        
        # 将标注数据导入数据库
        self._import_annotations_to_db()
        
        return self.annotations
    
    def _import_annotations_to_db(self):
        """将标注数据导入数据库"""
        cursor = self.db_conn.cursor()
        
        for doc_id, annotation in self.annotations.items():
            fields = annotation['fields']
            
            # 插入文档表
            cursor.execute('''
                INSERT OR REPLACE INTO documents (
                    doc_id, schema_type, document_type, publish_time, 
                    author_organization, topic_category, keywords, entities, 
                    technical_details, methodology, conclusions
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                doc_id,
                annotation['schema_type'],
                json.dumps(fields.get('document_type', [])),
                json.dumps(fields.get('publish_time', [])),
                json.dumps(fields.get('author_organization', [])),
                json.dumps(fields.get('topic_category', [])),
                json.dumps(fields.get('keywords', [])),
                json.dumps(fields.get('entities', [])),
                json.dumps(fields.get('technical_details', [])),
                json.dumps(fields.get('methodology', [])),
                json.dumps(fields.get('conclusions', []))
            ))
            
            # 插入元数据表
            if 'metadata' in fields:
                metadata = fields['metadata']
                cursor.execute('''
                    INSERT OR REPLACE INTO metadata (
                        doc_id, source, language, word_count
                    ) VALUES (?, ?, ?, ?)
                ''', (
                    doc_id,
                    json.dumps(metadata.get('source', [])),
                    json.dumps(metadata.get('language', [])),
                    len(metadata.get('source', []))  # 简单计算词数
                ))
        
        self.db_conn.commit()
    
    def parse_query(self, natural_language_query):
        """将自然语言查询解析为结构化查询"""
        # 简单示例：将自然语言查询转换为SQL查询
        # 实际应用中应该使用更复杂的NLP技术，如语义解析、意图识别等
        
        # 示例查询转换
        query_lower = natural_language_query.lower()
        
        # 简单实现：根据关键词构建SQL查询
        sql_query = 'SELECT doc_id FROM documents WHERE 1=1'
        
        # 检查是否包含特定关键词
        if 'technical' in query_lower or 'tech' in query_lower:
            sql_query += " AND technical_details != '[]'"
        
        if 'method' in query_lower or 'approach' in query_lower:
            sql_query += " AND methodology != '[]'"
        
        if 'conclusion' in query_lower or 'result' in query_lower:
            sql_query += " AND conclusions != '[]'"
        
        return sql_query
    
    def execute_query(self, sql_query):
        """执行SQL查询"""
        cursor = self.db_conn.cursor()
        cursor.execute(sql_query)
        results = cursor.fetchall()
        return [result[0] for result in results]
    
    def progressive_reasoning(self, query, initial_results):
        """基于SQL的渐进推理"""
        # 简单实现：对初始结果进行进一步筛选
        # 实际应用中应该实现更复杂的推理逻辑
        
        # 示例：根据查询中的关键词对结果进行排序
        query_lower = query.lower()
        
        # 计算每个结果与查询的相关性分数
        relevance_scores = {}
        for doc_id in initial_results:
            if doc_id in self.annotations:
                fields = self.annotations[doc_id]['fields']
                score = 0
                
                # 检查各个字段是否包含查询关键词
                for field_name, field_value in fields.items():
                    if isinstance(field_value, list):
                        for item in field_value:
                            if query_lower in str(item).lower():
                                score += 1
                    elif isinstance(field_value, dict):
                        for sub_field, sub_value in field_value.items():
                            if isinstance(sub_value, list):
                                for item in sub_value:
                                    if query_lower in str(item).lower():
                                        score += 0.5
                
                relevance_scores[doc_id] = score
        
        # 按相关性分数排序
        sorted_results = sorted(initial_results, key=lambda x: relevance_scores.get(x, 0), reverse=True)
        
        return sorted_results
    
    def extract(self, doc_ids, target_fields):
        """从文档中提取指定字段的值"""
        extracted_data = {}
        
        for doc_id in doc_ids:
            if doc_id in self.annotations:
                fields = self.annotations[doc_id]['fields']
                doc_data = {}
                
                for field_name in target_fields:
                    if field_name in fields:
                        doc_data[field_name] = fields[field_name]
                    else:
                        # 如果字段不在schema中，执行提取操作
                        doc_data[field_name] = self._extract_field_from_text(doc_id, field_name)
                
                extracted_data[doc_id] = doc_data
        
        return extracted_data
    
    def _extract_field_from_text(self, doc_id, field_name):
        """从文档文本中提取指定字段的值"""
        # 简单实现：返回空列表，实际应该使用更复杂的NLP技术
        return []
    
    def generate_table(self, extracted_data):
        """根据提取的数据生成表格"""
        # 简单实现：返回结构化数据
        # 实际应用中应该生成格式化的表格输出
        return extracted_data
    
    def retrieve(self, natural_language_query, target_fields=None):
        """执行完整的检索流程"""
        # 1. 解析自然语言查询为SQL查询
        sql_query = self.parse_query(natural_language_query)
        
        # 2. 执行SQL查询获取初始结果
        initial_results = self.execute_query(sql_query)
        
        # 3. 基于SQL的渐进推理，优化结果
        optimized_results = self.progressive_reasoning(natural_language_query, initial_results)
        
        # 4. 提取目标字段的值
        if target_fields:
            extracted_data = self.extract(optimized_results, target_fields)
            
            # 5. 生成表格
            table_data = self.generate_table(extracted_data)
            
            return {
                'query': natural_language_query,
                'sql_query': sql_query,
                'results_count': len(optimized_results),
                'top_results': optimized_results[:10],  # 返回前10个结果
                'extracted_data': table_data
            }
        
        return {
            'query': natural_language_query,
            'sql_query': sql_query,
            'results_count': len(optimized_results),
            'top_results': optimized_results[:10]  # 返回前10个结果
        }
    
    def close(self):
        """关闭数据库连接"""
        if self.db_conn:
            self.db_conn.close()
