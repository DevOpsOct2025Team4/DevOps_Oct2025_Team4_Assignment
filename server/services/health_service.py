import psycopg2


def check_database(db_url: str, logger) -> bool:
    if not db_url:
        return False

    try:
        with psycopg2.connect(db_url) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                cur.fetchone()
        return True
    except Exception as exc:  # pragma: no cover - best-effort health check
        logger.warning("DB healthcheck failed: %s", exc)
        return False
