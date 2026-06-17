import re
from datetime import datetime

def apply_time(text: str, dt: datetime) -> datetime:
    """Extract time from natural text and apply to datetime."""
    text = text.lower()
    # 12h: "7pm", "7:30 pm", "4:30pm"
    m = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)', text)
    if m:
        hour = int(m.group(1))
        minute = int(m.group(2)) if m.group(2) else 0
        ampm = m.group(3)
        if ampm == 'pm' and hour != 12:
            hour += 12
        elif ampm == 'am' and hour == 12:
            hour = 0
        return dt.replace(hour=hour, minute=minute)
    # 24h: "20:00", "15:45"
    m24 = re.search(r'(\d{1,2}):(\d{2})(?!\s*[ap]m)', text)
    if m24:
        return dt.replace(hour=int(m24.group(1)), minute=int(m24.group(2)))
    return dt