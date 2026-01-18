"""add_system_admin_table_and_remove_user_role

Revision ID: 54ffc5a9b833
Revises: 64fab00b9b1e
Create Date: 2026-01-18 15:18:46.178919

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "54ffc5a9b833"
down_revision: Union[str, Sequence[str], None] = "64fab00b9b1e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 创建 system_admins 表
    op.create_table(
        "system_admins",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("granted_by", sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["granted_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_system_admins_id"), "system_admins", ["id"], unique=False)

    # 将 role 为 'admin' 的用户迁移到 system_admins 表
    # 使用原始SQL执行数据迁移
    op.execute(
        """
        INSERT INTO system_admins (id, user_id, created_at, granted_by)
        SELECT
            LOWER(HEX(RANDOMBLOB(4)) || '-' || HEX(RANDOMBLOB(2)) || '-4' ||
                  SUBSTR(HEX(RANDOMBLOB(2)), 2) || '-' ||
                  SUBSTR('89ab', ABS(RANDOM()) % 4 + 1, 1) ||
                  SUBSTR(HEX(RANDOMBLOB(2)), 2) || '-' ||
                  HEX(RANDOMBLOB(6))),
            id,
            CURRENT_TIMESTAMP,
            NULL
        FROM users
        WHERE role = 'admin'
    """
    )

    # 删除 users 表的 role 列
    # SQLite 不支持直接删除列，需要重建表
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("role")


def downgrade() -> None:
    """Downgrade schema."""
    # 重新添加 users 表的 role 列
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("role", sa.String(), nullable=True))

    # 将 system_admins 表中的用户恢复到 users.role
    op.execute(
        """
        UPDATE users
        SET role = 'admin'
        WHERE id IN (SELECT user_id FROM system_admins)
    """
    )

    # 设置其他用户为 'user'
    op.execute(
        """
        UPDATE users
        SET role = 'user'
        WHERE role IS NULL
    """
    )

    # 删除 system_admins 表
    op.drop_index(op.f("ix_system_admins_id"), table_name="system_admins")
    op.drop_table("system_admins")
