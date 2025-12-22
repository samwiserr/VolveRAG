"""
Centralized path resolution with fallback strategies.

This module provides consistent path resolution across the codebase,
replacing scattered path resolution logic.
"""
from pathlib import Path
from typing import Optional
from .config import get_config, reset_config
from .result import Result, AppError, ErrorType


class PathResolver:
    """
    Centralized path resolution with fallback strategies.
    
    This class provides consistent path resolution across the codebase,
    handling various path formats and fallback scenarios.
    """
    
    @staticmethod
    def resolve_vectorstore(base_path: Optional[Path] = None) -> Path:
        """
        Resolve vectorstore path.
        
        Args:
            base_path: Optional base path (overrides config)
            
        Returns:
            Resolved Path to vectorstore directory
        """
        if base_path:
            return Path(base_path).resolve()
        # Always get fresh config to ensure test environment variables are respected
        # In tests, config should be reset before calling this
        config = get_config()
        return config.persist_directory.resolve()
    
    @staticmethod
    def resolve_documents(base_path: Optional[Path] = None) -> Result[Path, AppError]:
        """
        Resolve documents path with fallback strategies.
        
        Args:
            base_path: Optional base path (overrides config)
            
        Returns:
            Result containing resolved Path or error
        """
        config = get_config()
        
        # If explicit path provided, use it
        if base_path:
            path = Path(base_path)
            if path.exists():
                return Result.ok(path.resolve())
            return Result.err(AppError(
                type=ErrorType.CONFIGURATION_ERROR,
                message=f"Documents path does not exist: {base_path}",
                context={"path": str(base_path)}
            ))
        
        # Try config path
        if config.documents_path and config.documents_path.exists():
            return Result.ok(config.documents_path.resolve())
        
        # Fallback strategies
        candidates = [
            Path("../spwla_volve-main"),
            Path("./spwla_volve-main"),
            Path.cwd() / "spwla_volve-main",
            Path(__file__).resolve().parents[3] / "spwla_volve-main",  # From src/core/
        ]
        
        for candidate in candidates:
            if candidate.exists():
                return Result.ok(candidate.resolve())
        
        return Result.err(AppError(
            type=ErrorType.CONFIGURATION_ERROR,
            message="Documents path not found. Please set DOCUMENTS_PATH environment variable.",
            context={"tried_paths": [str(c) for c in candidates]}
        ))
    
    @staticmethod
    def resolve_cache_path(cache_name: str, base_dir: Optional[Path] = None) -> Path:
        """
        Resolve cache file path.
        
        Args:
            cache_name: Name of cache file (e.g., "petro_params_cache.json")
            base_dir: Optional base directory (defaults to vectorstore)
            
        Returns:
            Resolved Path to cache file
        """
        base = base_dir or PathResolver.resolve_vectorstore()
        return (base / cache_name).resolve()
    
    @staticmethod
    def resolve_well_picks_dat(base_path: Optional[Path] = None) -> Result[Path, AppError]:
        """
        Resolve well picks .dat file path.
        
        Args:
            base_path: Optional base path for documents directory
            
        Returns:
            Result containing resolved Path or error
        """
        # First try to resolve documents directory
        docs_result = PathResolver.resolve_documents(base_path)
        if docs_result.is_err():
            # If documents path not found, try common locations
            candidates = [
                Path("spwla_volve-main") / "Well_picks_Volve_v1.dat",
                Path("../spwla_volve-main") / "Well_picks_Volve_v1.dat",
                Path("./") / "Well_picks_Volve_v1.dat",
                Path.cwd().parent / "spwla_volve-main" / "Well_picks_Volve_v1.dat",
            ]
            for candidate in candidates:
                if candidate.exists():
                    return Result.ok(candidate.resolve())
            return Result.err(AppError(
                type=ErrorType.NOT_FOUND_ERROR,
                message="Well picks .dat file not found",
                context={"tried_paths": [str(c) for c in candidates]}
            ))
        
        docs_path = docs_result.unwrap()
        dat_path = docs_path / "Well_picks_Volve_v1.dat"
        
        if dat_path.exists():
            return Result.ok(dat_path.resolve())
        
        return Result.err(AppError(
            type=ErrorType.NOT_FOUND_ERROR,
            message=f"Well picks .dat file not found at {dat_path}",
            context={"documents_path": str(docs_path)}
        ))

