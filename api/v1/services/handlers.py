# myapp/handlers.py
from corsheaders.signals import check_request_enabled


def cors_allow_api_service(sender, request, **kwargs):
    return request.path.startswith("/api/services/")


check_request_enabled.connect(cors_allow_api_service)
