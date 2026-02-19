from datetime import datetime, timezone
# import humanize

def human_date(value):
#      Format	   Example
#     %d %B %Y	 31 October 2025
#     %b %d, %Y	 Oct 31, 2025
#     %I:%M %p	 10:35 AM
#     %H:%M	     10:35
    if not value:
        return ""
    return value.astimezone(timezone.utc).strftime('%d %b %Y, %I:%M %p')

# def time_ago(value):
#     if not value:
#         return ""
#     now = datetime.now(timezone.utc)
    # return humanize.naturaltime(now - value)
