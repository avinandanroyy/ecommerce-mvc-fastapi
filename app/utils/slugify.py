from typing import Any, Optional


def slugify(text: str) -> str:
    if not text:
        return ""
    
    import re
    
    text = text.lower().strip()
    
    text = re.sub(r"[\s_]+", "-", text)
    
    text = re.sub(r"[^a-z0-9-]", "", text)
    
    text = re.sub(r"-+", "-", text)
    
    text = text.strip("-")
    
    return text if text else "unknown"
