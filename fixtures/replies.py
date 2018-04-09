HELP_TEXT = """
Add this bot to your groups, then use /remind <b>replying to someone</b> to set an alert for that message!

For example you can use:
<b>/remind 2 minutes</b>
or -
<b>/r 2m</b>

and even
<b>/remind 1 hour 30 minutes</b>
- or -
<b>/r 1h 30m</b>
"""

TAG_URL = '<a href="tg://user?id={id}">{name}</a>'

USAGE_TEXT = """
<i>Samples:</i>
/r 2 minutes
/r 2m
/r 1d 2h
"""

SUCCESS_TEXT = """
Done, I've set my alarm at \
<a href="http://www.thetimezoneconverter.com/?t={hour}:{minute}&tz=UTC">\
{year}-{month}-{day} {hour}:{minute} UTC\
</a> \
for you. See you later 👌
"""

ALERT_TEXT = """
Hey {}, remember the alert you set?
It's now!
"""