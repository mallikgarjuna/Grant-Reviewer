"""Ensure an active PromptTemplate exists for review execution."""

import sys
from pathlib import Path
from uuid import UUID

from sqlmodel import Session, select

# Add backend root for app imports (tasks/lessons.md: L1).
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db import create_db_and_tables, get_session
from app.models.domain import PromptTemplate

DEFAULT_TEMPLATE_NAME = "Grant Reviewer Default Template"
DEFAULT_TEMPLATE_TEXT = "Review snippet: {snippet}"


def ensure_active_prompt_template(session: Session) -> tuple[UUID, bool]:
    """Return active template id, creating one when absent."""
    active_template = session.exec(
        select(PromptTemplate).where(PromptTemplate.is_active)
    ).first()
    if active_template is not None:
        return active_template.id, False

    template = PromptTemplate(
        name=DEFAULT_TEMPLATE_NAME,
        template_text=DEFAULT_TEMPLATE_TEXT,
        is_active=True,
    )
    session.add(template)
    session.commit()
    session.refresh(template)
    return template.id, True


def main() -> None:
    """Ensure PromptTemplate precondition for `POST /reviews`."""
    create_db_and_tables()
    session = get_session()
    try:
        template_id, created = ensure_active_prompt_template(session)
    finally:
        session.close()

    if created:
        print(f"Created active prompt template: {template_id}")
        return
    print(f"Active prompt template already exists: {template_id}")


if __name__ == "__main__":
    main()
