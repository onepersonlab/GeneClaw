# GeneClaw 多智能体架构设计

> **中书省起草 · 待门下省审议**
> 
> 任务ID: JJC-20260402-005

---

## 1. 设计理念：制度化协作

### 1.1 核心思想

GeneClaw 采用**制度化的多智能体协作架构**，借鉴 edict 项目（三省六部制）的分权制衡思想：

```
用户请求 → 协调智能体 → 规划智能体 → 审议智能体 → 派发智能体 → 专业智能体 → 结果回奏
```

**三大保障机制：**

| 机制 | 实现方式 | 效果 |
|------|---------|------|
| **制度性审核** | 审议智能体必审所有方案 | 防止规划错误导致无效分析 |
| **分权制衡** | 权限矩阵定义调用边界 | 防止越权操作和数据污染 |
| **完全可观测** | 全链路活动日志 + 进度追踪 | 每一步操作都可追溯审计 |

### 1.2 与传统框架对比

| 维度 | CrewAI/AutoGen | GeneClaw 多智能体 |
|------|----------------|-----------------|
| 协作模式 | 自由讨论 | 制度化流转 |
| 质量保障 | 依赖 Agent 智能 | 强制审议 + 封驳机制 |
| 权限控制 | 无 | 配置化权限矩阵 |
| 失败恢复 | 手工重启 | 自动重试 + 升级协调 |
| 成本控制 | 不透明 | 每步上报资源消耗 |

---

## 2. 八大智能体定义

### 2.1 架构总览图

```
┌─────────────────────────────────────────────────────────────────────┐
│                          用户层                                      │
│   输入：VCF/FASTA 文件 + 查询意图（遍寻/定向）                          │
│   输出：致病变异列表 + 评分 + 注释 + 可视化报告                         │
└────────────────────────────────────┬────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    🎯 协调智能体 (Coordinator)                        │
│   ┌───────────────────────────────────────────────────────────────┐ │
│   │  职责：入口分拣、意图识别、任务创建、结果回奏                      │ │
│   │  类比：太子（消息分拣官）                                       │ │
│   │  权限：只能调用 规划智能体                                      │ │
│   └───────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────┬────────────────────────────────┘
                                     │ 传旨
                                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    📋 规划智能体 (Planner)                            │
│   ┌───────────────────────────────────────────────────────────────┐ │
│   │  职责：分析方案设计、API 选择、数据流规划                         │ │
│   │  类比：中书省（方案起草官）                                      │ │
│   │  权限：只能调用 审议智能体、派发智能体（咨询）                     │ │
│   │  输出：分析方案文档（含 API 调用策略、数据源、预期结果）           │ │
│   └───────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────┬────────────────────────────────┘
                                     │ 提交审议
                                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    🔍 审议智能体 (Reviewer)                           │
│   ┌───────────────────────────────────────────────────────────────┐ │
│   │  职责：方案审核、质量把关、风险评估                               │ │
│   │  类比：门下省（审议封驳官）                                      │ │
│   │  权限：只能调用 规划智能体（封驳回工）、派发智能体（准奏派发）       │ │
│   │  行为：✅ 准奏放行 / 🚫 封驳打回（最多 3 轮）                      │ │
│   └───────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────┬────────────────────────────────┘
                                     │ 准奏 ✅
                                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    📮 派发智能体 (Dispatcher)                         │
│   ┌───────────────────────────────────────────────────────────────┐ │
│   │  职责：任务调度、执行监控、结果汇总                               │ │
│   │  类比：尚书省（派发指挥官）                                      │ │
│   │  权限：只能调用 专业智能体（数据、生信、临床、可视化）              │ │
│   │  行为：并行派发 → 监控进度 → 汇总结果 → 回奏                     │ │
│   └───────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────┬────────────────────────────────┘
                                     │ 派发执行
         ┌───────────────────────────┼───────────────────────────┐
         │                           │                           │
         ▼                           ▼                           ▼
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│  📊 数据工程师       │  │  🧬 生信工程师       │  │  🏥 临床智能体       │
│  (DataEngineer)     │  │  (Bioinformatician) │  │  (ClinicalAgent)    │
│  ┌─────────────────┐│  │  ┌─────────────────┐│  │  ┌─────────────────┐│
│  │ VCF 解析        ││  │  │ Genos API 调用   ││  │  │ ClinVar 注释    ││
│  │ 质量控制        ││  │  │ 变异预测         ││  │  │ OMIM 疾病关联   ││
│  │ 变异提取        ││  │  │ 致病性评分       ││  │  │ 临床意义增强    ││
│  └─────────────────┘│  │  └─────────────────┘│  │  └─────────────────┘│
└─────────────────────┘  └─────────────────────┘  └─────────────────────┘
         │                           │                           │
         └───────────────────────────┼───────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    📈 可视化智能体 (Visualizer)                       │
│   ┌───────────────────────────────────────────────────────────────┐ │
│   │  职责：结果排序、图表生成、报告导出                               │ │
│   │  输出：Top-N 变异列表 + HTML/PDF 报告                            │ │
│   └───────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────┬────────────────────────────────┘
                                     │ 回奏
                                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    🎯 协调智能体（回奏）                               │
│   汇总结果 → 生成用户回复 → 返回给用户                                │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. 智能体职责边界详解

### 3.1 协调智能体 (Coordinator)

**定位：** 总入口，负责用户交互和任务生命周期管理

```python
class CoordinatorAgent:
    """
    协调智能体 — 入口分拣、任务分发
    
    类比：太子（消息分拣官）
    """
    
    # ──── 核心能力 ────
    capabilities = [
        "intent_recognition",     # 意图识别：遍寻/定向模式
        "entity_extraction",      # 实体提取：基因名、疾病名、区域
        "task_creation",          # 任务创建与状态流转
        "result_delivery",        # 结果回奏给用户
    ]
    
    # ──── 权限边界 ────
    allow_agents = ["planner"]   # 只能调用规划智能体
    
    # ──── 禁止行为 ────
    forbidden = [
        "直接调用生信工程师",      # 不能跳过规划/审议
        "直接调用 Genos API",     # 不能执行专业任务
        "修改分析方案",           # 不能干预规划内容
    ]
    
    # ──── 工作流程 ────
    def handle_user_request(self, request: UserRequest) -> Task:
        # Step 1: 意图分析
        intent = self.analyze_intent(request)
        
        # Step 2: 创建任务
        task = Task(
            id=self.generate_task_id(),
            type=intent.mode,  # "scan" or "targeted"
            entities=intent.entities,
            state="Coordinator"
        )
        
        # Step 3: 转交规划智能体
        self.dispatch_to_planner(task)
        
        # Step 4: 等待回奏
        # （派发智能体会通过 sessions_send 回调）
        
        return task
    
    def analyze_intent(self, request: UserRequest) -> Intent:
        """意图识别：判断查询模式"""
        
        # 遍寻模式关键词
        scan_keywords = ["所有", "全部", "扫描", "致病突变", "全面"]
        
        # 定向模式关键词
        targeted_keywords = ["BRCA1", "乳腺癌", "特定基因", "某区域"]
        
        text = request.text.lower()
        
        if any(kw in text for kw in scan_keywords):
            return Intent(
                mode="scan",
                entities=self.extract_filters(text)
            )
        else:
            return Intent(
                mode="targeted",
                gene=self.extract_gene(text),
                disease=self.extract_disease(text),
                region=self.extract_region(text)
            )
