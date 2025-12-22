"""
Document grader for determining relevance of retrieved documents.
"""
import re
import logging
from typing import Literal
from langgraph.graph import MessagesState
from langchain_core.messages import HumanMessage, ToolMessage
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class GradeDocuments(BaseModel):
    """Grade documents using a binary score for relevance check."""
    binary_score: str = Field(
        description="Relevance score: 'yes' if relevant, or 'no' if not relevant"
    )


GRADE_PROMPT = (
    "You are a grader assessing relevance of retrieved documents to a user question. \n "
    "Here are the retrieved documents: \n\n {context} \n\n"
    "Here is the user question: {question} \n"
    "IMPORTANT: Be VERY lenient. If the documents contain:\n"
    "- The well name mentioned in the question\n"
    "- The word 'model' or 'evaluation' or related terms\n"
    "- Any text that appears to be a continuation or completion of the question\n"
    "- Any information about the well, formation, or evaluation\n"
    "Then mark it as relevant (yes).\n"
    "Only mark as not relevant (no) if the documents are completely unrelated (e.g., about a different well with no connection).\n"
    "Give a binary score 'yes' or 'no'."
)


def grade_documents(state: MessagesState) -> Literal["generate_answer", "rewrite_question"]:
    """
    Determine whether the retrieved documents are relevant to the question.
    
    Args:
        state: MessagesState containing messages
        
    Returns:
        Next node to route to: "generate_answer" or "rewrite_question"
    """
    # Import helper function from nodes.py inside function to avoid circular imports
    from ..nodes import _get_grader_model
    
    messages = state["messages"]
    question = messages[0].content
    
    # Extract context from tool messages (retrieved documents)
    context_parts = []
    rewrite_count = 0
    
    for msg in messages:
        # Count rewrite attempts
        if isinstance(msg, HumanMessage) and msg != messages[0]:
            rewrite_count += 1
        
        # Extract tool message content
        if isinstance(msg, ToolMessage):
            tool_name = getattr(msg, 'name', 'unknown')
            logger.info(f"[GRADE] Found ToolMessage from tool '{tool_name}', content length: {len(msg.content) if isinstance(msg.content, str) else 'non-string'}")
            context_parts.append(msg.content)
        elif hasattr(msg, 'content') and msg.content:
            # Check if it's a tool message by content length and structure
            if isinstance(msg.content, str) and len(msg.content) > 100:
                # Could be tool message content
                logger.debug(f"[GRADE] Found potential tool message content (length: {len(msg.content)})")
                context_parts.append(msg.content)
    
    # Prevent infinite rewrite loops
    if rewrite_count >= 2:
        logger.warning(f"[GRADE] Too many rewrite attempts ({rewrite_count}) - proceeding to generate answer anyway")
        return "generate_answer"
    
    if not context_parts:
        # Fallback: get last message content
        context = messages[-1].content if messages else ""
    else:
        context = "\n\n".join(context_parts)
    
    logger.info(f"[GRADE] Question: {question[:100]}...")
    logger.info(f"[GRADE] Context length: {len(context)} chars, Rewrite count: {rewrite_count}")
    
    # If context is very short or empty, it's probably not relevant
    if len(context) < 50:
        logger.info("[GRADE] Context too short - rewriting question")
        return "rewrite_question"
    
    # Quick heuristic check: if context contains well name and "model" or "evaluation", likely relevant
    question_lower = question.lower()
    context_lower = context.lower()
    
    # Extract well name pattern (e.g., "15/9-F-4", "15_9-F-4", "15-9-F-4")
    well_patterns = re.findall(r'15[_\s/-]?9[_\s/-]?F[_\s/-]?[0-9A-Z]+', question_lower)
    
    # Check if question appears to be a partial sentence (doesn't end with punctuation and has "is" or similar)
    is_partial_sentence = (
        not question.strip().endswith(('.', '!', '?', ':')) and 
        ('is' in question_lower or 'accordingly' in question_lower or 'reported' in question_lower)
    )
    
    # If it's a partial sentence and context is substantial, likely relevant
    if is_partial_sentence and len(context) > 500:
        logger.info("[GRADE] Quick check: Partial sentence query with substantial context - marking as relevant")
        return "generate_answer"
    
    # Check for well name and related terms
    if well_patterns:
        well_found = any(well in context_lower for well in well_patterns)
        model_terms = ["model", "evaluation", "sleipner", "volve", "hugin", "skagerak", "formation"]
        has_model_term = any(term in context_lower for term in model_terms)
        
        if well_found and (has_model_term or "accordingly" in context_lower or "reported" in context_lower):
            logger.info("[GRADE] Quick check: Well name and model/evaluation found in context - marking as relevant")
            return "generate_answer"
    
    prompt = GRADE_PROMPT.format(question=question, context=context[:3000])  # Limit context length
    response = _get_grader_model().with_structured_output(GradeDocuments).invoke(
        [{"role": "user", "content": prompt}]
    )
    score = response.binary_score
    
    if score == "yes":
        logger.info("[GRADE] Documents are relevant - proceeding to generate answer")
        return "generate_answer"
    else:
        logger.info("[GRADE] Documents are not relevant - rewriting question")
        return "rewrite_question"

