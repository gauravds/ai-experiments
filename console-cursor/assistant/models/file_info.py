"""
Data models for the Code Assistant.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class FileInfo:
    """Information about a file in the project."""

    path: str
    content: str
    language: str
    functions: List[Dict[str, Any]] = field(default_factory=list)
    classes: List[Dict[str, Any]] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
