# GeneClaw 智能体技能匹配目录

> 本文档说明 GeneClaw 八大智能体的职责定位及匹配的 OpenClaw-Medical-Skills 技能。

---

## 一、智能体架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                       决策层 (Tier 1)                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ 协调智能体 │  │ 规划智能体 │  │ 审议智能体 │  │ 派发智能体 │        │
│  │coordinator│  │ planner  │  │ reviewer │  │dispatcher│        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       执行层 (Tier 2)                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ 数据工程师 │  │ 生信工程师 │  │ 临床智能体 │  │ 报告智能体 │        │
│  │data_engineer│ │bioinfo_  │  │clinical_ │  │reporter_ │        │
│  │            │ │ engineer │  │ expert   │  │ agent    │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 二、决策层智能体

### 1. 协调智能体 (Coordinator)

**职责**：入口分拣、意图识别、任务创建、结果回奏

**权限**：只能调用规划智能体 (planner)

**匹配技能**：

| 技能名称 | 描述 | 用途 |
|---------|------|------|
| `hypothesis-generation` | 科学假设生成 | 根据用户意图生成分析假设，指导后续分析方向 |
| `biomni-general-agent` | 通用生物医学智能体 | 提供生物医学领域的通用知识和推理能力 |

---

### 2. 规划智能体 (Planner)

**职责**：分析方案设计、API选择、数据流规划

**权限**：可调用审议智能体、派发智能体

**匹配技能**：

| 技能名称 | 描述 | 用途 |
|---------|------|------|
| `hypothesis-generation` | 科学假设生成 | 设计基因分析假设和验证路径 |
| `biomni-general-agent` | 通用生物医学智能体 | 提供生物医学领域知识支持 |
| `bio-workflow-management-nextflow-pipelines` | Nextflow流程管理 | 规划大规模基因分析流水线 |
| `bio-workflow-management-snakemake-workflows` | Snakemake流程管理 | 规划可复现的分析工作流 |

---

### 3. 审议智能体 (Reviewer)

**职责**：方案审核、质量把关、可封驳

**权限**：可调用规划智能体（封驳回工）、派发智能体（准奏派发）

**匹配技能**：

| 技能名称 | 描述 | 用途 |
|---------|------|------|
| `bio-clinical-databases-variant-prioritization` | 变异优先级排序 | 审核变异筛选方案的科学性 |
| `bio-variant-calling-clinical-interpretation` | 变异临床解读 | 审核临床解读方案的准确性 |

---

### 4. 派发智能体 (Dispatcher)

**职责**：任务调度、执行监控、结果汇总

**权限**：可调用所有执行层智能体

**匹配技能**：

| 技能名称 | 描述 | 用途 |
|---------|------|------|
| `bio-workflow-management-nextflow-pipelines` | Nextflow流程管理 | 编排并行分析任务 |
| `bio-workflow-management-snakemake-workflows` | Snakemake流程管理 | 管理任务依赖和调度 |
| `bio-workflow-management-cwl-workflows` | CWL流程管理 | 标准化流程描述 |
| `slurm-job-script-generator` | SLURM作业脚本生成 | 生成HPC集群作业脚本 |

---

## 三、执行层智能体

### 5. 数据工程师 (Data Engineer)

**职责**：VCF解析、质量控制、变异提取（执行层第1步）

**权限**：结果传递给生信工程师

**匹配技能**：

| 技能名称 | 描述 | 用途 |
|---------|------|------|
| `bio-vcf-basics` | VCF基础操作 | 解析和查询VCF/BCF文件 |
| `bio-vcf-manipulation` | VCF文件操作 | 过滤、合并、拆分VCF文件 |
| `bio-vcf-statistics` | VCF统计分析 | 计算变异统计指标 |
| `bio-variant-calling-filtering-best-practices` | 变异过滤最佳实践 | 应用GATK等最佳实践过滤变异 |
| `bio-variant-normalization` | 变异标准化 | 左对齐、拆分多等位基因位点 |
| `vcf-annotator` | VCF注释工具 | 添加数据库注释信息 |
| `bio-read-qc-quality-reports` | 测序质量控制报告 | 生成质量评估报告 |

---

### 6. 生信工程师 (Bioinfo Engineer)

**职责**：Genos API调用、变异预测、致病性评分（执行层第2步）

**权限**：结果传递给临床智能体

**匹配技能**：