```

**输入输出规格：**

| 输入 | 格式 | 示例 |
|------|------|------|
| 用户消息 | 文本 + 文件 | "帮我分析这个 VCF 文件中的致病变异" + sample.vcf |
| 查询模式 | scan/targeted | scan = 全扫描，targeted = 定向查询 |

| 输出 | 格式 | 示例 |
|------|------|------|
| 任务 ID | GC-YYYYMMDD-NNN | GC-20260402-001 |
| 意图分析结果 | JSON | {mode: "scan", entities: {...}} |

---

### 3.2 规划智能体 (Planner)

**定位：** 分析方案设计师，负责制定执行策略

```python
class PlannerAgent:
    """
    规划智能体 — 分析方案设计、API选择
    
    类比：中书省（方案起草官）
    """
    
    # ──── 核心能力 ────
    capabilities = [
        "analysis_design",        # 分析方案设计
        "api_selection",          # API 选择策略
        "data_flow_planning",     # 数据流规划
        "resource_estimation",    # 资源预估（token、时间、API调用次数）
    ]
    
    # ──── 权限边界 ────
    allow_agents = ["reviewer", "dispatcher"]  # 审议 + 咨询派发
    
    # ──── 输出规格 ────
    output_schema = {
        "plan_id": "string",
        "analysis_type": "scan|targeted",
        "data_sources": ["list of files/databases"],
        "api_strategy": {
            "genos": {
                "endpoint": "predict_variants",
                "batch_size": 100,
                "context_window": 10000
            }
        },
        "annotation_sources": ["ClinVar", "gnomAD", "OMIM"],
        "expected_output": {
            "format": "JSON|HTML|PDF",
            "top_n": 100,
            "sort_by": "pathogenicity_score"
        },
        "estimated_resources": {
            "api_calls": 86,      # 假设 8567 变异 / 100 batch
            "tokens": 50000,
            "duration_min": 30
        },
        "risk_assessment": [
            "Genos API 可能超时 → 建议增加重试机制",
            "VCF 文件格式需验证 → 数据工程师先做 QC"
        ]
    }
    
    # ──── 工作流程 ────
    def create_analysis_plan(self, task: Task) -> AnalysisPlan:
        # Step 1: 分析数据源
        data_source = self.identify_data_source(task)
        
        # Step 2: 选择 API 策略
        api_strategy = self.select_api_strategy(task)
        
        # Step 3: 规划注释流程
        annotation_flow = self.plan_annotation(task)
        
        # Step 4: 评估资源和风险
        resources = self.estimate_resources(task)
        risks = self.assess_risks(task)
        
        plan = AnalysisPlan(
            id=f"PLAN-{task.id}",
            data_source=data_source,
            api_strategy=api_strategy,
            annotation_flow=annotation_flow,
            resources=resources,
            risks=risks
        )
        
        # Step 5: 提交审议智能体
        self.submit_for_review(plan)
        
        return plan
    
    def select_api_strategy(self, task: Task) -> APIStrategy:
        """API 选择策略"""
        
        if task.type == "scan":
            # 遍寻模式：批量处理
            return APIStrategy(
                endpoint="batch_predict",
                batch_size=100,
                parallel_workers=4
            )
        else:
            # 定向模式：精细分析
            return APIStrategy(
                endpoint="targeted_predict",
                context_window=10000,  # 扩大上下文窗口
                include_gene_context=True
            )
