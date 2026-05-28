from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import (
    DeclarativeBase,
    ORMExecuteState,
    Session,
    sessionmaker,
    with_loader_criteria,
)

from app.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Tenant auto-filter ------------------------------------------------------
# When an authenticated request binds an org to its DB session (via
# `bind_tenant`), every SELECT touching the Case entity is restricted to that
# org. This is defence-in-depth behind explicit org_id filters in routers —
# even if a router forgets to filter, the ORM cannot return another tenant's
# row.
#
# We key off `session.info` rather than a contextvar because FastAPI runs sync
# dependencies and endpoints in separate threadpool executions, each receiving
# its own *copy* of the context — a contextvar set inside the auth dependency
# would not be visible to the endpoint's query. The Session object, by
# contrast, is the same instance shared across the whole request.
#
# Background tasks, tests calling services directly, and admin tooling never
# call bind_tenant — they see everything (orchestrator + analytics pass org_id
# explicitly where it matters).
# ----------------------------------------------------------------------------

TENANT_KEY = "tenant_org_id"


def bind_tenant(db: Session, org_id) -> None:
    db.info[TENANT_KEY] = org_id


@event.listens_for(Session, "do_orm_execute")
def _scope_to_tenant(execute_state: ORMExecuteState) -> None:
    if not execute_state.is_select:
        return
    if execute_state.execution_options.get("skip_tenant_filter"):
        return
    org_id = execute_state.session.info.get(TENANT_KEY)
    if org_id is None:
        return
    from app.models import Case

    execute_state.statement = execute_state.statement.options(
        with_loader_criteria(Case, Case.org_id == org_id, include_aliases=True)
    )
