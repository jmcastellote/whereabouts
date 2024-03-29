"""Initial Revision

Revision ID: 7bb1b21c40e7
Revises: 
Create Date: 2022-11-19 20:06:24.374591

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7bb1b21c40e7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('gps_record',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('datetime', sa.DateTime(timezone=True), nullable=True),
    sa.Column('latitude', sa.Float(), nullable=True),
    sa.Column('longitude', sa.Float(), nullable=True),
    sa.Column('altitude', sa.Float(), nullable=True),
    sa.Column('accuracy', sa.Float(), nullable=True),
    sa.Column('vertical_accuracy', sa.Float(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('device', sa.String(length=128), nullable=True),
    sa.Column('app', sa.String(length=128), nullable=True),
    sa.Column('user', sa.String(length=32), nullable=True),
    sa.Column('distance', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('desc_date', 'gps_record', [sa.text('datetime DESC')], unique=False)
    op.create_index('desc_date_per_app', 'gps_record', [sa.text('datetime DESC'), 'device', 'app'], unique=False)
    op.create_index('desc_date_per_device', 'gps_record', [sa.text('datetime DESC'), 'device'], unique=False)
    op.create_index('device_records', 'gps_record', ['datetime', 'device', 'app', 'user'], unique=True)
    op.create_index(op.f('ix_gps_record_id'), 'gps_record', ['id'], unique=False)
    op.create_table('gps_tracker',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.Column('device', sa.String(length=128), nullable=True),
    sa.Column('app', sa.String(length=128), nullable=True),
    sa.Column('last_seen', sa.DateTime(timezone=True), nullable=True),
    sa.Column('icon', sa.String(length=512), nullable=True),
    sa.Column('icon_config', sa.JSON(), nullable=True),
    sa.Column('display_path', sa.Boolean(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('tracker_bearer', sa.String(length=128), nullable=True),
    sa.Column('distance_tracked', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_gps_tracker_id'), 'gps_tracker', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_gps_tracker_id'), table_name='gps_tracker')
    op.drop_table('gps_tracker')
    op.drop_index(op.f('ix_gps_record_id'), table_name='gps_record')
    op.drop_index('device_records', table_name='gps_record')
    op.drop_index('desc_date_per_device', table_name='gps_record')
    op.drop_index('desc_date_per_app', table_name='gps_record')
    op.drop_index('desc_date', table_name='gps_record')
    op.drop_table('gps_record')
    # ### end Alembic commands ###
