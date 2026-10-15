"""Conservative corpus normalization; never infer identities or missing dates."""
from datetime import datetime
import re

def parse_date(value):
    if not value or not isinstance(value,str): return None
    value=value.strip()
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}(?:[T ].*)?',value):
        try:return datetime.fromisoformat(value.replace('Z','+00:00'))
        except ValueError:return None
    # This corpus uses day-month-year: values such as 27-12-24 establish order.
    # Never switch between month-first and day-first on individual rows.
    for fmt in ('%d-%m-%y, %I:%M %p','%d-%m-%Y, %I:%M %p'):
        try:return datetime.strptime(value,fmt)
        except ValueError:pass
    return None

def author_label(value,post_id=None):
    value=str(value or '').strip()
    if value.lower() in {'','unknown','anonymous','[author]','[username]','[redacted]','none','null'}:
        if post_id is None or str(post_id).strip() in {'','None'}:
            raise ValueError('An unavailable author requires a stable post ID')
        return 'unattributed-post-'+str(post_id)
    return value
