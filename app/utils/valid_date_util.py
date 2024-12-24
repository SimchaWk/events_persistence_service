from datetime import datetime


def is_valid_date(date_str: str) -> bool:
    """Validate date string format"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False
