# AnnoRetrieve Configuration

# SchemaBoot Configuration
SCHEMA_CONFIG = {
    # 多版本schema字段数量配置
    'schema_versions': {
        'lite': {'max_fields': 5},
        'standard': {'min_fields': 8, 'max_fields': 12},
        'full': {'min_fields': 15, 'max_fields': 20}
    },
    
    # 三层结构配置
    'layers': {
        'fast_filter': ['document_type', 'publish_time', 'author_organization'],
        'semantic_match': ['topic_category', 'keywords', 'entities'],
        'fine_grained': ['technical_details', 'methodology', 'conclusions']
    },
    
    # 模式质量评估权重
    'quality_weights': {
        'alpha': 0.25,  # Coverage
        'beta': 0.25,   # Discrimination
        'gamma': 0.25,  # Consistency
        'delta': 0.25   # QueryMatch
    },
    
    # 约束条件
    'constraints': {
        'max_depth': 4,
        'max_branch_factor': 8,
        'max_annotation_time_per_doc': 120,  # 秒
        'max_index_growth': 0.3  # 30%
    }
}

# SSR (Structured Semantic Retrieval) Configuration
SSR_CONFIG = {
    'query_processing': {
        'max_sql_depth': 5,
        'enable_progressive_reasoning': True
    },
    
    'indexing': {
        'enable_hybrid_index': True,
        'index_types': ['metadata', 'semantic', 'fine_grained']
    }
}

# 数据路径配置
DATA_PATHS = {
    'datalake': '../datalake/origin',
    'candidate': '../candidate',
    'annotations': './annotations',
    'schemas': './schemas'
}

# 模型配置
MODEL_CONFIG = {
    'ner_model': 'en_core_web_sm',
    'relation_extractor': 'stanford-openie',
    'embedding_model': 'all-MiniLM-L6-v2',
    'gli_ner_model': 'yuchenlin/GliNER-base'
}
