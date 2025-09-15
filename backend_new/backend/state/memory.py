# backend/state/memory.py
from __future__ import annotations
from typing import Dict, List, Any
from threading import RLock

class LatestListStore:
    def __init__(self):
        self._data: Dict[str, List[Dict[str, Any]]] = {}
        self._lock = RLock()

    def get(self, session_id: str) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._data.get(session_id, []))

    def set(self, session_id: str, items: List[Dict[str, Any]]) -> None:
        with self._lock:
            self._data[session_id] = list(items)

    def is_empty(self, session_id: str) -> bool:
        with self._lock:
            return not bool(self._data.get(session_id))

    def clear(self, session_id: str) -> None:
        with self._lock:
            self._data.pop(session_id, None)