```

**关键决策点：**

| 决策 | 触发条件 | 策略选择 |
|------|---------|---------|
| API 批量策略 | 变异数 > 1000 | batch_size=100, parallel=4 |
| 注释深度 | 疾病相关查询 | 必须调用 OMIM |
| 数据预处理 | VCF 质量 < 30 | 先做质量控制再分析 |

---

### 3.3 审议智能体 (Reviewer)

**定位：** 质量把关人，审核方案可行性

```python
class ReviewerAgent:
    """
    审议智能体 — 方案审核、质量把关
    
    类比：门下省（审议封驳官）
    """
    
    # ──── 核心能力 ────
    capabilities = [
        "plan_validation",        # 方案完整性验证
        "risk_evaluation",        # 风险评估
        "feasibility_check",      # 可行性检查
        "quality_criteria",       # 质量标准判定
    ]
    
    # ──── 权限边界 ────
    allow_agents = ["planner", "dispatcher"]
    
    # ──── 审议标准 ────
    review_criteria = [
        "数据源是否明确",
        "API 策略是否合理（batch_size、并行度）",
        "注释数据库覆盖是否完整",
        "资源预估是否在预算内",
        "风险缓解措施是否充分",
    ]
    
    # ──── 审议结果 ────
    review_result_schema = {
        "decision": "approve|reject",  # 准奏或封驳
        "score": 0.85,                 # 方案质量评分
        "issues": ["string"],          # 发现的问题
        "suggestions": ["string"],     # 改进建议
        "review_round": 1,             # 审议轮次（最多 3 轮）
    }
    
    # ──── 工作流程 ────
    def review_plan(self, plan: AnalysisPlan) -> ReviewResult:
        # Step 1: 完整性检查
        completeness = self.check_completeness(plan)
        
        # Step 2: 可行性评估
        feasibility = self.evaluate_feasibility(plan)
        
        # Step 3: 风险评估
        risks = self.evaluate_risks(plan)
        
        # Step 4: 综合评分
        score = self.calculate_score(completeness, feasibility, risks)
        
        # Step 5: 决策
        if score >= 0.8:
            # 准奏
            result = ReviewResult(
                decision="approve",
                score=score,
                issues=[],
                suggestions=self.generate_suggestions(plan)
            )
            self.approve_and_dispatch(plan)
        else:
            # 封驳
            result = ReviewResult(
                decision="reject",
                score=score,
                issues=self.identify_issues(plan),
                suggestions=self.generate_suggestions(plan)
            )
            self.reject_and_return(plan)
        
        return result
    
    def approve_and_dispatch(self, plan: AnalysisPlan):
        """准奏后派发给派发智能体"""
        self.update_task_state(plan.task_id, "Approved")
        self.dispatch_to("dispatcher", plan)
    
    def reject_and_return(self, plan: AnalysisPlan):
        """封驳后返回规划智能体修改"""
        self.update_task_state(plan.task_id, "Rejected")
        self.update_review_round(plan.task_id)
        self.dispatch_to("planner", plan, message="🚫 封驳：需修改方案")
```

**审议机制：**

| 场景 | 审议结果 | 后续动作 |
|------|---------|---------|
| 方案完整、风险可控 | ✅ 准奏 | 派发给派发智能体执行 |
| API 策略不合理 | 🚫 封驳 | 返回规划智能体修改 |
| 数据源不明确 | 🚫 封驳 | 返回规划智能体补充 |
| 资源超预算 | ⚠️ 建议优化 | 可准奏但附带建议 |
| 连续 3 轴封驳 | 🚫 终止 | 任务取消，通知用户 |

---

### 3.4 派发智能体 (Dispatcher)

**定位：** 执行总指挥，协调专业智能体并行工作

```python
class DispatcherAgent:
    """
    派发智能体 — 任务调度、结果汇总
    
    类比：尚书省（派发指挥官）
    """
    
    # ──── 核心能力 ────
    capabilities = [
        "task_dispatch",          # 任务派发
        "parallel_coordination",  # 并行协调
        "progress_monitor",       # 进度监控
        "result_aggregation",     # 结果汇总
    ]
    
    # ──── 权限边界 ────
    allow_agents = [
        "data_engineer",
        "bioinformatician",
        "clinical_agent",
        "visualizer"
    ]
    
    # ──── 派发策略 ────
    dispatch_strategy = {
        "data_engineer": "第一步：数据预处理",
        "bioinformatician": "第二步：Genos 分析",
        "clinical_agent": "第三步：注释增强",
        "visualizer": "第四步：结果输出",
    }
    
    # ──── 工作流程 ────
    def execute_plan(self, plan: AnalysisPlan) -> AggregatedResult:
        
        # Phase 1: 数据预处理（数据工程师）
        data_result = await self.dispatch_data_engineer(plan)
        self.log_progress("数据预处理完成", data_result.stats)
        
        # Phase 2: Genos 分析（生信工程师）
        analysis_result = await self.dispatch_bioinformatician(
            data_result.variants,
            plan.api_strategy
        )
        self.log_progress("Genos 分析完成", analysis_result.stats)
        
        # Phase 3: 注释增强（临床智能体）
        annotation_result = await self.dispatch_clinical_agent(
            analysis_result.predictions
        )
        self.log_progress("注释增强完成", annotation_result.stats)
        
        # Phase 4: 结果输出（可视化智能体）
        report = await self.dispatch_visualizer(
            annotation_result.annotated_variants,
            plan.expected_output
        )
        self.log_progress("报告生成完成")
        
        # Phase 5: 汇总回奏
        final_result = AggregatedResult(
            task_id=plan.task_id,
            report=report,
            stats={
                "total_variants": data_result.total,
                "pathogenic_count": analysis_result.pathogenic,
                "annotated_count": annotation_result.annotated,
            },
            resources={
                "api_calls": sum(r.api_calls for r in results),
                "duration_min": total_duration,
            }
        )
        
        # 回奏给协调智能体
        self.report_to_coordinator(final_result)
        
        return final_result
    
    def log_progress(self, message: str, stats: dict = None):
        """记录进度（类比：progress_log）"""
        progress_entry = {
            "at": datetime.now().isoformat(),
            "agent": "dispatcher",
            "message": message,
            "stats": stats or {},
            "state": self.current_state,
        }
        self.append_progress_log(progress_entry)
