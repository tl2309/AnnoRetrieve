import os
import json
from transformers import pipeline
from config import DATA_PATHS, MODEL_CONFIG

class AnnotationExtractor:
    def __init__(self):
        self.gli_ner_pipeline = None
        self.load_models()
    
    def load_models(self):
        """Load required models"""
        # Load GliNER model
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
        """Extract annotations from document based on schema"""
        annotations = {
            'doc_id': doc_id,
            'schema_type': schema['type'],
            'fields': {}
        }
        
        # Extract information for each field
        for field in schema['schema']:
            field_name = field['name'] if isinstance(field, dict) else field
            
            if isinstance(field, dict) and field['type'] == 'object':
                # Process nested object
                annotations['fields'][field_name] = self._extract_object_field(field, document_text)
            else:
                # Process regular field
                extracted_value = self._extract_field_value(field_name, document_text)
                annotations['fields'][field_name] = extracted_value
        
        return annotations
    
    def _extract_object_field(self, field, document_text):
        """Extract nested object fields"""
        object_value = {}
        for prop_name, prop_type in field['properties'].items():
            extracted_value = self._extract_field_value(prop_name, document_text)
            object_value[prop_name] = extracted_value
        return object_value
    
    def _extract_field_value(self, field_name, document_text):
        """Extract value for a single field"""
        # Simple implementation, extracting relevant information from text based on field name
        # More complex NLP techniques like entity recognition and relation extraction should be used in practice
        
        # Use GliNER model for named entity recognition
        if self.gli_ner_pipeline:
            ner_results = self.gli_ner_pipeline(document_text)
            # Simple example: return all recognized entities
            entities = [result['word'] for result in ner_results]
            return entities
        
        # If GliNER model is unavailable, use keyword matching
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
        
        # Simple keyword matching
        if field_name in field_keywords:
            keywords = field_keywords[field_name]
            # Find sentences containing keywords
            sentences = document_text.split('.')
            relevant_sentences = []
            for sentence in sentences:
                if any(keyword in sentence.lower() for keyword in keywords):
                    relevant_sentences.append(sentence.strip())
            return relevant_sentences
        
        # Return empty list by default
        return []
    
    def process_documents(self, schemas, documents):
        """Process all documents and extract annotations"""
        all_annotations = {}
        
        for doc_id, document_text in documents.items():
            # Select the most appropriate schema (simply select the first cluster's schema here)
            best_schema = next(iter(schemas.values()))
            
            # Extract annotations
            annotations = self.extract_annotations(best_schema, document_text, doc_id)
            all_annotations[doc_id] = annotations
        
        # Save annotation results
        self.save_annotations(all_annotations)
        
        return all_annotations
    
    def save_annotations(self, annotations):
        """Save annotation results to file"""
        os.makedirs(DATA_PATHS['annotations'], exist_ok=True)
        
        # Save all annotations
        with open(os.path.join(DATA_PATHS['annotations'], 'all_annotations.json'), 'w', encoding='utf-8') as f:
            json.dump(annotations, f, indent=2, ensure_ascii=False)
        
        # Save individual annotation files by document ID
        for doc_id, annotation in annotations.items():
            with open(os.path.join(DATA_PATHS['annotations'], f'{doc_id}.json'), 'w', encoding='utf-8') as f:
                json.dump(annotation, f, indent=2, ensure_ascii=False)
    
    def load_annotations(self):
        """Load saved annotations"""
        annotations_path = os.path.join(DATA_PATHS['annotations'], 'all_annotations.json')
        if os.path.exists(annotations_path):
            with open(annotations_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
