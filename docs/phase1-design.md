# Phase 1 技术方案：致病靶点发现

## 1. 系统架构

### 1.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户层                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  输入：VCF/FASTA 文件 或 自然语言描述                       │   │
│  │  输出：致病变异列表 + 评分 + 注释 + 可视化                   │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    意图理解智能体 (Intent Agent)                   │
│  • 解析查询模式：遍寻 / 定向                                     │
│  • 提取关键实体：基因名、疾病名、区域范围                         │
│  • 生成执行计划                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    数据准备智能体 (Data Agent)                     │
│  • 文件解析：VCF → 变异列表                                      │
│  • 数据验证：格式检查、质量过滤                                   │
│  • 区域定位：获取目标序列                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Genos 分析智能体 (Analysis Agent)              │
│  • 调用 Genos SDK predict_variants()                            │
│  • 致病性评分计算                                               │
│  • 批量处理优化                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    注释增强智能体 (Annotation Agent)              │
│  • ClinVar 数据库匹配                                           │
│  • ClinGen 致病性分类                                           │
│  • gnomAD 频率数据                                              │
│  • OMIM 疾病关联                                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    结果输出智能体 (Output Agent)                  │
│  • 排序筛选：按致病概率 Top-N                                    │
│  • 可视化生成：变异位置图、热力图                                │
│  • 报告导出：JSON/CSV/HTML                                       │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 技术栈

| 层级 | 技术选型 |
|-----|---------|
| **前端** | React + TypeScript + ECharts |
| **后端** | Python + FastAPI |
| **多智能体框架** | LangGraph / AutoGen |
| **基因模型** | Genos SDK |
| **向量嵌入** | Genos embed_sequence() |
| **数据库** | PostgreSQL + Redis |
| **文件存储** | MinIO / S3 |

---

## 2. 智能体职责分工

### 2.1 意图理解智能体 (Intent Agent)

```python
class IntentAgent:
    """解析用户意图，生成执行计划"""
    
    capabilities = [
        "query_mode_detection",  # 遍寻/定向模式判断
        "entity_extraction",      # 基因名、疾病名、区域提取
        "plan_generation",        # 执行计划生成
    ]
    
    def analyze_intent(self, user_input: str) -> QueryPlan:
        # 遍寻模式关键词：所有、全部、全面、扫描
        # 定向模式关键词：特定疾病、某基因、某区域
        
        if self.is_scan_mode(user_input):
            return ScanPlan(
                mode="scan",
                filters=self.extract_filters(user_input)
            )
        else:
            return TargetedPlan(
                mode="targeted",
                gene=self.extract_gene(user_input),
                disease=self.extract_disease(user_input),
                region=self.extract_region(user_input)
            )
```

### 2.2 数据准备智能体 (Data Agent)

```python
class DataAgent:
    """处理基因测序数据输入"""
    
    capabilities = [
        "vcf_parser",           # VCF 文件解析
        "fasta_parser",         # FASTA 序列解析
        "quality_filter",       # 质量过滤
        "region_extractor",     # 区域序列提取
    ]
    
    def process_vcf(self, vcf_file: str) -> List[Variant]:
        """解析 VCF 文件为变异列表"""
        variants = []
        for record in self.parse_vcf(vcf_file):
            variant = Variant(
                chrom=record.CHROM,
                pos=record.POS,
                ref=record.REF,
                alt=record.ALT[0],
                quality=record.QUAL,
                filter=record.FILTER
            )
            variants.append(variant)
        
        # 质量过滤
        variants = [v for v in variants if v.quality > 30]
        return variants
    
    def get_sequence(self, chrom: str, start: int, end: int) -> str:
        """从参考基因组获取序列"""
        # 使用 pyfaidx 或 Ensembl API
        pass
```

### 2.3 Genos 分析智能体 (Analysis Agent)

```python
class GenosAnalysisAgent:
    """调用 Genos SDK 进行致病性预测"""
    
    capabilities = [
        "variant_prediction",   # 变异致病性预测
        "batch_processing",     # 批量处理
        "score_calculation",    # 综合评分
    ]
    
    tools = [
        "Genos.predict_variants",
        "Genos.embed_sequence",
    ]
    
    async def predict_pathogenicity(
        self,
        variants: List[Variant],
        context_window: int = 10000
    ) -> List[PredictionResult]:
        """批量预测变异致病性"""
        
        results = []
        batch_size = 100
        
        for batch in self.chunk(variants, batch_size):
            # 获取变异区域序列
            sequences = await self.get_context_sequences(batch, context_window)
            
            # 调用 Genos API
            predictions = self.genos_client.predict_variants(
                sequences=sequences,
                variants=batch
            )
            
            results.extend(predictions)
        
        return results
```

