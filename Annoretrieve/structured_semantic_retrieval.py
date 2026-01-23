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
        """Initialize SQLite database"""
        # Create temporary database for structured queries
        self.db_conn = sqlite3.connect(':memory:')
        self._create_tables()
    
    def _create_tables(self):
        """Create database tables"""
        cursor = self.db_conn.cursor()
        
        # Create main documents table
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
        
        # Create metadata table
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
        """Load annotation data"""
        annotations_path = os.path.join(DATA_PATHS['annotations'], 'all_annotations.json')
        if os.path.exists(annotations_path):
            with open(annotations_path, 'r', encoding='utf-8') as f:
                self.annotations = json.load(f)
        
        # Import annotation data into database
        self._import_annotations_to_db()
        
        return self.annotations
    
    def _import_annotations_to_db(self):
        """Import annotation data into database"""
        cursor = self.db_conn.cursor()
        
        for doc_id, annotation in self.annotations.items():
            fields = annotation['fields']
            
            # Insert into documents table
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
            
            # Insert into metadata table if metadata exists
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
                    len(metadata.get('source', []))  # Simple word count calculation
                ))
        
        self.db_conn.commit()
    
    def parse_query(self, natural_language_query):
        """Parse natural language query into structured query"""
        # Simple example: convert natural language query to SQL query
        # More complex NLP techniques like semantic parsing and intent recognition should be used in practice
        
        # Example query conversion
        query_lower = natural_language_query.lower()
        
        # Simple implementation: build SQL query based on keywords
        sql_query = 'SELECT doc_id FROM documents WHERE 1=1'
        
        # Check for specific keywords
        if 'technical' in query_lower or 'tech' in query_lower:
            sql_query += " AND technical_details != '[]'"
        
        if 'method' in query_lower or 'approach' in query_lower:
            sql_query += " AND methodology != '[]'"
        
        if 'conclusion' in query_lower or 'result' in query_lower:
            sql_query += " AND conclusions != '[]'"
        
        return sql_query
    
    def execute_query(self, sql_query):
        """Execute SQL query"""
        cursor = self.db_conn.cursor()
        cursor.execute(sql_query)
        results = cursor.fetchall()
        return [result[0] for result in results]
    
    def progressive_reasoning(self, query, initial_results):
        """SQL-based progressive reasoning"""
        # Simple implementation: further filter initial results
        # More complex reasoning logic should be implemented in practice
        
        # Example: sort results based on keyword matches in query
        query_lower = query.lower()
        
        # Calculate relevance scores for each result
        relevance_scores = {}
        for doc_id in initial_results:
            if doc_id in self.annotations:
                fields = self.annotations[doc_id]['fields']
                score = 0
                
                # Check if fields contain query keywords
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
        
        # Sort results by relevance score
        sorted_results = sorted(initial_results, key=lambda x: relevance_scores.get(x, 0), reverse=True)
        
        return sorted_results
    
    def extract(self, doc_ids, target_fields):
        """Extract values for specified fields from documents"""
        extracted_data = {}
        
        for doc_id in doc_ids:
            if doc_id in self.annotations:
                fields = self.annotations[doc_id]['fields']
                doc_data = {}
                
                for field_name in target_fields:
                    if field_name in fields:
                        doc_data[field_name] = fields[field_name]
                    else:
                        # Perform extraction if field is not in schema
                        doc_data[field_name] = self._extract_field_from_text(doc_id, field_name)
                
                extracted_data[doc_id] = doc_data
        
        return extracted_data
    
    def _extract_field_from_text(self, doc_id, field_name):
        """Extract value for specified field from document text"""
        # Simple implementation: return empty list, more complex NLP techniques should be used in practice
        return []
    
    def generate_table(self, extracted_data):
        """Generate table based on extracted data"""
        # Simple implementation: return structured data
        # Formatted table output should be generated in practice
        return extracted_data
    
    def retrieve(self, natural_language_query, target_fields=None):
        """Execute full retrieval process"""
        # 1. Parse natural language query into SQL query
        sql_query = self.parse_query(natural_language_query)
        
        # 2. Execute SQL query to get initial results
        initial_results = self.execute_query(sql_query)
        
        # 3. Optimize results with SQL-based progressive reasoning
        optimized_results = self.progressive_reasoning(natural_language_query, initial_results)
        
        # 4. Extract values for target fields if specified
        if target_fields:
            extracted_data = self.extract(optimized_results, target_fields)
            
            # 5. Generate table
            table_data = self.generate_table(extracted_data)
            
            return {
                'query': natural_language_query,
                'sql_query': sql_query,
                'results_count': len(optimized_results),
                'top_results': optimized_results[:10],  # Return top 10 results
                'extracted_data': table_data
            }
        
        return {
            'query': natural_language_query,
            'sql_query': sql_query,
            'results_count': len(optimized_results),
            'top_results': optimized_results[:10]  # Return top 10 results
        }
    
    def close(self):
        """Close database connection"""
        if self.db_conn:
            self.db_conn.close()
