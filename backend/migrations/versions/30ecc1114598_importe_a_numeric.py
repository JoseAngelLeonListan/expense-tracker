"""importe a numeric

Revision ID: 30ecc1114598
Revises: f842fdf21446
Create Date: 2026-10-07 10:00:28.737957

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '30ecc1114598'
down_revision: Union[str, Sequence[str], None] = 'f842fdf21446'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Revisada a mano: Alembic generó DOUBLE_PRECISION (solo PostgreSQL) y un ALTER suelto
    # que falla en SQLite. batch_alter_table vale para los dos.
    with op.batch_alter_table("expenses") as batch_op:
        batch_op.alter_column(
            "amount",
            existing_type=sa.Float(),
            type_=sa.Numeric(precision=10, scale=2),
            existing_nullable=False,
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("expenses") as batch_op:
        batch_op.alter_column(
            "amount",
            existing_type=sa.Numeric(precision=10, scale=2),
            type_=sa.Float(),
            existing_nullable=False,
        )
