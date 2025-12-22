"""
Query rewriter for improving retrieval.
"""
import logging
from langgraph.graph import MessagesState
from langchain_core.messages import HumanMessage
from ..utils.message_utils import _latest_user_question

logger = logging.getLogger(__name__)


REWRITE_PROMPT = (
    "You are a question rewriter. Given the following question and context, "
    "rewrite the question to be more specific and retrieval-friendly. "
    "If the context is not relevant, ask a better question based on the original question.\n\n"
    "CRITICAL RULES:\n"
    "- DO NOT add well names, formation names, or other entities that were NOT in the original question.\n"
    "- If the original question asks about well 15/9-F-4, the rewritten question must ONLY mention 15/9-F-4, not other wells.\n"
    "- DO NOT add comparison questions (e.g., 'compare to well X') unless the original question explicitly asks for comparison.\n"
    "- Focus on making the question more specific for retrieval, but keep the same entities (wells, formations, parameters).\n\n"
    "Original question: {question} \n"
    "Context: {context} \n"
    "Rewritten question:"
)


def rewrite_question(state: MessagesState):
    """
    Rewrite the original user question to improve retrieval.
    
    Args:
        state: MessagesState containing messages
        
    Returns:
        Dictionary with 'messages' key containing rewritten question
    """
    # Import helper function from nodes.py inside function to avoid circular imports
    from ..nodes import _get_response_model
    
    messages = state["messages"]
    question = _latest_user_question(messages)
    question = _latest_user_question(messages)
    context = messages[-1].content
    
    prompt = REWRITE_PROMPT.format(question=question, context=context)
    response = _get_response_model().invoke([{"role": "user", "content": prompt}])
    
    logger.info(f"[REWRITE] Original: {question}")
    logger.info(f"[REWRITE] Rewritten: {response.content}")
    
    return {"messages": [HumanMessage(content=response.content)]}

