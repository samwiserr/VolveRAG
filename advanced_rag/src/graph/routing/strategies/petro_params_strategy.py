"""
Routing strategy for petrophysical parameters queries.
"""
import re
from pathlib import Path
from langchain_core.messages import AIMessage
from src.normalize.query_normalizer import extract_well, NormalizedQuery
from src.core.result import Result, AppError, ErrorType
from src.core.logging import get_logger
from .base import RoutingStrategy

logger = get_logger(__name__)


class PetroParamsRoutingStrategy(RoutingStrategy):
    """
    Routes petrophysical parameter queries to petro params tool.
    
    Priority: 2 (high - parameters are structured data)
    """
    
    @property
    def priority(self) -> int:
        return 2
    
    def should_route(
        self,
        question: str,
        normalized_query: NormalizedQuery,
        tool_query: str,
        persist_dir: str,
    ) -> bool:
        """Check if this is a petrophysical parameter query."""
        ql = question.lower()
        
        # Check for parameter keywords
        param_keywords = [
            "petrophysical parameters", "petrophysical parameter",
            "net to gross", "net-to-gross", "netgros", "net/gross", "ntg", "n/g",
            "phif", "phi", "poro", "porosity",
            "water saturation", "sw",
            "klogh", "permeability", "permeab", "perm"
        ]
        has_param_keyword = (
            any(k in ql for k in param_keywords) or
            bool(re.search(r'\bsw\b', ql, re.IGNORECASE)) or
            bool(re.search(r'\bk\b', ql, re.IGNORECASE))
        )
        
        # Check for well pattern
        extracted_well = extract_well(question)
        has_well_pattern = (
            ("15" in ql and "9" in ql) or
            extracted_well is not None or
            normalized_query.well is not None
        )
        
        # Check if cache exists
        try:
            vectorstore_dir = Path(persist_dir).resolve()
            cache_path = vectorstore_dir / "petro_params_cache.json"
            has_petro_cache = cache_path.exists()
        except Exception:
            has_petro_cache = False
        
        is_param_query = has_param_keyword and (has_petro_cache or has_well_pattern)
        
        if is_param_query:
            logger.info(
                f"[ROUTING] ✅ Detected param query - routing to lookup_petrophysical_params. "
                f"Query: '{question[:100]}'"
            )
        else:
            logger.debug(
                f"[ROUTING] ❌ NOT routing to petro params tool. "
                f"has_param_keyword={has_param_keyword}, "
                f"has_petro_cache={has_petro_cache}, "
                f"has_well_pattern={has_well_pattern}"
            )
        
        return is_param_query
    
    def route(
        self,
        question: str,
        normalized_query: NormalizedQuery,
        tool_query: str,
        persist_dir: str,
    ) -> Result[AIMessage, AppError]:
        """Route to petrophysical parameters tool."""
        try:
            message = self._create_tool_call_message(
                tool_name="lookup_petrophysical_params",
                query=tool_query,
                call_id="call_lookup_petrophysical_params_1",
            )
            return Result.ok(message)
        except Exception as e:
            return Result.from_exception(
                e,
                ErrorType.ROUTING_ERROR,
                context={"strategy": "petro_params", "question": question[:100]}
            )

