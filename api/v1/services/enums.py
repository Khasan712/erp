from enum import Enum


class PaymentFor(Enum):
    hourly = 'hourly'
    weekly = 'weekly'
    bi_weekly = 'bi_weekly'
    monthly = 'monthly'
    yearly = 'yearly'

    @classmethod
    def choices(cls):
        return [(key.value, key.name)for key in cls]


class IncreasePayTerms(Enum):
    weekly = 'weekly'
    monthly = 'monthly'
    yearly = 'yearly'

    @classmethod
    def choices(cls):
        return [(key.value, key.name)for key in cls]


class ItemStatuses(Enum):
    active = 'active'
    inactive = 'inactive'
    expired = 'expired'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]