### 2.4 注释增强智能体 (Annotation Agent)

```python
class AnnotationAgent:
    """数据库注释增强"""
    
    databases = {
        "ClinVar": "临床意义数据库",
        "ClinGen": "致病性分类标准",
        "gnomAD": "人群频率数据",
        "OMIM": "遗传疾病关联",
        "dbSNP": "变异ID映射",
    }
    
    async def annotate_variant(self, variant: Variant) -> VariantAnnotation:
        """为变异添加数据库注释"""
        
        annotation = VariantAnnotation(variant=variant)
        
        # ClinVar 查询
        clinvar = await self.query_clinvar(variant)
        annotation.clinical_significance = clinvar.significance
        annotation.clinvar_id = clinvar.id
        
        # gnomAD 频率
        gnomad = await self.query_gnomad(variant)
        annotation.population_frequency = gnomad.af
        
        # OMIM 疾病关联
        omim = await self.query_omim(variant.gene)
        annotation.diseases = omim.diseases
        
        return annotation
```

### 2.5 结果输出智能体 (Output Agent)

```python
class OutputAgent:
    """结果处理与可视化"""
    
    capabilities = [
        "result_sorting",       # 按致病概率排序
        "visualization",        # 生成图表
        "report_export",        # 导出报告
    ]
    
    def generate_report(
        self,
        results: List[AnnotatedResult],
        format: str = "html"
    ) -> Report:
        """生成分析报告"""
        
        # 按致病概率排序
        sorted_results = sorted(
            results,
            key=lambda r: r.pathogenicity_score,
            reverse=True
        )
        
        # Top-N 筛选
        top_results = sorted_results[:100]
        
        # 生成可视化
        charts = self.generate_charts(top_results)
        
        return Report(
            results=top_results,
            charts=charts,
            format=format
        )
```

---

## 3. Genos SDK 集成

### 3.1 核心 API 使用

```python
from genos import GenosClient

client = GenosClient(api_key="xxx", endpoint="xxx")

# 变异预测
result = client.variant_predict(
    assembly="hg38",
    chrom="chr17",
    pos=43000000,
    ref="A",
    alt="G"
)
# 返回：Pathogenic / Benign + 置信度

# 序列嵌入（用于下游分析）
embedding = client.get_embedding(
    sequence="ATGC...",
    model_name="Genos-10B",
    pooling_method="mean"
)
```

### 3.2 批量处理优化

```python
class GenosBatchProcessor:
    """批量处理优化"""
    
    def __init__(self, client: GenosClient, batch_size: int = 100):
        self.client = client
        self.batch_size = batch_size
    
    async def batch_predict(
        self,
        variants: List[Variant]
    ) -> List[PredictionResult]:
        """批量预测，自动分片"""
        
        results = []
        batches = self.create_batches(variants)
        
        # 并行处理
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(self.process_batch, batch)
                for batch in batches
            ]
            for future in as_completed(futures):
                results.extend(future.result())
        
        return results
```

---

## 4. 数据流设计

### 4.1 遍寻模式数据流

```
用户上传 VCF 文件
     │
     ▼
DataAgent: 解析 → 变异列表 (12,345 个)
     │
     ▼
质量过滤 → 剩余 8,567 个高质量变异
     │
     ▼
GenosAgent: 批量预测 (batch_size=100, 86 batches)
     │
     ▼
AnnotationAgent: 数据库注释 (ClinVar/gnomAD/OMIM)
     │
     ▼
OutputAgent: 排序 → Top-100 致病变异
     │
     ▼
生成报告 + 可视化图表
```

### 4.2 定向模式数据流

```
用户输入："查找 BRCA1 基因与乳腺癌相关的致病变异"
     │
     ▼
IntentAgent: 识别定向模式 + 提取实体
    gene=BRCA1, disease=breast_cancer
     │
     ▼
DataAgent: 获取 BRCA1 基因区域序列
    chr17:43000000-43100000
     │
     ▼
从用户 VCF 或数据库获取该区域变异
     │
     ▼
GenosAgent: 预测致病性 + 乳腺癌关联评分
     │
     ▼
AnnotationAgent: 添加 ClinVar + OMIM 注释
     │
     ▼
OutputAgent: 按疾病相关性排序 → 报告
```

---

## 5. MVP 范围定义

### 5.1 MVP 功能清单

