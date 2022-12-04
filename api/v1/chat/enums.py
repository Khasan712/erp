from enum import Enum


class NotificationChoices(Enum):
    s_request = 's_request'
    s_event = 's_event'
    s_category = 's_category'
    s_question = 's_question'
    other = 'other'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]
