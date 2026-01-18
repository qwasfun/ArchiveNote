"""add_workspace_id_to_folders_and_notes

Revision ID: 64fab00b9b1e
Revises: be4b0729467f
Create Date: 2026-01-18 14:04:40.168089

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "64fab00b9b1e"
down_revision: Union[str, Sequence[str], None] = "be4b0729467f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 使用 batch mode 为 folders 表添加 workspace_id 列
    with op.batch_alter_table("folders") as batch_op:
        batch_op.add_column(sa.Column("workspace_id", sa.String(36), nullable=True))
        batch_op.create_foreign_key(
            "fk_folders_workspace_id", "workspaces", ["workspace_id"], ["id"]
        )

    # 使用 batch mode 为 notes 表添加 workspace_id 列
    with op.batch_alter_table("notes") as batch_op:
        batch_op.add_column(sa.Column("workspace_id", sa.String(36), nullable=True))
        batch_op.create_foreign_key(
            "fk_notes_workspace_id", "workspaces", ["workspace_id"], ["id"]
        )


def downgrade() -> None:
    """Downgrade schema."""
    # 使用 batch mode 删除 notes 外键和列
    with op.batch_alter_table("notes") as batch_op:
        batch_op.drop_constraint("fk_notes_workspace_id", type_="foreignkey")
        batch_op.drop_column("workspace_id")

    # 使用 batch mode 删除 folders 外键和列
    with op.batch_alter_table("folders") as batch_op:
        batch_op.drop_constraint("fk_folders_workspace_id", type_="foreignkey")
        batch_op.drop_column("workspace_id")
