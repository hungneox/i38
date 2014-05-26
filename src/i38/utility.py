# -*- coding: utf-8 -*-
from datetime import datetime

class Utility(object):
    @staticmethod
    def time_ago(created_at):
        if not created_at:
            return "Undefined"
        now = datetime.now()
        diff = now - created_at
        if diff.days >= 365:
            return "%s years ago" % (diff.days // 365)
        elif diff.days >= 30:
            return "%s months ago" % (diff.days // 30)
        elif diff.days > 0:
            return "%s days ago" % diff.days
        elif diff.seconds >= 3600:
            return "%s hours ago" % (diff.seconds // 3600)
        elif diff.seconds > 60:
            return "%s minutes ago" % (diff.seconds // 60)
        elif diff.seconds > 0:
            return "%s seconds ago" % diff.seconds
