"""
Message handling utilities for graph nodes.
"""
from typing import Optional, Iterator, Tuple
from langchain_core.messages import HumanMessage


def _latest_user_question(messages) -> str:
    """
    Multi-turn support: use the most recent HumanMessage as the "current question".
    
    Args:
        messages: List of messages (dict-style or LangChain message objects)
        
    Returns:
        Most recent user question, or empty string if not found
    """
    try:
        for m in reversed(messages or []):
            if isinstance(m, HumanMessage) and isinstance(getattr(m, "content", None), str):
                return m.content
    except Exception:
        pass
    # Fallback (single-turn behavior)
    try:
        if messages and isinstance(messages[-1].get("content"), str):
            return messages[-1]["content"]
    except Exception:
        pass
    try:
        return messages[0].content if messages else ""
    except Exception:
        return ""


def _iter_message_texts(messages) -> Iterator[Tuple[str, str]]:
    """
    Yield (role, content) for both dict-style and LangChain message objects.
    
    Args:
        messages: List of messages
        
    Yields:
        Tuple of (role, content)
    """
    for m in messages or []:
        # dict-style
        if isinstance(m, dict):
            role = m.get("role")
            content = m.get("content")
            if isinstance(content, str):
                yield role, content
            continue
        # LangChain message objects
        role = getattr(m, "type", None) or getattr(m, "__class__", type("x", (), {})).__name__
        content = getattr(m, "content", None)
        if isinstance(content, str):
            yield str(role), content


def _infer_recent_context(messages) -> Tuple[Optional[str], Optional[str]]:
    """
    Infer (well, formation) from recent conversation history.
    
    Args:
        messages: List of messages
        
    Returns:
        Tuple of (well, formation) or (None, None) if not found
    """
    from src.normalize.query_normalizer import extract_well, normalize_formation
    
    well = None
    formation = None
    
    # Look through recent messages for well/formation mentions
    for role, content in _iter_message_texts(messages):
        if not content:
            continue
        
        # Extract well
        if not well:
            well = extract_well(content)
        
        # Try to extract formation (simplified - just look for common formation names)
        if not formation:
            content_lower = content.lower()
            common_formations = ["hugin", "sleipner", "skagerak", "volve"]
            for f in common_formations:
                if f in content_lower:
                    formation = normalize_formation(f, persist_dir="./data/vectorstore")
                    break
    
    return well, formation

