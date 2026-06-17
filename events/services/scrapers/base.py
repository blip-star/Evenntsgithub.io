from contextlib import contextmanager
from datetime import datetime, timedelta

def dedupe_events(events):
    unique = {}
    for ev in events:
        key = (ev['title'].lower().strip(), ev['venue'].lower().strip(), ev['date'][:10])
        if key not in unique:
            unique[key] = ev
    return list(unique.values())

@contextmanager
def shared_browser():
    yield None
