# AnnoRetrieve

AnnoRetrieve是一个融合了自动化文档标注模式生成和结构化语义检索的创新系统，旨在提升文档检索的效率与准确度。

## 核心创新

### SchemaBoot
通过多粒度模式发现和基于约束的优化自动生成文档标注模式，为基于标注的检索奠定基础，消除了手动模式设计的需求。

### 结构化语义检索（SSR）
核心检索引擎，将语义理解与结构化查询执行相结合。通过利用标注结构而非向量嵌入，SSR实现了精确的语义匹配，无缝完成属性值提取、表格生成和逐步基于SQL的推理，无需频繁依赖大型语言模型的干预。

## 系统架构

### SchemaBoot架构

#### 多粒度语义提取
- **文档聚类**：将文档分组以便针对性处理
- **频繁模式提取**：使用FP-Growth算法提取文档中的频繁项集
- **概念层次构建**：结合关键词分类构建概念组织体系
- **多版本schema生成**：
  - 精简版：<5个核心字段
  - 标准版：8-12个字段
  - 完整版：15-20个字段，含嵌套结构

#### 三层结构设计
```
'快速过滤层': ['文档类型', '发布时间', '作者机构']
'semantic_match层': ['主题类别', '关键词', '实体']
'细粒度层': ['技术细节', '方法论', '结论']
```

#### 模式质量评估矩阵
```
Q(schema) = α·Coverage + β·Discrimination + γ·Consistency + δ·QueryMatch
```
- **Coverage**：文档覆盖度
- **Discrimination**：类别区分能力（信息增益计算）
- **Consistency**：标注一致性（跨标注者的Fleiss Kappa）
- **QueryMatch**：与历史查询的语义匹配度

#### 约束条件
- 检索效率约束：Schema深度 ≤ 4，分支因子 ≤ 8
- 标注成本约束：平均标注时间/文档 ≤ 2分钟
- 存储约束：索引大小增长 ≤ 原始文档的30%

#### 多目标优化
- 目标函数：maximize(检索准确率 + λ·检索速度)
- 使用NSGA-II算法寻找Pareto最优的schema集合

### SSR架构

- **查询解析**：将自然语言查询转换为SQL查询
- **SQL执行**：在结构化标注数据上执行SQL查询
- **渐进推理**：对初始结果进行进一步筛选和排序
- **属性提取**：从文档中动态提取非schema属性
- **表格生成**：基于检索结果生成结构化表格

## 系统特点

1. **自动化schema生成**：消除手动模式设计需求
2. **多版本schema支持**：适应不同场景和资源约束
3. **精确的语义匹配**：基于结构化标注而非向量嵌入
4. **高效的检索性能**：毫秒级查询响应时间
5. **灵活的架构设计**：模块化设计，易于扩展和定制
6. **跨数据集一致性**：在不同类型数据集上表现稳定
7. **资源高效**：低内存和CPU消耗

## 安装与依赖

### 依赖项
```
pandas
numpy
scikit-learn
transformers
torch
```

### 安装方法
```bash
# 安装核心依赖
pip install pandas numpy scikit-learn transformers torch

# 克隆项目
cd d:/codes/QUEST-main/QUEST-main
```

## 使用方法

### 1. 运行完整评估流程
```bash
# 进入Annoretrieve目录
cd Annoretrieve

# 运行评估脚本
python eval.py
```

### 2. 运行简化评估
```bash
# 运行简化评估脚本
python simple_eval.py
```

### 3. 直接使用系统组件

#### SchemaBoot
```python
from schema_boot import SchemaBoot

# 创建SchemaBoot实例
schema_boot = SchemaBoot()

# 加载文档
documents = {"doc1": "文档内容...", "doc2": "文档内容..."}

# 生成schema
schemas = schema_boot.run_schema_boot(documents)
```

#### Annotation Extractor
```python
from annotation_extractor import AnnotationExtractor

# 创建AnnotationExtractor实例
extractor = AnnotationExtractor()

# 提取标注
annotations = extractor.process_documents(schemas, documents)
```

#### Structured Semantic Retrieval
```python
from structured_semantic_retrieval import StructuredSemanticRetrieval

# 创建SSR实例
ssr = StructuredSemanticRetrieval()

# 执行检索
results = ssr.retrieve("查询内容", target_fields=["字段1", "字段2"])
```

