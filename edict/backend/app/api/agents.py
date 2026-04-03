"""Agents API — Agent 配置和状态查询。"""

import json
import logging
from pathlib import Path

from fastapi import APIRouter

log = logging.getLogger("edict.api.agents")
router = APIRouter()

# Agent 元信息（对应 agents/ 目录下的 SOUL.md）
AGENT_META = {
    # 决策层
    "coordinator": {"name": "协调智能体", "role": "入口分拣与意图识别", "icon": "🎯"},
    "planner": {"name": "规划智能体", "role": "方案设计与API选择", "icon": "📋"},
    "reviewer": {"name": "审议智能体", "role": "质量把关与封驳", "icon": "🔍"},
    "dispatcher": {"name": "派发智能体", "role": "任务调度与结果汇总", "icon": "📮"},
    # 执行层
    "data_engineer": {"name": "数据工程师", "role": "VCF解析与质量控制", "icon": "📊"},
    "bioinfo_engineer": {"name": "生信工程师", "role": "Genos分析", "icon": "🧬"},
    "clinical_expert": {"name": "临床智能体", "role": "数据库注释", "icon": "🏥"},
    "reporter_agent": {"name": "报告智能体", "role": "结果输出", "icon": "📈"},
}


@router.get("")
async def list_agents():
    """列出所有可用 Agent。"""
    agents = []
    for agent_id, meta in AGENT_META.items():
        agents.append({
            "id": agent_id,
            **meta,
        })
    return {"agents": agents}


@router.get("/{agent_id}")
async def get_agent(agent_id: str):
    """获取 Agent 详情。"""
    meta = AGENT_META.get(agent_id)
    if not meta:
        return {"error": f"Agent '{agent_id}' not found"}, 404

    # 尝试读取 SOUL.md
    soul_path = Path(__file__).parents[4] / "agents" / agent_id / "SOUL.md"
    soul_content = ""
    if soul_path.exists():
        soul_content = soul_path.read_text(encoding="utf-8")[:2000]

    return {
        "id": agent_id,
        **meta,
        "soul_preview": soul_content,
    }


@router.get("/{agent_id}/config")
async def get_agent_config(agent_id: str):
    """获取 Agent 运行时配置。"""
    config_path = Path(__file__).parents[4] / "data" / "agent_config.json"
    if not config_path.exists():
        return {"agent_id": agent_id, "config": {}}

    try:
        configs = json.loads(config_path.read_text(encoding="utf-8"))
        agent_config = configs.get(agent_id, {})
        return {"agent_id": agent_id, "config": agent_config}
    except (json.JSONDecodeError, IOError):
        return {"agent_id": agent_id, "config": {}}