| 功能 | 优先级 | MVP 状态 |
|-----|-------|---------|
| VCF 文件上传解析 | P0 | ✅ 必须 |
| Genos 变异预测调用 | P0 | ✅ 必须 |
| ClinVar 数据库注释 | P0 | ✅ 必须 |
| 致病性评分排序 | P0 | ✅ 必须 |
| JSON/CSV 结果导出 | P0 | ✅ 必须 |
| 遍寻模式 | P0 | ✅ 必须 |
| 定向模式 | P1 | ⏳ MVP 后 |
| 自然语言输入 | P1 | ⏳ MVP 后 |
| 可视化图表 | P1 | ⏳ MVP 后 |
| HTML 报告 | P1 | ⏳ MVP 后 |

### 5.2 MVP 技术范围

```
MVP = 
    VCF 解析器
  + Genos predict_variants() 调用
  + ClinVar API 查询
  + 致病性排序算法
  + REST API (FastAPI)
  + 基础 CLI 工具
```

### 5.3 MVP 后续迭代

- 迭代 1：定向模式 + 自然语言输入
- 迭代 2：可视化图表 + HTML 报告
- 迭代 3：更多数据库 (gnomAD, OMIM)
- 迭代 4：性能优化 + 缓存

---

## 6. API 设计

### 6.1 REST API

```yaml
# 遍寻模式
POST /api/v1/scan
  Request:
    file: VCF 文件
    filters:
      min_quality: 30
      region: "chr17:43000000-43100000" (可选)
  Response:
    variants: List[VariantResult]
    total_count: int
    pathogenic_count: int

# 定向模式
POST /api/v1/target
  Request:
    gene: "BRCA1"
    disease: "breast_cancer" (可选)
    file: VCF 文件 (可选)
  Response:
    variants: List[VariantResult]
    gene_info: GeneInfo

# 变异详情
GET /api/v1/variant/{variant_id}
  Response:
    variant: VariantDetail
    pathogenicity: Score
    annotations: Annotations
```

### 6.2 CLI 工具

```bash
# 遍寻模式
geneclaw scan --input sample.vcf --output results.json

# 定向模式
geneclaw target --gene BRCA1 --disease breast_cancer --input sample.vcf

# 单变异查询
geneclaw query --chrom chr17 --pos 43000000 --ref A --alt G
```

---

## 7. 开发计划

### 7.1 时间估算

| 阶段 | 内容 | 时间 |
|-----|------|-----|
| Week 1 | VCF 解析 + Genos SDK 集成 | 5 天 |
| Week 2 | ClinVar 注释 + 排序算法 | 5 天 |
| Week 3 | REST API + CLI 工具 | 5 天 |
| Week 4 | 测试 + 文档 + 发布 | 5 天 |

### 7.2 里程碑

- M1: VCF 解析器可用 (Day 5)
- M2: Genos 预测可用 (Day 10)
- M3: MVP 功能完整 (Day 15)
- M4: MVP 发布 (Day 20)

---

## 8. 风险与缓解

| 风险 | 影响 | 缓解措施 |
|-----|-----|---------|
| Genos API 不稳定 | 高 | 本地缓存 + 重试机制 |
| VCF 文件格式多样 | 中 | 多格式解析器 + 兼容测试 |
| ClinVar 查询延迟 | 中 | 本地数据库镜像 + 批量查询 |
| 大文件处理慢 | 中 | 流式处理 + 分片加载 |

---

## 9. 附录

### 9.1 数据格式示例

```json
// 变异结果
{
  "variant_id": "rs12345",
  "chrom": "chr17",
  "pos": 43000000,
  "ref": "A",
  "alt": "G",
  "gene": "BRCA1",
  "pathogenicity_score": 0.92,
  "clinical_significance": "Likely_pathogenic",
  "population_frequency": 0.0001,
  "diseases": ["HBOC", "breast_cancer"],
  "genos_prediction": {
    "score": 0.92,
    "confidence": 0.85
  }
}
```

### 9.2 项目结构

```
GeneClaw/
├── README.md
├── docs/
│   ├── phase1-design.md
│   └── api-spec.md
├── src/
│   ├── agents/
│   │   ├── intent_agent.py
│   │   ├── data_agent.py
│   │   ├── genos_agent.py
│   │   ├── annotation_agent.py
│   │   └ output_agent.py
│   ├── api/
│   │   ├── routes.py
│   │   ├── schemas.py
│   │   └── main.py
│   ├── parsers/
│   │   ├── vcf_parser.py
│   │   └ fasta_parser.py
│   ├── utils/
│   │   ├── genos_client.py
│   │   └ database_clients.py
│   └── cli/
│       └ geneclaw.py
├── tests/
│   ├── test_vcf_parser.py
│   ├── test_genos_agent.py
│   └── test_api.py
├── requirements.txt
├── setup.py
└── Makefile
```

---

**方案起草完成，待门下省审议。**

*中书省*
*任务ID: JJC-20260402-003*