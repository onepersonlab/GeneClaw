"""Task 模型 — GeneClaw 基因分析多智能体任务核心表。"""
from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Boolean, Column, DateTime, Enum, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from ..db import Base


class TaskState(str, enum.Enum):
    """任务状态枚举 — 映射 GeneClaw 八大智能体流程。"""

    Pending = "Pending"
    Coordinator = "Coordinator"
    Planning = "Planning"
    Reviewing = "Reviewing"
    Approved = "Approved"
    Dispatching = "Dispatching"
    Executing = "Executing"
    Aggregating = "Aggregating"
    Done = "Done"
    Blocked = "Blocked"
    Cancelled = "Cancelled"


TERMINAL_STATES = {TaskState.Done, TaskState.Cancelled}

STATE_TRANSITIONS = {
    TaskState.Pending: {TaskState.Coordinator, TaskState.Cancelled},
    TaskState.Coordinator: {TaskState.Planning, TaskState.Cancelled},
    TaskState.Planning: {TaskState.Reviewing, TaskState.Coordinator, TaskState.Cancelled, TaskState.Blocked},
    TaskState.Reviewing: {TaskState.Approved, TaskState.Planning, TaskState.Cancelled},
    TaskState.Approved: {TaskState.Dispatching, TaskState.Cancelled, TaskState.Blocked},
    TaskState.Dispatching: {TaskState.Executing, TaskState.Cancelled, TaskState.Blocked},
    TaskState.Executing: {TaskState.Aggregating, TaskState.Done, TaskState.Blocked, TaskState.Cancelled},
    TaskState.Aggregating: {TaskState.Done, TaskState.Dispatching, TaskState.Executing, TaskState.Cancelled},
    TaskState.Blocked: {
        TaskState.Coordinator,
        TaskState.Planning,
        TaskState.Reviewing,
        TaskState.Dispatching,
        TaskState.Executing,
    },
}

STATE_AGENT_MAP = {
    TaskState.Coordinator: "coordinator",
    TaskState.Planning: "planner",
    TaskState.Reviewing: "reviewer",
    TaskState.Approved: "dispatcher",
    TaskState.Dispatching: "dispatcher",
    TaskState.Executing: "dispatcher",
    TaskState.Aggregating: "dispatcher",
}

ORG_AGENT_MAP = {
    "协调智能体": "coordinator",
    "规划智能体": "planner",
    "审议智能体": "reviewer",
    "派发智能体": "dispatcher",
    "数据工程师": "data_engineer",
    "生信工程师": "bioinfo_engineer",
    "临床智能体": "clinical_expert",
    "报告智能体": "reporter_agent",
}

STATE_ORG_MAP = {
    TaskState.Coordinator: "协调智能体",
    TaskState.Planning: "规划智能体",
    TaskState.Reviewing: "审议智能体",
    TaskState.Approved: "派发智能体",
    TaskState.Dispatching: "派发智能体",
    TaskState.Executing: "执行层",
    TaskState.Aggregating: "派发智能体",
}


class Task(Base):
    """GeneClaw 基因分析多智能体任务表。"""

    __tablename__ = "tasks"

    task_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trace_id = Column(String(64), nullable=False, default=lambda: str(uuid.uuid4()), comment="追踪链路 ID")
    title = Column(String(200), nullable=False, comment="任务标题")
    description = Column(Text, default="", comment="任务描述")
    priority = Column(String(10), default="中", comment="优先级")
    state = Column(
        Enum(TaskState, name="task_state", native_enum=False, validate_strings=True),
        nullable=False,
        default=TaskState.Coordinator,
        comment="任务状态",
    )
    assignee_org = Column(String(50), nullable=True, comment="目标执行智能体")
    creator = Column(String(50), default="user", comment="创建者")
    tags = Column(JSONB, default=list, comment="标签")
    meta = Column(JSONB, default=dict, comment="扩展元数据")

    # 兼容旧看板字段
    org = Column(String(32), nullable=False, default="协调智能体", comment="当前执行智能体")
    official = Column(String(32), default="", comment="责任智能体")
    now = Column(Text, default="", comment="当前进展描述")
    eta = Column(String(64), default="-", comment="预计完成时间")
    block = Column(Text, default="无", comment="阻塞原因")
    output = Column(Text, default="", comment="最终产出")
    archived = Column(Boolean, default=False, comment="是否归档")

    flow_log = Column(JSONB, default=list, comment="流转日志 [{at, from, to, remark}]")
    progress_log = Column(JSONB, default=list, comment="进展日志 [{at, agent, text, todos}]")
    todos = Column(JSONB, default=list, comment="子任务 [{id, title, status, detail}]")
    scheduler = Column(JSONB, default=dict, comment="调度器元数据")
    template_id = Column(String(64), default="", comment="模板ID")
    template_params = Column(JSONB, default=dict, comment="模板参数")
    ac = Column(Text, default="", comment="验收标准")
    target_dept = Column(String(64), default="", comment="目标智能体")

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        Index("ix_tasks_trace_id", "trace_id"),
        Index("ix_tasks_assignee_org", "assignee_org"),
        Index("ix_tasks_created_at", "created_at"),
        Index("ix_tasks_state", "state"),
        Index("ix_tasks_state_archived", "state", "archived"),
        Index("ix_tasks_updated_at", "updated_at"),
    )

    @staticmethod
    def org_for_state(state: TaskState, assignee_org: str | None = None) -> str:
        if state in {TaskState.Executing}:
            return assignee_org or "执行层"
        return STATE_ORG_MAP.get(state, assignee_org or "协调智能体")

    def to_dict(self) -> dict[str, Any]:
        """序列化为 API 响应格式，并兼容旧 live_status 字段。"""

        state_value = self.state.value if isinstance(self.state, TaskState) else str(self.state or "")
        meta = self.meta or {}
        scheduler = self.scheduler or {}
        task_id = str(self.task_id) if self.task_id else ""
        updated_at = self.updated_at.isoformat() if self.updated_at else ""
        legacy_output = self.output or meta.get("output") or meta.get("legacy_output", "")

        return {
            "task_id": task_id,
            "trace_id": self.trace_id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "state": state_value,
            "assignee_org": self.assignee_org,
            "creator": self.creator,
            "tags": self.tags or [],
            "meta": meta,
            "flow_log": self.flow_log or [],
            "progress_log": self.progress_log or [],
            "todos": self.todos or [],
            "scheduler": scheduler,
            "created_at": self.created_at.isoformat() if self.created_at else "",
            "updated_at": updated_at,
            # 旧前端兼容字段
            "id": task_id,
            "org": self.org or self.org_for_state(self.state, self.assignee_org),
            "official": self.official or self.creator,
            "now": self.now or self.description,
            "eta": self.eta if self.eta != "-" else updated_at,
            "block": self.block,
            "output": legacy_output,
            "archived": self.archived,
            "templateId": self.template_id,
            "templateParams": self.template_params or {},
            "ac": self.ac,
            "targetDept": self.target_dept,
            "_scheduler": scheduler,
            "createdAt": self.created_at.isoformat() if self.created_at else "",
            "updatedAt": updated_at,
        }