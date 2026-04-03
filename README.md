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

### 决策层 (Decision Layer)

| 智能体 | ID | 职责 |
|--------|-----|------|
| 协调智能体 | coordinator | 入口分拣、意图识别、任务创建、结果回奏 |
| 规划智能体 | planner | 分析方案设计、API选择、数据流规划 |
| 审议智能体 | reviewer | 方案审核、质量把关、可封驳 |
| 派发智能体 | dispatcher | 任务调度、执行监控、结果汇总 |

### 执行层 (Execution Layer)

| 智能体 | ID | 职责 | 执行顺序 |
|--------|-----|------|----------|
| 数据工程师 | data_engineer | VCF解析、质量控制、变异提取 | 第1步 |
| 生信工程师 | bioinfo_engineer | Genos API调用、变异预测、致病性评分 | 第2步 |
| 临床智能体 | clinical_expert | ClinVar/OMIM/gnomAD注释、临床意义增强 | 第3步 |
| 报告智能体 | reporter_agent | 结果排序、图表生成、报告导出 | 第4步 |

---

## 通信架构

### 完整通信流程

```
用户
 ↓
协调智能体 ←─────────────────────┐
 ↓ 分拣                          │ 回奏结果
规划智能体                        │
 ↓ 规划                          │
审议智能体                        │
 ↓ 准奏/封驳                     │
派发智能体                        │
 ↓ 广播任务                      │
 ├→ 数据工程师 ──→ 生信工程师 ──→ 临床智能体 ──→ 报告智能体
      ↓ 结果传递    ↓ 结果传递     ↓ 结果传递
```

### 通信机制

**双重通信模式：**

1. **广播机制**：派发智能体向所有执行层智能体广播任务信息，让每个执行者都知道整体任务
2. **链式传递**：执行层按顺序传递处理结果，形成流水线

### allowAgents 配置

| 智能体 | 允许调用 | 通信目的 |
|--------|----------|----------|
| coordinator | planner | 分拣后转规划 |
| planner | reviewer, dispatcher | 方案送审/直接派发 |
| reviewer | planner, dispatcher | 封驳/准奏 |
| dispatcher | 4个执行层 | 广播任务 |
| data_engineer | bioinfo_engineer | 结果传递 |
| bioinfo_engineer | clinical_expert | 结果传递 |
| clinical_expert | reporter_agent | 结果传递 |
| reporter_agent | coordinator | **回奏结果** |

### 状态流转

```
Pending → Coordinator → Planning → Reviewing → Approved → Dispatching → Executing → Aggregating → Done
                              ↓ Rejected ↗ Planning (封驳重做)
```

---

## 目录结构

```
GeneClaw/
├── agents/              # 八大智能体定义
│   ├── coordinator/     # 协调智能体
│   ├── planner/         # 规划智能体
│   ├── reviewer/        # 审议智能体
│   ├── dispatcher/      # 派发智能体
│   ├── data_engineer/   # 数据工程师
│   ├── bioinfo_engineer/# 生信工程师
│   ├── clinical_expert/ # 临床智能体
│   └── reporter_agent/  # 报告智能体
├── agents.json          # 智能体通信配置
├── install.sh           # 一键安装脚本
├── uninstall.sh         # 卸载脚本
├── dashboard/           # 看板前端
│   └── server.py        # 看板服务器 (端口 7891)
├── edict/               # 后端服务
│   ├── backend/         # FastAPI + PostgreSQL
│   └── frontend/        # React + TypeScript
├── scripts/             # 工具脚本
│   ├── kanban_update.py # 看板状态更新
│   ├── sync_agent_config.py
│   └── run_loop.sh      # 数据刷新循环
└── docs/                # 文档
```

---

## 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/onepersonlab/GeneClaw.git
cd GeneClaw

# 一键安装
bash install.sh
```

### 启动服务

```bash
# 启动数据刷新循环
bash scripts/run_loop.sh &

# 启动看板服务器
python3 dashboard/server.py

# 访问看板
open http://127.0.0.1:7891
```

---

## 配置文件

### agents.json

核心配置文件，定义智能体通信关系：

```json
{
  "agents": [...],
  "permissions": {
    "matrix": {...}
  },
  "executionOrder": {
    "sequence": ["data_engineer", "bioinfo_engineer", "clinical_expert", "reporter_agent"]
  }
}
```

### OpenClaw 集成

安装后自动注册到 `~/.openclaw/openclaw.json`：

```json
{
  "agents": {
    "list": [
      {"id": "coordinator", "workspace": "~/.openclaw/workspace-coordinator", ...},
      ...
    ]
  }
}
```

---

## 技术栈

- **前端**: React + TypeScript + ECharts
- **后端**: Python + FastAPI + PostgreSQL + Redis
- **基因模型**: Genos SDK
- **多智能体框架**: OpenClaw

---

## 相关项目

- [Genos](https://github.com/BGI-HangzhouAI/Genos) - 人类基因组基础模型
- [OpenClaw](https://github.com/openclaw/openclaw) - 多智能体框架

---

## License

MIT