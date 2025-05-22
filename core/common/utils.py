from datetime import datetime
from typing import Any, Dict, List, Optional
import json
from flask import jsonify

def to_dict(obj: Any) -> Dict:
    """Convert an object to a dictionary."""
    if hasattr(obj, '__dict__'):
        return {k: to_dict(v) for k, v in obj.__dict__.items() 
                if not k.startswith('_')}
    elif isinstance(obj, (list, tuple)):
        return [to_dict(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: to_dict(v) for k, v in obj.items()}
    elif isinstance(obj, datetime):
        return obj.isoformat()
    return obj

def paginate(pagination, transform_func=None):
    """
    Helper function to format paginated results.
    
    Args:
        pagination: SQLAlchemy pagination object
        transform_func: Optional function to transform each item in the results
    
    Returns:
        dict: Formatted pagination response
    """
    items = pagination.items
    if transform_func:
        items = [transform_func(item) for item in items]
    else:
        items = [item.to_dict() for item in items]

    return {
        'items': items,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'total': pagination.total,
        'pages': pagination.pages,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev,
        'next_page': pagination.next_num if pagination.has_next else None,
        'prev_page': pagination.prev_num if pagination.has_prev else None
    }

def format_currency(amount: float, currency: str = 'USD') -> str:
    """Format currency amount."""
    currency_symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥',
        'KZT': '₸'
    }
    symbol = currency_symbols.get(currency, currency)
    return f"{symbol}{amount:,.2f}"
