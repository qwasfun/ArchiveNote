"""Update notes column nullability

Revision ID: db38fc2274be
Revises: 3cc16d4f8bbb
Create Date: 2026-02-01 13:46:10.705890

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "db38fc2274be"
down_revision: Union[str, Sequence[str], None] = "3cc16d4f8bbb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 将 notes 表的 title 字段设置为必填（NOT NULL）
    op.alter_column("notes", "title", existing_type=sa.VARCHAR(), nullable=False)
    # 将 notes 表的 content 字段设置为可空（允许为空）
    op.alter_column("notes", "content", existing_type=sa.TEXT(), nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    # 回滚：将 content 字段改回必填
    op.alter_column("notes", "content", existing_type=sa.TEXT(), nullable=False)
    # 回滚：将 title 字段改回可空
    op.alter_column("notes", "title", existing_type=sa.VARCHAR(), nullable=True)
