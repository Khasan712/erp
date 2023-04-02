from enum import Enum


class ReportModel(Enum):
    contract = 'contract'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]
