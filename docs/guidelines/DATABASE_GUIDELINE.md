## 1. Project foundations

1. Choose a cloud PostgreSQL provider.
2. Create an empty PostgreSQL database instance.
3. Store the connection string in environment variables.
4. Add a `.env` file and load it in the backend.
5. Never hardcode credentials in the codebase.

---

## 2. Dependency setup (If not yet installed)

6. Check and install (if necessary) SQLAlchemy (2.x).
7. Check and install (if necessary) a PostgreSQL driver (`psycopg`).
8. Check and install (if necessary) Alembic for migrations.
9. Check and install (if necessary) dotenv or equivalent for configuration.
10. Lock dependencies in your project manager.

---

## 3. Database layer architecture

11. Create a dedicated `db` module.
12. Define a single declarative base.
13. Create one model file per table.
14. Centralize engine and session creation.
15. Ensure all models are imported on startup.

---

## 4. Schema modeling

16. Translate each table into a SQLAlchemy model.
17. Use UUID as primary keys.
18. Use timezone-aware timestamps.
19. Define all foreign keys explicitly.
20. Add all constraints (checks, uniques).
21. Add all indexes.
22. Use soft deletes where required.
23. Do not store derived fields in base tables.
24. Keep models in 3NF.

---

## 5. Migration system

25. Initialize Alembic.
26. Link Alembic to SQLAlchemy metadata.
27. Generate the initial migration.
28. Review generated SQL.
29. Apply migrations to the database.
30. Commit migration files to git.

---

## 6. Reset & automation

31. Create a CLI script to drop the database.
32. Recreate the database.
33. Run all migrations.
34. Seed minimal data.
35. Make the script executable.
36. Ensure the script is idempotent.

---

## 7. Seeding & fixtures

37. Create a seeding layer.
38. Insert core reference data.
39. Keep seeds deterministic.
40. Never seed production automatically.

---

## 8. Views & performance

41. Implement database views or materialized views.
42. Index time-series tables aggressively.
43. Validate query plans for dashboards.
44. Cache heavy aggregates.

---

## 9. Environment separation

45. Use different databases for dev, test, prod.
46. Never share prod credentials.
47. Run migrations per environment.
48. Keep prod data immutable from dev tools.

---

## 10. CI / team workflow

49. Run migrations in CI.
50. Fail build if migration is missing.
51. Enforce migration review in PRs.
52. Never allow manual schema edits.

---

## 11. Backup & recovery

53. Schedule automatic backups.
54. Test restore procedures.
55. Keep local backup scripts.
56. Version backup policies.

---

## 12. Operational rules

57. All schema changes go through migrations.
58. No hotfixes in the database.
59. No raw SQL in business logic.
60. No production reset scripts.
61. All destructive scripts restricted.
62. All schema is reproducible from git.

---

## 13. Long-term hygiene

63. Periodically squash migrations.
64. Archive old data.
65. Monitor table growth.
66. Reindex when needed.
67. Document schema changes.

---

## 14. Security & safety

68. Least-privilege DB users.
69. Separate read/write roles.
70. Enforce SSL connections.
71. Log all migrations.
72. Protect migration commands.

---

## 15. Mental model (the rule)

73. The database is **not infrastructure**.
74. The database is **source code**.
75. Git is the single source of truth.
76. PostgreSQL is a compiled artifact.
