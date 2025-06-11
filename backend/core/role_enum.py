from enum import Enum

class RoleEnum(str, Enum):
    guest = "guest"
    registered = "registered"
    verified = "verified"
    org_verified = "org_verified"
    merchant = "merchant"
    merchant_pro = "merchant_pro"
    admin = "admin"
    super_admin = "super_admin"
