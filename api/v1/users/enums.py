from enum import Enum


class UserRoles(Enum):
    admin = 'admin'
    contract_administrator = 'contract_administrator'
    category_manager = 'category_manager'
    lawyer = 'lawyer'
    sourcing_administrator = 'sourcing_administrator'
    supplier = 'supplier'
    sourcing_director = 'sourcing_director'
    business_lead = 'business_lead'
    
    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]
