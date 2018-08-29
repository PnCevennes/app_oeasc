SELECT * FROM active_locks;

SELECT pg_terminate_backend(pid), * FROM active_locks