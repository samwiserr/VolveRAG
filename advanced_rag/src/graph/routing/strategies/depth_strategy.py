"""
Routing strategy for depth queries (MD/TVD/TVDSS).
"""
from typing import Optional
from langchain_core.messages import AIMessage
from src.normalize.query_normalizer import extract_well, NormalizedQuery
from src.core.result import Result, AppError, ErrorType
from .base import RoutingStrategy


class DepthRoutingStrategy(RoutingStrategy):
    """
    Routes depth queries (MD/TVD/TVDSS) to well picks tool.
    
    Priority: 1 (highest - depth queries are very specific)
    """
    
    @property
    def priority(self) -> int:
        return 1
    
    def should_route(
        self,
        question: str,
        normalized_query: NormalizedQuery,
        tool_query: str,
        persist_dir: str,
    ) -> bool:
        """Check if this is a depth query."""
        ql = question.lower()
        
        # Check for depth keywords
        has_depth_keyword = any(k in ql for k in [
            "depth", "md", "tvd", "tvdss", 
            "measured depth", "true vertical depth", "depth of"
        ])
        
        # Must have well and formation context
        has_well = normalized_query.well is not None or extract_well(question) is not None
        has_formation = normalized_query.formation is not None or "formation" in ql
        
        return has_depth_keyword and has_well and has_formation
    
    def route(
        self,
        question: str,
        normalized_query: NormalizedQuery,
        tool_query: str,
        persist_dir: str,
    ) -> Result[AIMessage, AppError]:
        """Route to well picks tool for depth lookup."""
        try:
            message = self._create_tool_call_message(
                tool_name="lookup_well_picks",
                query=tool_query,
                call_id="call_lookup_well_picks_depth_1",
            )
            return Result.ok(message)
        except Exception as e:
            return Result.from_exception(
                e,
                ErrorType.ROUTING_ERROR,
                context={"strategy": "depth", "question": question[:100]}
            )

