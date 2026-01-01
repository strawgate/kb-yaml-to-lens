"""Shared configuration model and utility functions for the dashboard compiler."""

from .config import stable_id_generator
from .type_guards import ensure_dict, ensure_list, ensure_str, is_str_dict

__all__ = [
    'ensure_dict',
    'ensure_list',
    'ensure_str',
    'is_str_dict',
    'stable_id_generator',
]
