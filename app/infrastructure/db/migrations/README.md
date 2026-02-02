Migrations placeholder.

Alembic is used for schema migrations.

Typical commands (run from repo root):

- Initialize database to latest:
  - `python -m alembic upgrade head`
- Create a new revision (autogenerate):
  - `python -m alembic revision --autogenerate -m "describe change"`

