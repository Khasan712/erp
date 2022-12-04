from enum import Enum

"""
created
assigned
in_progress
outdated
completed
closed
"""

"""
total of request
number of request in each status
"""


class SourcingStatus(Enum):
    created = 'created'
    assigned = 'assigned'
    in_progress = 'in_progress'
    completed = 'completed'
    outdated = 'outdated'
    closed = 'closed'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]
    

class SourcingEvent(Enum):
    rfp = 'rfp'
    rfq = 'rfq'
    rfi = 'rfi'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class SourcingSection(Enum):
    sourcing_event = 'sourcing_event'
    info = 'info'
    questionary = 'questionary'
    category = 'category'
    question = 'question'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class QuestionaryStatus(Enum):
    congratulations = 'congratulations'
    rejected = 'rejected'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class SourcingEventSupplierTimeLine(Enum):
    not_viewed = 'not_viewed'
    in_progress = 'in_progress'
    done = 'done'
    passed = 'passed'
    rejected = 'rejected'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]
