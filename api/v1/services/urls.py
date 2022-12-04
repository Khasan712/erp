from django.urls import path

from .views import (
    ServicePostListAPIView,
    ServiceDetailAPIView,
    CommodityPostListAPIView,
    CommodityDetailAPIView,
    ConsultantPostListAPIView,
    ConsultantDetailAPIView,
    CheckServiceStatus
)

urlpatterns = [
    path('list/', ServicePostListAPIView.as_view()),
    path('detail/', ServiceDetailAPIView.as_view()),
    path('commodity/list/', CommodityPostListAPIView.as_view()),
    path('commodity/detail/', CommodityDetailAPIView.as_view()),
    path('consultant/list/', ConsultantPostListAPIView.as_view()),
    path('consultant/detail/', ConsultantDetailAPIView.as_view()),
    path('status/', CheckServiceStatus.as_view()),
]
