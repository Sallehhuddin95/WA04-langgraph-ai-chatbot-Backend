"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

revision: str = ${up_revision!r}
down_revision: Union[str, None] = ${down_revision!r}
branch_labels: Union[str, Sequence[str], None] = ${branch_labels!r}
depends_on: Union[str, Sequence[str], None] = ${depends_on!r}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
