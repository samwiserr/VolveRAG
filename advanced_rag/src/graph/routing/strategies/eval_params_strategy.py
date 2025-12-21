"""
Routing strategy for evaluation parameters queries.
"""
from langchain_core.messages import AIMessage
from src.normalize.query_normalizer import extract_well, NormalizedQuery
from src.core.result import Result, AppError, ErrorType
from src.core.logging import get_logger
from .base import RoutingStrategy

logger = get_logger(__name__)


class EvalParamsRoutingStrategy(RoutingStrategy):
    """
    Routes evaluation parameter queries to eval params tool.
    
    Priority: 3 (high - evaluation parameters are structured data)
    """
    
    @property
    def priority(self) -> int:
        return 3
    
    def should_route(
        self,
        question: str,
        normalized_query: NormalizedQuery,
        tool_query: str,
        persist_dir: str,
    ) -> bool:
        """Check if this is an evaluation parameters query."""
        ql = question.lower()
        
        # Check for well pattern
        extracted_well = extract_well(question)
        has_well_pattern = (
            ("15" in ql and "9" in ql) or
            extracted_well is not None or
            normalized_query.well is not None
        )
        
        # Check for evaluation parameter terms
        eval_params_terms = [
            "evaluation parameter", "evaluation parameters",
            "grmax", "grmin",
            "rhoma", "rhofl",
            "archie a", "archie m", "archie n",
            "tortuosity factor",
            "cementation exponent",
            "saturation exponent",
            "matrix density",
            "fluid density",
            "ρma", "ρfl",
        ]
        is_eval_params = has_well_pattern and any(t in ql for t in eval_params_terms)
        
        if is_eval_params:
            logger.info(
                f"[ROUTING] ✅ Detected eval params query - routing to lookup_evaluation_parameters. "
                f"Query: '{question[:100]}', well_pattern={has_well_pattern}, "
                f"extracted_well='{extracted_well}'"
            )
        
        return is_eval_params
    
    def route(
        self,
        question: str,
        normalized_query: NormalizedQuery,
        tool_query: str,
        persist_dir: str,
    ) -> Result[AIMessage, AppError]:
        """Route to evaluation parameters tool with retriever fallback."""
        try:
            ql = question.lower()
            
            # Enhance retriever query with evaluation parameter synonyms
            eval_param_synonyms = {
                "matrix density": ["rhoma", "ρma", "matrix density", "evaluation parameters", "density matrix"],
                "fluid density": ["rhofl", "ρfl", "fluid density", "evaluation parameters", "density fluid"],
                "density": ["rhoma", "rhofl", "ρma", "ρfl", "matrix density", "fluid density", "evaluation parameters"],
                "grmax": ["gr max", "gamma ray max", "gr maximum", "evaluation parameters"],
                "grmin": ["gr min", "gamma ray min", "gr minimum", "evaluation parameters"],
                "archie": ["archie a", "archie m", "archie n", "tortuosity", "cementation", "saturation exponent", "evaluation parameters"],
            }
            
            # Build enhanced query with synonyms
            enhanced_retriever_query = tool_query
            for term, synonyms in eval_param_synonyms.items():
                if term in ql:
                    enhanced_retriever_query = f"{tool_query} {' '.join(synonyms)}"
                    logger.info(
                        f"[ROUTING] Enhanced retriever query with eval param synonyms: "
                        f"'{enhanced_retriever_query[:150]}'"
                    )
                    break
            
            # Add retriever as fallback
            additional_tools = [
                {
                    "name": "retrieve_petrophysical_docs",
                    "args": {"query": enhanced_retriever_query},
                    "id": "call_retrieve_petrophysical_docs_eval_fallback_1",
                }
            ]
            
            message = self._create_tool_call_message(
                tool_name="lookup_evaluation_parameters",
                query=tool_query,
                call_id="call_lookup_evaluation_parameters_1",
                additional_tools=additional_tools,
            )
            return Result.ok(message)
        except Exception as e:
            return Result.from_exception(
                e,
                ErrorType.ROUTING_ERROR,
                context={"strategy": "eval_params", "question": question[:100]}
            )

