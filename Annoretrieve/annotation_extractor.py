import os
import json
from transformers import pipeline
from config import DATA_PATHS, MODEL_CONFIG

class AnnotationExtractor:
    def __init__(self):
        self.gli_ner_pipeline = None
        self.load_models()
    
    def load_models(self):
        """加载所需的模型"""
        # 加载GliNER模型
        try:
            self.gli_ner_pipeline = pipeline(
                "ner",
                model=MODEL_CONFIG['gli_ner_model'],
                tokenizer=MODEL_CONFIG['gli_ner_model']
            )
        except Exception as e:
            print(f"Failed to load GliNER model: {e}")
            self.gli_ner_pipeline = None
    
    def extract_annotations(self, schema, document_text, doc_id):
        """根据schema从文档中提取标注"""
        annotations = {
            'doc_id': doc_id,
            'schema_type': schema['type'],
            'fields': {}
        }
        
        # 提取每个字段的信息
        for field in schema['schema']:
            field_name = field['name'] if isinstance(field, dict) else field
            
            if isinstance(field, dict) and field['type'] == 'object':
                # 处理嵌套对象
                annotations['fields'][field_name] = self._extract_object_field(field, document_text)
            else:
                # 处理普通字段
                extracted_value = self._extract_field_value(field_name, document_text)
                annotations['fields'][field_name] = extracted_value
        
        return annotations
    
    def _extract_object_field(self, field, document_text):
        """提取嵌套对象字段"""
        object_value = {}
        for prop_name, prop_type in field['properties'].items():
            extracted_value = self._extract_field_value(prop_name, document_text)
            object_value[prop_name] = extracted_value
        return object_value
    
    def _extract_field_value(self, field_name, document_text):
        """提取单个字段的值"""
        # 简单实现，根据字段名从文本中提取相关信息
        # 实际应用中应该使用更复杂的NLP技术，如实体识别、关系抽取等
        
        # 使用GliNER模型进行命名实体识别
        if self.gli_ner_pipeline:
            ner_results = self.gli_ner_pipeline(document_text)
            # 简单示例：返回所有识别到的实体
            entities = [result['word'] for result in ner_results]
            return entities
        
        # 如果GliNER模型不可用，使用关键词匹配
        field_keywords = {
            'document_type': ['report', 'paper', 'article', 'document'],
            'publish_time': ['date', 'time', 'published', 'released'],
            'author_organization': ['author', 'organization', 'institution', 'university'],
            'topic_category': ['topic', 'category', 'subject', 'theme'],
            'keywords': ['keywords', 'key terms', 'tags', 'terms'],
            'entities': ['entity', 'person', 'organization', 'location'],
            'technical_details': ['technical', 'details', 'specifications', 'implementation'],
            'methodology': ['method', 'methodology', 'approach', 'technique'],
            'conclusions': ['conclusion', 'results', 'findings', 'summary']
        }
        
        # 简单关键词匹配
        if field_name in field_keywords:
            keywords = field_keywords[field_name]
            # 查找包含关键词的句子
            sentences = document_text.split('.')
            relevant_sentences = []
            for sentence in sentences:
                if any(keyword in sentence.lower() for keyword in keywords):
                    relevant_sentences.append(sentence.strip())
            return relevant_sentences
        
        # 默认返回空列表
        return []
    
    def process_documents(self, schemas, documents):
        """处理所有文档，提取标注"""
        all_annotations = {}
        
        for doc_id, document_text in documents.items():
            # 选择最合适的schema（这里简单选择第一个聚类的schema）
            best_schema = next(iter(schemas.values()))
            
            # 提取标注
            annotations = self.extract_annotations(best_schema, document_text, doc_id)
            all_annotations[doc_id] = annotations
        
        # 保存标注结果
        self.save_annotations(all_annotations)
        
        return all_annotations
    
    def save_annotations(self, annotations):
        """保存标注结果到文件"""
        os.makedirs(DATA_PATHS['annotations'], exist_ok=True)
        
        # 保存所有标注
        with open(os.path.join(DATA_PATHS['annotations'], 'all_annotations.json'), 'w', encoding='utf-8') as f:
            json.dump(annotations, f, indent=2, ensure_ascii=False)
        
        # 按文档ID保存单独的标注文件
        for doc_id, annotation in annotations.items():
            with open(os.path.join(DATA_PATHS['annotations'], f'{doc_id}.json'), 'w', encoding='utf-8') as f:
                json.dump(annotation, f, indent=2, ensure_ascii=False)
    
    def load_annotations(self):
        """加载已保存的标注"""
        annotations_path = os.path.join(DATA_PATHS['annotations'], 'all_annotations.json')
        if os.path.exists(annotations_path):
            with open(annotations_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