| 技能名称 | 描述 | 用途 |
|---------|------|------|
| `bio-variant-annotation` | 变异注释 | 使用VEP/SnpEff/ANNOVAR注释变异 |
| `bio-variant-calling` | 变异检测 | GATK等工具的变异检测流程 |
| `bio-variant-calling-deepvariant` | DeepVariant变异检测 | 深度学习变异检测工具 |
| `bio-variant-calling-clinical-interpretation` | 变异临床解读 | 致病性判定和临床分类 |
| `bio-clinical-databases-variant-prioritization` | 变异优先级排序 | 多维度筛选候选致病变异 |
| `bio-sequence-properties` | 序列属性分析 | 分析DNA/RNA序列特征 |
| `bio-sequence-similarity` | 序列相似性分析 | BLAST等序列比对 |
| `bio-sequence-statistics` | 序列统计分析 | 计算序列组成统计量 |

---

### 7. 临床智能体 (Clinical Expert)

**职责**：ClinVar/OMIM/gnomAD注释、临床意义增强（执行层第3步）

**权限**：结果传递给报告智能体

**匹配技能**：

| 技能名称 | 描述 | 用途 |
|---------|------|------|
| `bio-clinical-databases-clinvar-lookup` | ClinVar查询 | 查询变异临床意义分类 |
| `bio-clinical-databases-gnomad-frequencies` | gnomAD频率查询 | 查询人群等位基因频率 |
| `bio-clinical-databases-variant-prioritization` | 变异优先级排序 | 综合筛选候选致病变异 |
| `clinvar-database` | ClinVar数据库 | 直接访问ClinVar数据 |
| `gnomad-database` | gnomAD数据库 | 直接访问gnomAD数据 |
| `gene-database` | 基因数据库 | 查询基因功能和疾病关联 |
| `bio-pathway-enrichment-visualization` | 通路富集可视化 | 可视化基因通路富集结果 |
| `bio-pathway-go-enrichment` | GO富集分析 | Gene Ontology功能注释 |
| `bio-pathway-gsea` | GSEA分析 | 基因集富集分析 |
| `bio-systems-biology-gene-essentiality` | 基因必需性分析 | 评估基因功能重要性 |
| `tooluniverse-gene-enrichment` | 基因富集工具 | 多数据库基因富集分析 |

---

### 8. 报告智能体 (Reporter Agent)

**职责**：结果排序、图表生成、报告导出（执行层第4步，完成后回奏协调智能体）

**权限**：回奏协调智能体

**匹配技能**：

| 技能名称 | 描述 | 用途 |
|---------|------|------|
| `bio-data-visualization-genome-browser-tracks` | 基因组浏览器轨道 | 生成IGV等可视化轨道 |
| `bio-data-visualization-genome-tracks` | 基因组轨道可视化 | 创建自定义基因组视图 |
| `bio-data-visualization-heatmaps-clustering` | 热图聚类可视化 | 生成表达/变异热图 |
| `bio-data-visualization-volcano-customization` | 火山图定制 | 差异分析结果可视化 |
| `bio-data-visualization-circos-plots` | Circos图绘制 | 染色体水平变异展示 |
| `bio-reporting-automated-qc-reports` | 自动化QC报告 | 生成质量控制报告 |
| `bio-reporting-figure-export` | 图表导出 | 导出高质量图像文件 |
| `bio-reporting-jupyter-reports` | Jupyter报告 | 生成交互式分析报告 |
| `pdf-processing` | PDF处理 | 生成和编辑PDF报告 |
| `clinical-reports` | 临床报告生成 | 生成临床诊断报告 |
| `data-visualization-expert` | 数据可视化专家 | 高级可视化设计和实现 |

---

## 四、执行流程

```
用户请求
    │
    ▼
协调智能体 ─────────────────────────────────────┐
    │ 分拣意图，创建任务                          │ 回奏结果
    ▼                                           │
规划智能体                                       │
    │ 设计分析方案                               │
    ▼                                           │
审议智能体                                       │
    │ 审核方案（准奏/封驳）                       │
    ▼ 准奏                                      │
派发智能体                                       │
    │ 派发任务                                   │
    ▼                                           │
┌───────────────────────────────────────────┐   │
│ 执行层流水线                                │   │
│                                           │   │
│ 数据工程师 → 生信工程师 → 临床智能体 → 报告智能体│
│ (VCF解析)   (变异预测)   (临床注释)   (报告生成)│   │
└───────────────────────────────────────────┘   │
    │                                           │
    └───────────────────────────────────────────┘
```

---

## 五、技能来源

所有技能来自 [OpenClaw-Medical-Skills](https://github.com/FreedomIntelligence/OpenClaw-Medical-Skills) 仓库，包含 869 个生物医学和临床研究相关的 AI 技能。

---

*文档生成时间: 2026-04-10*
*GeneClaw 版本: 1.0.0*