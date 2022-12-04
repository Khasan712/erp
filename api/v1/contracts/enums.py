from enum import Enum


class ServiceChoice(Enum):
    commodity = 'commodity'
    consultant = 'consultant'
    service = 'service'

    @classmethod
    def choices(cls):
        return [(key.value, key.name)for key in cls]
