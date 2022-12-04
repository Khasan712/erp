# myapp/handlers.py
from corsheaders.signals import check_request_enabled


def cors_allow_api_organization(sender, request, **kwargs):
    return request.path.startswith("/api/organization/")


check_request_enabled.connect(cors_allow_api_organization)
