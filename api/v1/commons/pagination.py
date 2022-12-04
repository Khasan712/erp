from rest_framework.pagination import LimitOffsetPagination
from rest_framework import pagination


class CustomPagination(pagination.PageNumberPagination):
    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 50
    page_query_param = 'p'


class CustomLimitPagination(pagination.LimitOffsetPagination):
    default_limit = 2
    limit_query_param = 'l'
    offset_query_param = 'o'
    max_limit = 50


def make_pagination(request, serializer, data):
    paginator = LimitOffsetPagination()
    result_page = paginator.paginate_queryset(data, request)
    serializer = serializer(result_page, many=True)
    paginator_response = paginator.get_paginated_response(result_page).data
    return {
        "success": True,
        "message": "Successfully got list",
        "error": [],
        "count": paginator_response["count"],
        "next": paginator_response["next"],
        "previous": paginator_response["previous"],
        "data": serializer.data,
    }




