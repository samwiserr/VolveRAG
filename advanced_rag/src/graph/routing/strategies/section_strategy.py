"""
Routing strategy for section lookup queries.
"""
from langchain_core.messages import AIMessage
from src.normalize.query_normalizer import extract_well, NormalizedQuery
from src.core.result import Result, AppError, ErrorType
from .base import RoutingStrategy


class SectionRoutingStrategy(RoutingStrategy):
    """
    Routes section lookup queries to section lookup tool.
    
    Priority: 4 (medium - sections are specific document parts)
    """
    
    @property
    def priority(self) -> int:
        return 4
    
    def should_route(
        self,
        question: str,
        normalized_query: NormalizedQuery,
        tool_query: str,
        persist_dir: str,
    ) -> bool:
        """Check if this is a section lookup query."""
        ql = question.lower()
        
        # Check for section keywords
        has_section_keyword = any(k in ql for k in [
            "summary", "introduction", "conclusion",
            "results", "discussion", "abstract"
        ])
        
        # Check for well pattern
        extracted_well = extract_well(question)
        has_well_pattern = (
            ("15" in ql and "9" in ql) or
            extracted_well is not None or
            normalized_query.well is not None
        )
        
        return has_section_keyword and has_well_pattern
    
    def route(
        self,
        question: str,
        normalized_query: NormalizedQuery,
        tool_query: str,
        persist_dir: str,
    ) -> Result[AIMessage, AppError]:
        """Route to section lookup tool."""
        try:
            message = self._create_tool_call_message(
                tool_name="lookup_section",
                query=tool_query,
                call_id="call_lookup_section_1",
            )
            return Result.ok(message)
        except Exception as e:
            return Result.from_exception(
                e,
                ErrorType.ROUTING_ERROR,
                context={"strategy": "section", "question": question[:100]}
            )