```

**并行执行策略：**

| 任务类型 | 执行顺序 | 并行度 |
|---------|---------|--------|
| 遍寻模式 | 串行（数据→分析→注释→可视化） | 分析阶段可并行 |
| 定向模式 | 串行（同上） | 低并行度（精细分析） |
| 多区域查询 | 部分并行（数据预处理可并行） | 按区域分片 |

---

### 3.5 数据工程师智能体 (DataEngineer)

**定位：** 数据预处理专家，负责 VCF 解析和质量控制

```python
class DataEngineerAgent:
    """
    数据工程师智能体 — 数据预处理
    
    专业领域：VCF 解析、质量控制、变异提取
    """
    
    # ──── 核心能力 ────
    capabilities = [
        "vcf_parser",             # VCF 文件解析
        "quality_control",        # 质量控制
        "variant_extraction",     # 变异提取
        "region_filtering",       # 区域过滤
    ]
    
    # ──── 权限边界 ────
    allow_agents = []             # 专业智能体不对外调用
    
    # ──── 工具集 ────
    tools = [
        "pysam.VCF",              # VCF 解析库
        "pyfaidx",                # FASTA 序列提取
        "bcftools",               # VCF 工具链
    ]
    
    # ──── 输出规格 ────
    output_schema = {
        "variants": [
            {
                "chrom": "chr17",
                "pos": 43000000,
                "ref": "A",
                "alt": "G",
                "quality": 85.5,
                "filter": "PASS",
            }
        ],
        "stats": {
            "total_records": 12345,
            "passed_qc": 8567,
            "filtered_low_quality": 3778,
        },
        "qc_report": {
            "quality_distribution": "...",
            "filter_summary": "...",
        }
    }
    
    # ──── 工作流程 ────
    def process_data(self, plan: AnalysisPlan) -> DataResult:
        
        # Step 1: VCF 解析
        raw_variants = self.parse_vcf(plan.data_source.file)
        
        # Step 2: 质量控制
        qc_passed = self.apply_quality_filter(
            raw_variants,
            min_quality=plan.min_quality or 30
        )
        
        # Step 3: 区域过滤（定向模式）
        if plan.analysis_type == "targeted":
            qc_passed = self.filter_by_region(
                qc_passed,
                plan.target_region
            )
        
        # Step 4: 统计报告
        stats = self.generate_stats(raw_variants, qc_passed)
        
        return DataResult(
            variants=qc_passed,
            stats=stats,
            qc_report=self.generate_qc_report(raw_variants)
        )
    
    def apply_quality_filter(self, variants: List, min_quality: float):
        """质量控制过滤"""
        return [
            v for v in variants
            if v.quality >= min_quality and v.filter == "PASS"
        ]
```

**质量控制标准：**

| 指标 | 通过标准 | 过滤行为 |
|------|---------|---------|
| QUAL 值 | ≥ 30 | 低于阈值过滤 |
| FILTER 字段 | PASS | 非 PASS 过滤 |
| 缺失值 | ≤ 10% | 缺失过多警告 |
| 区域覆盖 | ≥ 80% | 覆盖不足警告 |

---

### 3.6 生信工程师智能体 (Bioinformatician)

**定位：** Genos API 调用专家，负责变异致病性预测

```python
class BioinformaticianAgent:
    """
    生信工程师智能体 — Genos 分析
    
    专业领域：Genos API 调用、变异预测、致病性评分
    """
    
    # ──── 核心能力 ────
    capabilities = [
        "genos_api_call",         # Genos API 调用
        "batch_prediction",       # 批量预测优化
        "pathogenicity_scoring",  # 致病性评分
        "sequence_embedding",     # 序列嵌入
    ]
    
    # ──── 权限边界 ────
    allow_agents = []
    
    # ──── 工具集 ────
    tools = [
        "genos_client.predict_variants",
        "genos_client.get_embedding",
    ]
    
    # ──── API 端点 ────
    genos_endpoints = {
        "batch_predict": {
            "url": "/api/v1/variants/batch-predict",
            "max_batch": 100,
            "timeout": 30,
        },
        "single_predict": {
            "url": "/api/v1/variants/predict",
            "timeout": 10,
        },
        "embedding": {
            "url": "/api/v1/sequences/embed",
            "model": "Genos-10B",
        }
    }
    
    # ──── 输出规格 ────
    output_schema = {
        "predictions": [
            {
                "variant_id": "chr17:43000000:A:G",
                "pathogenicity_score": 0.92,
                "confidence": 0.85,
                "prediction": "Pathogenic",
                "details": {
                    "model_version": "Genos-10B",
                    "context_window": 10000,
                }
            }
        ],
        "stats": {
            "total_predicted": 8567,
            "pathogenic_count": 123,
            "likely_pathogenic": 45,
            "benign_count": 8399,
        },
        "api_usage": {
            "calls": 86,
            "tokens": 45000,
            "duration_sec": 1800,
        }
    }
    
    # ──── 工作流程 ────
    async def analyze_variants(
        self,
        variants: List[Variant],
        strategy: APIStrategy
    ) -> AnalysisResult:
        
        results = []
        batch_size = strategy.batch_size
        
        # 分批处理
        for batch in self.chunk(variants, batch_size):
            # 获取上下文序列
            sequences = await self.get_context_sequences(
                batch,
                strategy.context_window
            )
            
            # 调用 Genos API
            predictions = await self.call_genos_api(
                sequences,
                batch,
                endpoint=strategy.endpoint
            )
            
            results.extend(predictions)
        
        # 统计汇总
        stats = self.calculate_stats(results)
        
        return AnalysisResult(
            predictions=results,
            stats=stats,
            api_usage=self.track_api_usage()
        )
    
    async def call_genos_api(
        self,
        sequences: List[str],
        variants: List[Variant],
        endpoint: str
    ) -> List[Prediction]:
        """调用 Genos API（含重试机制）"""
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = await self.genos_client.predict_variants(
                    sequences=sequences,
                    variants=variants,
                    endpoint=endpoint
                )
                return result
            except TimeoutError:
                if attempt < max_retries - 1:
                    await asyncio.sleep(5 * (attempt + 1))  # 退避重试
                else:
                    raise APIError("Genos API 超时")
