# SQLModel Gotchas

- **Session access:** Don't access ORM objects after the session is closed. Capture IDs or convert to Pydantic primitives first before leaving the session context.
