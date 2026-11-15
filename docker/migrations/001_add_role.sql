-- Migracion 001: rol de usuario.
-- Necesaria solo en bases creadas antes de existir el control de acceso:
-- las instalaciones nuevas ya reciben la columna desde create_all.
--
-- Uso en Docker Compose:
--   docker compose exec -T postgres psql -U fittrack -d fittrack_users < docker/migrations/001_add_role.sql
--
-- Uso en Swarm:
--   docker exec -i $(docker ps -qf name=fittrack_postgres) \
--     psql -U fittrack -d fittrack_users < docker/migrations/001_add_role.sql

ALTER TABLE users
    ADD COLUMN IF NOT EXISTS role VARCHAR(20) NOT NULL DEFAULT 'user';
