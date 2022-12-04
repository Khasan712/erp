from enum import Enum


class SupplierStatusChoice(Enum):
    active = 'active'
    inactive = 'inactive'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

