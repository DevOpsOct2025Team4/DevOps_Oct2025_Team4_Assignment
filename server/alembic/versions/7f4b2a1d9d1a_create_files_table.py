"""create-files-table

Revision ID: 7f4b2a1d9d1a
Revises: c51fffa422a9
Create Date: 2026-02-06 20:35:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "7f4b2a1d9d1a"
down_revision = "c51fffa422a9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "files" not in inspector.get_table_names():
        op.create_table(
            "files",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("user_id", sa.String(length=255), nullable=False),
            sa.Column("filename", sa.String(length=255), nullable=False),
            sa.Column("original_filename", sa.String(length=255), nullable=False),
            sa.Column("file_path", sa.String(length=1024), nullable=False),
            sa.Column("file_size", sa.Integer(), server_default="0", nullable=False),
            sa.Column("mime_type", sa.String(length=255), nullable=False),
            sa.Column("bucket", sa.String(length=255), nullable=False),
            sa.Column(
                "uploaded_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_files_user_id"), "files", ["user_id"], unique=False)
    else:
        existing_indexes = {idx["name"] for idx in inspector.get_indexes("files")}
        ix_name = op.f("ix_files_user_id")
        if ix_name not in existing_indexes:
            op.create_index(ix_name, "files", ["user_id"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "files" in inspector.get_table_names():
        existing_indexes = {idx["name"] for idx in inspector.get_indexes("files")}
        ix_name = op.f("ix_files_user_id")
        if ix_name in existing_indexes:
            op.drop_index(ix_name, table_name="files")
        op.drop_table("files")