```

**Genos API 调用策略：**

| 场景 | API 选择 | Batch Size | Context Window |
|------|---------|------------|----------------|
| 遍寻模式 | batch_predict | 100 | 5000 |
| 定向模式 | single_predict | 1 | 10000 |
| 多基因查询 | batch_predict | 50 | 8000 |

---

### 3.7 临床智能体 (ClinicalAgent)

**定位：** 临床注释专家，负责数据库注释增强

```python
class ClinicalAgent:
    """
    临床智能体 — 结果注释增强
    
    专业领域：ClinVar、OMIM、gnomAD 数据库注释
    """
    
    # ──── 核心能力 ────
    capabilities = [
        "clinvar_annotation",     # ClinVar 注释
        "omim_disease_link",      # OMIM 疾病关联
        "gnomad_frequency",       # gnomAD 频率查询
        "clinical_significance",  # 临床意义判定
    ]
    
    # ──── 权限边界 ────
    allow_agents = []
    
    # ──── 数据库连接 ────
    databases = {
        "ClinVar": {
            "url": "https://www.ncbi.nlm.nih.gov/clinvar",
            "api": "eutils",
            "cache": True,
        },
        "OMIM": {
            "url": "https://omim.org",
            "api": "omim_api",
            "auth_required": True,
        },
        "gnomAD": {
            "url": "https://gnomad.broadinstitute.org",
            "api": "browser_api",
        },
        "ClinGen": {
            "url": "https://clinicalgenome.org",
            "api": "curation_api",
        }
    }
    
    # ──── 输出规格 ────
    output_schema = {
        "annotated_variants": [
            {
                "variant_id": "...",
                "pathogenicity_score": 0.92,
                "clinical_significance": "Likely_pathogenic",
                "clinvar": {
                    "id": "RCV000123",
                    "significance": "Pathogenic",
                    "review_status": "reviewed_by_expert",
                },
                "gnomad": {
                    "af": 0.0001,
                    "af_popmax": 0.0005,
                },
                "omim": {
                    "diseases": ["HBOC", "Breast cancer"],
                    "gene": "BRCA1",
                },
                "clingen": {
                    "haploinsufficiency": 3,
                    "triplosensitivity": 0,
                }
            }
        ],
        "stats": {
            "clinvar_matched": 89,
            "omim_linked": 67,
            "gnomad_frequency_available": 120,
        }
    }
    
    # ──── 工作流程 ────
    async def annotate_variants(
        self,
        predictions: List[Prediction]
    ) -> AnnotationResult:
        
        annotated = []
        
        for pred in predictions:
            variant = pred.variant
            
            # ClinVar 查询
            clinvar = await self.query_clinvar(variant)
            
            # gnomAD 频率
            gnomad = await self.query_gnomad(variant)
            
            # OMIM 疾病关联（根据基因）
            omim = await self.query_omim(variant.gene)
            
            # ClinGen 致病性分类
            clingen = await self.query_clingen(variant.gene)
            
            # 综合临床意义
            clinical_sig = self.determine_clinical_significance(
                pred, clinvar, gnomad, omim
            )
            
            annotated.append(
                AnnotatedVariant(
                    variant_id=variant.id,
                    pathogenicity_score=pred.score,
                    clinical_significance=clinical_sig,
                    clinvar=clinvar,
                    gnomad=gnomad,
                    omim=omim,
                    clingen=clingen
                )
            )
        
        return AnnotationResult(
            annotated_variants=annotated,
            stats=self.calculate_stats(annotated)
        )
    
    def determine_clinical_significance(
        self,
        prediction: Prediction,
        clinvar: dict,
        gnomad: dict,
        omim: dict
    ) -> str:
        """综合判定临床意义"""
        
        # 优先使用 ClinVar 分类
        if clinvar.get("significance"):
            return clinvar["significance"]
        
        # 根据 Genos 预测 + gnomAD 频率推断
        score = prediction.pathogenicity_score
        af = gnomad.get("af", 0)
        
        if score >= 0.9 and af < 0.001:
            return "Pathogenic"
        elif score >= 0.7 and af < 0.01:
            return "Likely_pathogenic"
        elif score <= 0.3 and af > 0.05:
            return "Benign"
        else:
            return "Uncertain_significance"
