"""
Base node implementations that maintain backward compatibility with LangGraph.

These are thin wrappers around the refactored classes that maintain
the original function signatures for LangGraph compatibility.
"""
from typing import List
from langgraph.graph import MessagesState
from langchain_core.messages import AIMessage
from src.graph.routing.router import QueryRouter
from src.graph.retrieval.document_grader import DocumentGrader
from src.graph.generation.query_rewriter import QueryRewriter
from src.core.logging import get_logger

logger = get_logger(__name__)

# Global instances (will be initialized on first use)
_router: QueryRouter | None = None
_grader: DocumentGrader | None = None
# _generator: AnswerGenerator | None = None  # Will be added when AnswerGenerator is implemented
_rewriter: QueryRewriter | None = None


def _get_router(tools: List) -> QueryRouter:
    """Get or create router instance."""
    global _router
    if _router is None:
        _router = QueryRouter(tools)
    return _router


def _get_grader() -> DocumentGrader:
    """Get or create grader instance."""
    global _grader
    if _grader is None:
        _grader = DocumentGrader()
    return _grader


# AnswerGenerator will be implemented later - for now use old implementation
# def _get_generator() -> AnswerGenerator:
#     """Get or create generator instance."""
#     global _generator
#     if _generator is None:
#         _generator = AnswerGenerator()
#     return _generator


def _get_rewriter() -> QueryRewriter:
    """Get or create rewriter instance."""
    global _rewriter
    if _rewriter is None:
        _rewriter = QueryRewriter()
    return _rewriter


def generate_query_or_respond(state: MessagesState, tools: List):
    """
    Call the model to generate a response based on the current state.
    
    This is a backward-compatible wrapper around QueryRouter.
    
    Args:
        state: MessagesState containing messages
        tools: Tools to bind to the model
        
    Returns:
        Dictionary with 'messages' key containing the model response
    """
    router = _get_router(tools)
    result = router.route(state)
    
    # Convert Result to dict format expected by LangGraph
    if result.is_ok():
        return result.unwrap()
    else:
        # On error, return a helpful error message
        error = result.error()
        logger.error(f"Routing error: {error}")
        return {
            "messages": [
                AIMessage(content=f"I encountered an error processing your query: {error.message}")
            ]
        }


def grade_documents(state: MessagesState) -> str:
    """
    Determine whether the retrieved documents are relevant to the question.
    
    This is a backward-compatible wrapper around DocumentGrader.
    
    Args:
        state: MessagesState containing messages
        
    Returns:
        Next node to route to: "generate_answer" or "rewrite_question"
    """
    grader = _get_grader()
    result = grader.grade(state)
    
    if result.is_ok():
        return result.unwrap()
    else:
        # On error, default to generating answer
        error = result.error()
        logger.error(f"Grading error: {error}")
        return "generate_answer"


def rewrite_question(state: MessagesState):
    """
    Rewrite the original user question to improve retrieval.
    
    This is a backward-compatible wrapper around QueryRewriter.
    
    Args:
        state: MessagesState containing messages
        
    Returns:
        Dictionary with 'messages' key containing rewritten question
    """
    rewriter = _get_rewriter()
    result = rewriter.rewrite(state)
    
    if result.is_ok():
        return result.unwrap()
    else:
        # On error, return original question
        error = result.error()
        logger.error(f"Rewrite error: {error}")
        from ..utils.message_utils import _latest_user_question
        from langchain_core.messages import HumanMessage
        question = _latest_user_question(state.get("messages", []))
        return {"messages": [HumanMessage(content=question)]}


def generate_answer(state: MessagesState):
    """
    Generate final answer from relevant documents.
    
    For now, this delegates to the old implementation in nodes.py.
    TODO: Extract to AnswerGenerator class once implementation is complete.
    
    Args:
        state: MessagesState containing messages
        
    Returns:
        Dictionary with 'messages' key containing final answer
    """
    # Import old implementation for backward compatibility
    # We need to import from the parent graph module's nodes.py
    import importlib.util
    import sys
    from pathlib import Path
    
    # Get the old nodes.py file path
    old_nodes_path = Path(__file__).parent.parent / "nodes.py"
    if old_nodes_path.exists():
        spec = importlib.util.spec_from_file_location("old_nodes", old_nodes_path)
        old_nodes = importlib.util.module_from_spec(spec)
        sys.modules["old_nodes"] = old_nodes
        spec.loader.exec_module(old_nodes)
        return old_nodes.generate_answer(state)
    else:
        # Fallback: return error message
        from langchain_core.messages import AIMessage
        return {
            "messages": [
                AIMessage(content="Error: Could not find answer generator implementation.")
            ]
        }

