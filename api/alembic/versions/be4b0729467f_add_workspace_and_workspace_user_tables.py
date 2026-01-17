"""add_workspace_and_workspace_user_tables

Revision ID: be4b0729467f
Revises: 58d5027c1abd
Create Date: 2026-01-17 23:14:56.051095

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "be4b0729467f"
down_revision: Union[str, Sequence[str], None] = "58d5027c1abd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 创建 workspaces 表
    op.create_table(
        "workspaces",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("created_by", sa.String(36), nullable=True),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_workspaces_id", "workspaces", ["id"])
    op.create_index("ix_workspaces_name", "workspaces", ["name"])

    # 创建 workspace_user_association 表
    op.create_table(
        "workspace_user_association",
        sa.Column("workspace_id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), primary_key=True),
        sa.Column("role", sa.String(), nullable=False, server_default="member"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["workspace_id"], ["workspaces.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )

    # 使用 batch mode 为 files 表添加 workspace_id 列
    with op.batch_alter_table("files") as batch_op:
        batch_op.add_column(sa.Column("workspace_id", sa.String(36), nullable=True))
        batch_op.create_foreign_key(
            "fk_files_workspace_id", "workspaces", ["workspace_id"], ["id"]
        )

    # 使用 batch mode 为 storage_backends 表添加 workspace_id 列
    with op.batch_alter_table("storage_backends") as batch_op:
        batch_op.add_column(sa.Column("workspace_id", sa.String(36), nullable=True))
        batch_op.create_foreign_key(
            "fk_storage_backends_workspace_id", "workspaces", ["workspace_id"], ["id"]
        )


def downgrade() -> None:
    """Downgrade schema."""
    # 使用 batch mode 删除 storage_backends 外键和列
    with op.batch_alter_table("storage_backends") as batch_op:
        batch_op.drop_constraint("fk_storage_backends_workspace_id", type_="foreignkey")
        batch_op.drop_column("workspace_id")

    # 使用 batch mode 删除 files 外键和列
    with op.batch_alter_table("files") as batch_op:
        batch_op.drop_constraint("fk_files_workspace_id", type_="foreignkey")
        batch_op.drop_column("workspace_id")

    # 删除 workspace_user_association 表
    op.drop_table("workspace_user_association")

    # 删除 workspaces 表
    op.drop_index("ix_workspaces_name", "workspaces")
    op.drop_index("ix_workspaces_id", "workspaces")
    op.drop_table("workspaces")
