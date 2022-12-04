# myapp/handlers.py
from corsheaders.signals import check_request_enabled


def cors_allow_api_sourcing(sender, request, **kwargs):
    return request.path.startswith("/api/sourcing/")


check_request_enabled.connect(cors_allow_api_sourcing)