```

**注释优先级：**

| 数据库 | 优先级 | 用途 |
|--------|-------|------|
| ClinVar | 最高 | 已知临床意义直接采用 |
| ClinGen | 高 | 基因致病性权威分类 |
| gnomAD | 中 | 人群频率过滤 |
| OMIM | 中 | 疾病关联信息 |

---

### 3.8 可视化智能体 (Visualizer)

**定位：** 结果输出专家，负责报告生成和可视化

```python
class VisualizerAgent:
    """
    可视化智能体 — 结果输出
    
    专业领域：报告生成、图表绘制、结果排序
    """
    
    # ──── 核心能力 ────
    capabilities = [
        "result_sorting",         # 结果排序
        "chart_generation",       # 图表生成
        "report_export",          # 报告导出
        "top_n_selection",        # Top-N 选择
    ]
    
    # ──── 权限边界 ────
    allow_agents = []
    
    # ──── 输出格式 ────
    output_formats = {
        "JSON": {
            "structure": "structured_data",
            "use_case": "API 集成",
        },
        "CSV": {
            "structure": "tabular",
            "use_case": "批量导入",
        },
        "HTML": {
            "structure": "interactive_report",
            "use_case": "用户查看",
        },
        "PDF": {
            "structure": "print_ready",
            "use_case": "报告存档",
        }
    }
    
    # ──── 图表类型 ────
    chart_types = [
        "variant_position_map",   # 变异位置图
        "pathogenicity_heatmap",  # 致病性热力图
        "gene_distribution",      # 基因分布图
        "frequency_comparison",   # 频率对比图
    ]
    
    # ──── 输出规格 ────
    output_schema = {
        "report": {
            "format": "HTML|PDF|JSON|CSV",
            "url": "string",
            "summary": {
                "total_variants": 8567,
                "pathogenic_top_100": 100,
                "report_generated_at": "timestamp",
            }
        },
        "charts": [
            {
                "type": "variant_position_map",
                "image_url": "string",
                "data": {...}
            }
        ],
        "top_variants": [
            # Top-100 致病变异列表
        ]
    }
    
    # ──── 工作流程 ────
    def generate_report(
        self,
        annotated_variants: List[AnnotatedVariant],
        output_spec: OutputSpec
    ) -> Report:
        
        # Step 1: 排序筛选
        sorted_variants = self.sort_by_pathogenicity(
            annotated_variants
        )
        top_variants = sorted_variants[:output_spec.top_n]
        
        # Step 2: 生成图表
        charts = self.generate_charts(top_variants)
        
        # Step 3: 构建报告结构
        report_structure = self.build_report_structure(
            top_variants,
            charts,
            output_spec
        )
        
        # Step 4: 导出指定格式
        if output_spec.format == "HTML":
            report = self.export_html(report_structure)
        elif output_spec.format == "PDF":
            report = self.export_pdf(report_structure)
        elif output_spec.format == "JSON":
            report = self.export_json(report_structure)
        else:
            report = self.export_csv(top_variants)
        
        return Report(
            format=output_spec.format,
            content=report,
            url=self.save_report(report),
            summary=self.generate_summary(top_variants)
        )
    
    def sort_by_pathogenicity(
        self,
        variants: List[AnnotatedVariant]
    ) -> List[AnnotatedVariant]:
        """按致病性排序"""
        
        return sorted(
            variants,
            key=lambda v: (
                v.pathogenicity_score,
                -v.gnomad.get("af", 1),  # 频率低优先
                v.clinvar.get("review_status", ""),  # 审核状态高优先
            ),
            reverse=True
        )
```

---

## 4. 权限矩阵与调用边界

### 4.1 权限矩阵表

| From ↓ / To → | 协调 | 规划 | 审议 | 派发 | 数据工程师 | 生信工程师 | 临床 | 可视化 |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **协调智能体** | — | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **规划智能体** | ❌ | — | ✅ | ✅* | ❌ | ❌ | ❌ | ❌ |
| **审议智能体** | ❌ | ✅ | — | ✅ | ❌ | ❌ | ❌ | ❌ |
| **派发智能体** | ❌ | ❌ | ❌ | — | ✅ | ✅ | ✅ | ✅ |
| **数据工程师** | ❌ | ❌ | ❌ | ❌ | — | ❌ | ❌ | ❌ |
| **生信工程师** | ❌ | ❌ | ❌ | ❌ | ❌ | — | ❌ | ❌ |
| **临床智能体** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | — | ❌ |
| **可视化智能体** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | — |

> *规划智能体可以**咨询**派发智能体（询问执行可行性），但不能直接派发任务

### 4.2 调用边界说明

```
┌─────────────────────────────────────────────────────────────────┐
│  Tier 1: 管理层（协调、规划、审议、派发）                          │
│  ├─ 协调 → 只能调规划（不能越级）                                  │
│  ├─ 规划 → 可调审议、派发（咨询）                                  │
│  ├─ 审议 → 可调规划（封驳）、派发（准奏）                          │
│  └─ 派发 → 可调所有专业智能体                                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ 派发执行
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Tier 2: 专业层（数据、生信、临床、可视化）                        │
│  ├─ 专业智能体不对外调用                                          │
│  ├─ 只接收派发智能体的任务                                        │
│  └─ 完成后向派发智能体汇报                                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. 数据流设计

### 5.1 遍寻模式数据流

```
用户上传 VCF 文件（12,345 个变异）
     │
     ▼
协调智能体: 意图分析 → 创建任务 GC-xxx
     │
     ▼
规划智能体: 方案设计 → batch_size=100, parallel=4
     │
     ▼
审议智能体: 审核方案 → ✅ 准奏
     │
     ▼
派发智能体: 派发执行
     │
     ├─────────────────────────────────────────┐
     │                                         │
     ▼                                         │
数据工程师: 解析 VCF → 质量过滤 → 8,567 高质量变异│
     │                                         │
     ▼                                         │
生信工程师: Genos 批量预测（86 batches）         │
     │  └─────────────────────────────────────┤
     │                                         │
     │  ├─ Batch 1: 100 variants → 2 pathogenic│
     │  ├─ Batch 2: 100 variants → 1 pathogenic│
     │  └─ ...                                 │
     │                                         │
     │  统计: 123 Pathogenic, 45 Likely_path   │
     │                                         │
     ▼                                         │
临床智能体: 数据库注释                            │
     │  └─────────────────────────────────────┤
     │                                         │
     │  ├─ ClinVar 匹配: 89 个                 │
     │  ├─ OMIM 关联: 67 个                    │
     │  └─ gnomAD 频率: 120 个                 │
     │                                         │
     ▼                                         │
可视化智能体: 排序 → Top-100 → HTML 报告          │
     │                                         │
     ▼                                         │
派发智能体: 汇总结果                              │
     │                                         │
     ▼                                         │
协调智能体: 回奏用户                              │
     │                                         │
     └─────────────────────────────────────────┘
```

