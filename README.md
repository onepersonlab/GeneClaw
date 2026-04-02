# GeneClaw 🧬

**AI-powered gene analysis multi-agent framework**

基于 Genos 基因组基础模型的多智能体基因分析框架，支持遍寻和定向两种突变位点分析模式。

---

## 项目定位

GeneClaw 采用**制度化的多智能体协作架构**，实现从基因测序数据到致病变异列表的自动化分析流程。

**核心目标：**
- **遍寻模式**：全面扫描基因测序数据，找出所有可能的致病变异
- **定向模式**：针对特定疾病，查找相关的突变位点

---

## 八大智能体架构

### 决策层 (Tier 1)

| 智能体 | ID | 职责 |
|--------|-----|------|
| 协调智能体 | coordinator | 入口分拣、意图识别、任务创建、结果回奏 |
| 规划智能体 | planner | 分析方案设计、API选择、数据流规划 |
| 审议智能体 | reviewer | 方案审核、质量把关、可封驳 |
| 派发智能体 | dispatcher | 任务调度、执行监控、结果汇总 |

### 执行层 (Tier 2)

| 智能体 | ID | 职责 |
|--------|-----|------|
| 数据工程师 | data_engineer | VCF解析、质量控制、变异提取 |
| 生信工程师 | bioinfo_engineer | Genos API调用、变异预测、致病性评分 |
| 临床智能体 | clinical_expert | ClinVar/OMIM/gnomAD注释、临床意义增强 |
| 报告智能体 | reporter_agent | 结果排序、图表生成、报告导出 |

---

## 交互流程

```
用户请求 → 协调智能体 → 规划智能体 → 审议智能体 → 派发智能体 → 专业智能体 → 结果回奏
```

---

## 目录结构

```
GeneClaw/
├── agents/              # 八大智能体定义
│   ├── coordinator/
│   ├── planner/
│   ├── reviewer/
│   ├── dispatcher/
│   ├── data_engineer/
│   ├── bioinfo_engineer/
│   ├── clinical_expert/
│   └── reporter_agent/
├── agents.json          # 智能体配置
├── dashboard/           # 看板前端
├── edict/               # 后端服务
├── scripts/             # 脚本
└── docs/                # 文档
```

---

## 技术栈

- **前端**: React + TypeScript + ECharts
- **后端**: Python + FastAPI + PostgreSQL + Redis
- **基因模型**: Genos SDK
- **多智能体框架**: 基于 OpenClaw

---

## 相关项目

- [Genos](https://github.com/BGI-HangzhouAI/Genos) - 人类基因组基础模型
- [edict](https://github.com/cft0808/edict) - 三省六部制多智能体框架

---

## License

MIT
