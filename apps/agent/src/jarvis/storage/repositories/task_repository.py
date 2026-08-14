"""
SQLite Task Repository for task state persistence.
"""

import json
import time

from jarvis.core.contracts import RiskLevel, TaskPlan, TaskStep
from jarvis.storage.sqlite import SQLiteManager


class SQLiteTaskRepository:
    """Repository handling CRUD operations for TaskPlan and TaskStep entities."""

    def __init__(self, manager: SQLiteManager):
        self.manager = manager

    def save_task_plan(self, plan: TaskPlan) -> None:
        """Save or update TaskPlan and its steps in SQLite."""
        now = time.time()
        with self.manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO tasks (task_id, command_id, goal_summary, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(task_id) DO UPDATE SET
                    status=excluded.status,
                    updated_at=excluded.updated_at
                """,
                (plan.task_id, plan.command_id, plan.goal_summary, plan.status, now, now),
            )

            for step in plan.steps:
                cursor.execute(
                    """
                    INSERT INTO task_steps (
                        step_id, task_id, step_number, tool_id, tool_input, risk_level,
                        status, requires_approval, description, output_summary, error_message
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(step_id) DO UPDATE SET
                        status=excluded.status,
                        output_summary=excluded.output_summary,
                        error_message=excluded.error_message
                    """,
                    (
                        step.step_id,
                        plan.task_id,
                        step.step_number,
                        step.tool_id,
                        json.dumps(step.tool_input),
                        step.risk_level.value,
                        step.status,
                        1 if step.requires_approval else 0,
                        step.description,
                        None,
                        None,
                    ),
                )
            conn.commit()

    def get_task_plan(self, task_id: str) -> TaskPlan | None:
        """Retrieve TaskPlan by task_id."""
        with self.manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,))
            row = cursor.fetchone()
            if not row:
                return None

            cursor.execute("SELECT * FROM task_steps WHERE task_id = ? ORDER BY step_number ASC", (task_id,))
            step_rows = cursor.fetchall()

            steps: list[TaskStep] = []
            for sr in step_rows:
                steps.append(
                    TaskStep(
                        step_id=sr["step_id"],
                        step_number=sr["step_number"],
                        tool_id=sr["tool_id"],
                        tool_input=json.loads(sr["tool_input"]),
                        risk_level=RiskLevel(sr["risk_level"]),
                        status=sr["status"],
                        requires_approval=bool(sr["requires_approval"]),
                        description=sr["description"] or "",
                    )
                )

            return TaskPlan(
                task_id=row["task_id"],
                command_id=row["command_id"],
                goal_summary=row["goal_summary"],
                steps=steps,
                status=row["status"],
            )

    def update_task_status(self, task_id: str, status: str) -> None:
        """Update overall task status."""
        now = time.time()
        with self.manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE tasks SET status = ?, updated_at = ? WHERE task_id = ?", (status, now, task_id))
            conn.commit()

    def update_step_result(self, step_id: str, status: str, output_summary: str = "", error_message: str = "") -> None:
        """Update execution outcome for a specific step."""
        with self.manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE task_steps
                SET status = ?, output_summary = ?, error_message = ?
                WHERE step_id = ?
                """,
                (status, output_summary, error_message, step_id),
            )
            conn.commit()