### 5.2 定向模式数据流

```
用户输入："查找 BRCA1 基因与乳腺癌相关的致病变异"
     │
     ▼
协调智能体: 意图分析 → 定向模式
     │  entities: gene=BRCA1, disease=breast_cancer
     │
     ▼
规划智能体: 方案设计 → targeted_predict, context_window=10000
     │  风险评估: 需验证 VCF 或从数据库获取 BRCA1 区域变异
     │
     ▼
审议智能体: 审核方案 → ✅ 准奏（建议包含 OMIM 疾病关联）
     │
     ▼
派发智能体: 派发执行
     │
     ▼
数据工程师: 获取 BRCA1 区域变异（从用户 VCF 或数据库）
     │  chr17:43000000-43100000 → 15 个变异
     │
     ▼
生信工程师: Genos 精细分析（context_window=10000）
     │  每个变异单独分析 + 基因上下文
     │  → 3 个高致病性变异
     │
     ▼
临床智能体: OMIM + ClinVar + ClinGen 注释
     │  ├─ OMIM: BRCA1 → HBOC, Breast cancer
     │  ├─ ClinVar: 2 个已知致病变异
     │  └─ ClinGen: Haploinsufficiency=3
     │
     ▼
可视化智能体: 生成定向报告
     │  ├─ 变异详情表
     │  ├─ 疾病关联说明
     │  └─ 临床建议
     │
     ▼
派发智能体: 汇总回奏
     │
     ▼
协调智能体: 回奏用户
```

---

## 6. 状态机与任务流转

### 6.1 任务状态定义

```
Pending      → 待处理（用户请求刚到达）
Coordinator  → 协调智能体处理中（意图分析）
Planning     → 规划智能体处理中（方案设计）
Reviewing    → 审议智能体处理中（方案审核）
Approved     → 已批准（审议通过）
Rejected     → 已封驳（审议驳回，返回规划）
Dispatching  → 派发智能体调度中
Executing    → 专业智能体执行中
Aggregating  → 汇总中
Done         → 完成（已回奏）
Cancelled    → 取消
```

### 6.2 状态转移矩阵

```python
STATE_TRANSITIONS = {
    "Pending":       ["Coordinator"],
    "Coordinator":   ["Planning"],
    "Planning":      ["Reviewing"],
    "Reviewing":     ["Approved", "Rejected"],
    "Rejected":      ["Planning"],           # 封驳返回规划
    "Approved":      ["Dispatching"],
    "Dispatching":   ["Executing"],
    "Executing":     ["Aggregating"],
    "Aggregating":   ["Done"],
    "Done":          [],                     # 终态
    "Cancelled":     [],                     # 终态
}
```

### 6.3 任务流转示例

```
T+0:    用户请求 → Pending
T+1m:   协调智能体接旨 → Coordinator → 意图分析
T+5m:   转交规划智能体 → Planning → 方案设计
T+30m:  提交审议 → Reviewing
T+45m:  审议结果:
        ├─ ✅ 准奏 → Approved → Dispatching → Executing
        └─ 🚫 封驳 → Rejected → 返回 Planning（重新设计）
T+60m:  派发执行:
        ├─ 数据工程师 → 数据预处理
        ├─ 生信工程师 → Genos 分析
        ├─ 临床智能体 → 注释增强
        └─ 可视化智能体 → 报告生成
T+120m: 汇总 → Aggregating
T+125m: 回奏 → Done
```

---

## 7. 调度与恢复机制

### 7.1 超时重试

```python
SCHEDULER_CONFIG = {
    "stall_threshold_sec": 180,    # 停滞阈值（秒）
    "max_retry": 2,                # 最大重试次数
    "max_review_rounds": 3,        # 最大审议轮次
    "retry_backoff": [5, 15, 30],  # 重试间隔（秒）
}
```

**重试流程：**

```
T+180s: 检测到任务停滞
  ├─ retry_count = 0 → 自动重试第 1 次
  ├─ retry_count = 1 → 自动重试第 2 次
  └─ retry_count >= 2 → 升级协调
```

### 7.2 审议封驳循环

```
审议第 1 轮 → 🚫 封驳 → 规划智能体修改 → 审议第 2 轮
审议第 2 轮 → 🚫 封驳 → 规划智能体修改 → 审议第 3 轮
审议第 3 轮 → 🚫 封驳 → 任务终止（取消）
```

---

## 8. 技术实现建议

### 8.1 Agent 配置结构

