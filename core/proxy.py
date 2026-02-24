from typing import Optional, Dict

def get_proxy_dict(proxy_url: Optional[str]) -> Optional[Dict[str, str]]:
    """
    Returns a dictionary for httpx proxy configuration.
    Example: {"all://": "http://user:pass@host:port"}
    """
    if not proxy_url:
        return None
    return {"all://": proxy_url}
