"""empty message

Revision ID: 1d36e5ec34c6
Revises: 538ea31d3311
Create Date: 2022-02-08 15:28:55.456596

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1d36e5ec34c6'
down_revision = '538ea31d3311'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('diploma_themes', sa.Column('requirements', sa.String(length=2048), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('summer_school', 'requirements',
               existing_type=sa.VARCHAR(length=1024),
               nullable=True)
    op.alter_column('summer_school', 'advisors',
               existing_type=sa.VARCHAR(length=1024),
               nullable=True)
    op.alter_column('summer_school', 'tech',
               existing_type=sa.VARCHAR(length=1024),
               nullable=True)
    op.alter_column('summer_school', 'description',
               existing_type=sa.VARCHAR(length=2048),
               nullable=True)
    op.alter_column('summer_school', 'project_name',
               existing_type=sa.VARCHAR(length=1024),
               nullable=True)
    op.alter_column('post_vote', 'post_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_column('diploma_themes', 'requirements')
    # ### end Alembic commands ###
