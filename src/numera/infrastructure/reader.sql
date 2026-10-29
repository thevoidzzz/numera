DO $$
BEGIN
    CREATE ROLE numera_reader LOGIN;
EXCEPTION
    WHEN duplicate_object THEN
        NULL;
END
$$;

GRANT USAGE ON SCHEMA warehouse TO numera_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA warehouse TO numera_reader;
ALTER ROLE numera_reader SET statement_timeout = '2s';
