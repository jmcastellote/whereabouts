"""Add column - app_config

Revision ID: 6439e23d8a79
Revises: 9d02f2cdd82f
Create Date: 2023-01-15 11:08:25.035404

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6439e23d8a79'
down_revision = '9d02f2cdd82f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('gps_tracker', sa.Column('app_config', sa.JSON(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('gps_tracker', 'app_config')
    # ### end Alembic commands ###
