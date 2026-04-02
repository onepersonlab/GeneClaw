# GeneClaw 🧬

**AI-powered gene analysis multi-agent framework**

基于 Genos 基因组基础模型的多智能体基因分析框架，让每个人都能简单进行基因相关分析。

---

## 项目愿景

让保罗为罗西做的事（花费数万澳元、三个月时间），变成普通用户一句话就能完成的任务。

> 参考：[一只狗的 mRNA 癌症疫苗故事](https://zhuanlan.zhihu.com/p/...) — 主人用 ChatGPT + AI 自研 mRNA 疫苗拯救患癌爱犬

---

## 开发阶段

| 阶段 | 功能 | 状态 |
|-----|------|-----|
| **Phase 1** | 致病靶点发现 | 🔄 规划中 |
| **Phase 2** | 通路与机制分析 | 待开发 |
| **Phase 3** | 药物/疗法匹配 | 待开发 |
| **Phase 4** | 治疗方案生成 | 待开发 |

---

## Phase 1: 致病靶点发现

### 核心功能

**输入：** 基因测序数据（VCF/FASTA/BAM）

**输出：** 致病变异列表 + 置信度评分 + 数据库注释

### 两种查询模式

| 模式 | 描述 | 用户场景 |
|-----|------|---------|
| **遍寻模式** | 全面扫描所有变异，按致病性排序 | "帮我找出所有可能致病的突变" |
| **定向模式** | 针对特定疾病，查找关键靶点 | "查找与乳腺癌相关的 BRCA1/2 突变" |

---

## 技术架构

详见 [docs/phase1-design.md](docs/phase1-design.md)

---

## 相关项目

- [Genos](https://github.com/BGI-HangzhouAI/Genos) - 人类基因组基础模型
- OpenClaw - 多智能体框架基础设施

---

## License

MIT