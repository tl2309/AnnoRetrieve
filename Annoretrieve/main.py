import os
import glob
from config import DATA_PATHS
from schema_boot import SchemaBoot
from annotation_extractor import AnnotationExtractor
from structured_semantic_retrieval import StructuredSemanticRetrieval

class AnnoRetrieveSystem:
    def __init__(self):
        self.schema_boot = SchemaBoot()
        self.annotation_extractor = AnnotationExtractor()
        self.ssr = StructuredSemanticRetrieval()
        self.documents = {}
    
    def load_documents(self, max_docs=100):
        """Load document data"""
        print(f"Loading documents from {DATA_PATHS['datalake']}...")
        
        # Get all HTML document paths
        doc_paths = glob.glob(os.path.join(DATA_PATHS['datalake'], '*.htm'))
        
        # Limit the number of documents loaded
        doc_paths = doc_paths[:max_docs]
        
        for doc_path in doc_paths:
            doc_id = os.path.basename(doc_path).split('.')[0]
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.documents[doc_id] = content
            except Exception as e:
                print(f"Failed to load document {doc_id}: {e}")
        
        print(f"Loaded {len(self.documents)} documents.")
        return self.documents
    
    def generate_schemas(self, queries=None):
        """Run SchemaBoot to generate document annotation schemas"""
        print("Running SchemaBoot to generate schemas...")
        schemas = self.schema_boot.run_schema_boot(self.documents, queries)
        print(f"Generated schemas for {len(schemas)} document clusters.")
        return schemas
    
    def extract_annotations(self, schemas):
        """Extract structured annotations"""
        print("Extracting annotations using AnnotationExtractor...")
        annotations = self.annotation_extractor.process_documents(schemas, self.documents)
        print(f"Extracted annotations for {len(annotations)} documents.")
        return annotations
    
    def run_retrieval(self, query, target_fields=None):
        """Execute structured semantic retrieval"""
        print(f"Running structured semantic retrieval for query: '{query}'")
        
        # Ensure annotation data is loaded
        if not self.ssr.annotations:
            self.ssr.load_annotations()
        
        results = self.ssr.retrieve(query, target_fields)
        print(f"Found {results['results_count']} results.")
        return results
    
    def run_full_pipeline(self, queries=None, max_docs=100):
        """Run full AnnoRetrieve pipeline"""
        print("Starting AnnoRetrieve full pipeline...")
        
        # 1. Load documents
        self.load_documents(max_docs)
        
        # 2. Generate annotation schemas
        schemas = self.generate_schemas(queries)
        
        # 3. Extract annotations
        self.extract_annotations(schemas)
        
        print("AnnoRetrieve full pipeline completed successfully!")
        return {
            'schemas': schemas,
            'document_count': len(self.documents)
        }

def main():
    """Main function"""
    # Create AnnoRetrieve system instance
    annoretrieve = AnnoRetrieveSystem()
    
    # Example: Run full pipeline
    annoretrieve.run_full_pipeline(max_docs=10)
    
    # Example: Execute retrieval
    query = "Find documents with technical details about algorithms"
    results = annoretrieve.run_retrieval(query, target_fields=['document_type', 'technical_details', 'methodology'])
    
    # Print retrieval results
    print("\nRetrieval Results:")
    print(f"Query: {results['query']}")
    print(f"SQL Query: {results['sql_query']}")
    print(f"Results Count: {results['results_count']}")
    print(f"Top Results: {results['top_results']}")
    
    if 'extracted_data' in results:
        print("\nExtracted Data:")
        for doc_id, data in results['extracted_data'].items():
            print(f"\nDocument {doc_id}:")
            for field, value in data.items():
                print(f"  {field}: {value[:200]}...") if isinstance(value, str) else print(f"  {field}: {value}")

if __name__ == "__main__":
    main()