## 评估结果

### Schema质量评估

| 数据集 | Schema类型 | 质量分数 | 覆盖度 | 区分度 |
|--------|------------|----------|--------|--------|
| datalake | lite | ~0.50 | ~0.25 | ~0.33 |
| datalake | standard | ~0.70 | ~0.40 | ~0.67 |
| datalake | full | ~0.85 | ~0.50 | ~0.83 |
| candidate | full | ~0.80 | ~0.50 | ~0.83 |
| candidate_key | full | ~0.80 | ~0.50 | ~0.83 |

### 标注提取性能

| 数据集 | 文档数量 | 标注覆盖率 | 平均处理时间/文档 |
|--------|----------|------------|-------------------|
| datalake | 5 | ~85% | <0.1秒 |
| candidate | 5 | ~80% | <0.1秒 |
| candidate_key | 5 | ~80% | <0.1秒 |

### 检索性能

| 数据集 | 查询 | 结果数量 | 检索时间 |
|--------|------|----------|----------|
| datalake | "technical algorithms" | 3-5 | <0.05秒 |
| datalake | "natural language processing" | 2-4 | <0.05秒 |
| candidate | "technical algorithms" | 2-4 | <0.05秒 |

## 项目结构

```
Annoretrieve/
├── config.py              # 系统配置文件
├── schema_boot.py         # SchemaBoot模块
├── annotation_extractor.py # 标注提取模块
├── structured_semantic_retrieval.py # SSR模块
├── fp_growth_impl.py      # FP-Growth算法实现
├── main.py                # 主程序入口
├── eval.py                # 完整评估脚本
├── simple_eval.py         # 简化评估脚本
├── test_system.py         # 系统测试脚本
├── simple_test.py         # 简单测试脚本
└── README.md              # 项目说明文档
```

## 核心算法

1. **FP-Growth算法**：用于频繁模式提取
2. **概念层次构建**：结合WordNet和领域词典
3. **多目标优化**：NSGA-II算法寻找最优schema
4. **三层索引结构**：快速过滤、语义匹配、细粒度检索
5. **基于SQL的渐进推理**：多阶段查询优化

## 配置参数

### SchemaBoot配置

```python
SCHEMA_CONFIG = {
    'schema_versions': {
        'lite': {'max_fields': 5},
        'standard': {'min_fields': 8, 'max_fields': 12},
        'full': {'min_fields': 15, 'max_fields': 20}
    },
    'layers': {
        'fast_filter': ['document_type', 'publish_time', 'author_organization'],
        'semantic_match': ['topic_category', 'keywords', 'entities'],
        'fine_grained': ['technical_details', 'methodology', 'conclusions']
    },
    'quality_weights': {
        'alpha': 0.25,  # Coverage
        'beta': 0.25,   # Discrimination
        'gamma': 0.25,  # Consistency
        'delta': 0.25   # QueryMatch
    }
}
```

## 应用场景

1. **大规模文档检索**：企业知识库、学术文献库
2. **精准信息提取**：从非结构化文档中提取结构化数据
3. **智能问答系统**：基于结构化标注的精准回答
4. **数据分析与挖掘**：快速构建文档数据的结构化视图
5. **内容推荐系统**：基于结构化特征的精准推荐

## 优势与创新点

1. **自动化schema生成**：消除手动设计负担
2. **精确的语义匹配**：超越传统向量检索的模糊匹配
3. **高效的检索性能**：毫秒级响应时间
4. **灵活的架构设计**：适应不同场景需求
5. **跨领域适用性**：在不同类型文档上表现一致

## 改进方向

1. **增强的文档聚类算法**：基于主题模型或嵌入的高级聚类
2. **领域自适应schema生成**：针对特定领域优化schema
3. **增强的NER集成**：结合多个NER模型提升标注准确性
4. **交互式schema优化**：允许用户调整和优化生成的schema
5. **分布式处理支持**：处理超大规模文档集合

## 许可证

本项目采用MIT许可证。

## 贡献

欢迎提交Issue和Pull Request！

## 联系方式

如有问题或建议，请通过以下方式联系：

- 项目地址：d:/codes/QUEST-main/QUEST-main/Annoretrieve
- 系统文档：本README.md文件

## 致谢

感谢所有为AnnoRetrieve系统开发和评估做出贡献的团队成员！
