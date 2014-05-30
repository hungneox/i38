# -*- coding: utf-8 -*-
from datetime import datetime

class Utility(object):
    @staticmethod
    def time_ago(created_at):
        result = {}
        now = datetime.now()
        diff = now - created_at
        if diff.days >= 365:
          result['duration'] = (diff.days // 365)
          result['text'] = "years ago";
        elif diff.days >= 30:
          result['duration'] = (diff.days // 30)
          result['text'] = "months ago";
        elif diff.days > 0:
          result['duration'] = diff.days
          result['text'] = "days ago";
        elif diff.seconds >= 3600:
          result['duration'] = (diff.seconds // 3600)
          result['text'] = "hours ago";
        elif diff.seconds > 60:
          result['duration'] = (diff.seconds // 60)
          result['text'] = "minutes ago";
        elif diff.seconds > 0:
          result['duration'] = diff.seconds
          result['text'] = "seconds ago";
        return result