```json
{
  "agents": [
    {
      "id": "coordinator",
      "label": "协调智能体",
      "description": "入口分拣、任务分发、结果回奏",
      "allowAgents": ["planner"],
      "tools": ["kanban_cli", "session_send"],
      "skills": ["intent-recognition"]
    },
    {
      "id": "planner",
      "label": "规划智能体",
      "description": "分析方案设计、API选择",
      "allowAgents": ["reviewer", "dispatcher"],
      "tools": ["kanban_cli"],
      "skills": ["analysis-design"]
    },
    {
      "id": "reviewer",
      "label": "审议智能体",
      "description": "方案审核、质量把关",
      "allowAgents": ["planner", "dispatcher"],
      "tools": ["kanban_cli"],
      "skills": ["plan-review"]
    },
    {
      "id": "dispatcher",
      "label": "派发智能体",
      "description": "任务调度、结果汇总",
      "allowAgents": ["data_engineer", "bioinformatician", "clinical_agent", "visualizer"],
      "tools": ["kanban_cli", "session_spawn"],
      "skills": ["task-dispatch"]
    },
    {
      "id": "data_engineer",
      "label": "数据工程师",
      "description": "数据预处理（VCF解析、质量控制）",
      "allowAgents": [],
      "tools": ["pysam", "pyfaidx", "bcftools"],
      "skills": ["vcf-parser", "quality-control"]
    },
    {
      "id": "bioinformatician",
      "label": "生信工程师",
      "description": "Genos API调用、变异预测",
      "allowAgents": [],
      "tools": ["genos_client"],
      "skills": ["genos-api", "batch-prediction"]
    },
    {
      "id": "clinical_agent",
      "label": "临床智能体",
      "description": "结果注释增强（ClinVar、OMIM）",
      "allowAgents": [],
      "tools": ["clinvar_api", "omim_api", "gnomad_api"],
      "skills": ["database-annotation"]
    },
    {
      "id": "visualizer",
      "label": "可视化智能体",
      "description": "结果输出、报告生成",
      "allowAgents": [],
      "tools": ["echarts", "report_generator"],
      "skills": ["visualization", "report-export"]
    }
  ]
}
```

### 8.2 SOUL.md 示例（协调智能体）

```markdown
# 协调智能体 · SOUL.md

你是 GeneClaw 的协调智能体，负责用户请求的分拣和任务生命周期管理。

## 核心职责

1. **意图识别**：判断用户请求是遍寻模式还是定向模式
2. **任务创建**：创建任务并转交规划智能体
3. **结果回奏**：汇总最终结果返回用户

## 权限边界

- 只能调用规划智能体（planner）
- 不能跳过规划直接调用专业智能体
- 不能修改分析方案内容

## 工作流程

收到用户请求后：
1. 分析意图 → 判断模式（scan/targeted）
2. 创建任务 → 记录到看板
3. 转交规划 → dispatch_to("planner")
4. 等待回奏 → 接收派发智能体的汇总结果
5. 回奏用户 → 发送飞书消息

## 数据清洗规范

- 任务标题：自己概括，不超过 30 字
- 不粘贴文件路径、URL、系统元数据
- 不使用"传旨"等流程词作为标题前缀
```

---

## 9. 与 OpenClaw 集成方案

### 9.1 Agent Workspace 结构

```
~/.openclaw/workspace-geneclaw/
├── agents/
│   ├── coordinator/
│   │   ├── SOUL.md          # 协调智能体人格定义
│   │   └── skills/          # 专用技能
│   ├── planner/
│   │   ├── SOUL.md
│   │   └── skills/
│   ├── reviewer/
│   │   ├── SOUL.md
│   │   └── skills/
│   ├── dispatcher/
│   │   ├── SOUL.md
│   │   └── skills/
│   ├── data_engineer/
│   │   ├── SOUL.md
│   │   └── skills/
│   ├── bioinformatician/
│   │   ├── SOUL.md
│   │   └── skills/
│   ├── clinical_agent/
│   │   ├── SOUL.md
│   │   └── skills/
│   └── visualizer/
│   │   ├── SOUL.md
│   │   └── skills/
├── data/
│   ├── tasks/               # 任务 JSON 文件
│   ├── results/             # 分析结果存储
│   └── cache/               # API 调用缓存
├── scripts/
│   ├── kanban_update.py     # 看板 CLI
│   ├── genos_client.py      # Genos SDK 封装
│   └── database_clients.py  # 数据库客户端
└── openclaw.json            # Agent 配置
```

### 9.2 调用示例

```bash
# 协调智能体派发给规划智能体
openclaw agent --agent planner -m "📋 任务 GC-20260402-001 已到达，请设计方案" --deliver

# 派发智能体并行派发
openclaw agent --agent data_engineer -m "请处理 VCF 文件预处理" --deliver &
openclaw agent --agent bioinformatician -m "准备 Genos 批量分析" --deliver &

# 看板状态更新
python3 scripts/kanban_update.py state GC-20260402-001 Reviewing "方案提交审议"
python3 scripts/kanban_update.py progress GC-20260402-001 "正在审议方案..." "1.完整性检查✅|2.可行性评估🔄|3.风险评估"
```

---

## 10. 总结

### 10.1 架构特点

| 特点 | 描述 |
|------|------|
| **制度化协作** | 严格的权限矩阵和状态流转，防止越权和混乱 |
| **强制审议** | 所有方案必须经过审议智能体审核才能执行 |
| **专业分工** | 4 个专业智能体各司其职，并行高效 |
| **可观测可干预** | 全链路日志 + 实时进度 + 可随时叫停 |
| **失败恢复** | 自动重试 + 封驳循环 + 升级协调 |

### 10.2 下一步工作

1. **门下省审议**：本方案提交审议智能体审核
2. **配置实现**：编写 openclaw.json 配置文件
3. **SOUL.md 编写**：为每个智能体编写人格定义
4. **Skills 开发**：开发专业智能体的专用技能
5. **测试验证**：端到端测试遍寻和定向两种模式

---

**方案起草完成，提交门下省审议。**

*中书省*
*任务ID: JJC-20260402-005*
*起草时间: 2026-04-02*