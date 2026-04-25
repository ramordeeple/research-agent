import logging
from functools import cache

from src.core.constants import MAX_HISTORY_MESSAGES
from src.llm.schemas import Message
from src.memory.schemas import Session

logger = logging.getLogger(__name__)


class MemoryStore:
    """In-memory storage of dialogue history.

Not persistent - when the server is restarted, everything is lost.
Not suitable for multi-replica deployment.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}

    def get_messages(self, session_id: str) -> list[Message]:
        session = self._sessions.get(session_id)
        if session is None:
            return []
        return list(session.messages[-MAX_HISTORY_MESSAGES:])

    def append(self, session_id: str, messages: list[Message]) -> None:
        session = self._sessions.get(session_id)
        if session is None:
            session = Session(session_id=session_id)
            self._sessions[session_id] = session
            logger.info("Created new session: %s", session_id)

        session.messages.extend(messages)
        logger.debug(
            "Session %s now has %d messages",
            session_id,
            len(session.messages),
        )

    def clear(self, session_id: str) -> bool:
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info("Cleared session: %s", session_id)
            return True
        return False


@cache
def get_memory_store() -> MemoryStore:
    return MemoryStore()
