from django.urls import path

from . import views


urlpatterns = [
    path('category/', views.CategoryRequestView.as_view()),
    path('category/list/', views.CategoryRequestListAPIView.as_view()),
    path('request/', views.SourcingRequestView.as_view()),
    path('request/statistics/', views.SourcingRequestStatusStatisticsView.as_view()),
    path('request/event/', views.SourcingRequestEventView.as_view()),
    path('request/event/by-params/', views.SourcingEventGetByParamsAPIView.as_view()),
    path('request/event/detail/<int:id>', views.SourcingRequestEventDetailView.as_view(), name='event-detail'),
    path('comments/', views.SourcingCommentsView.as_view()),
    path('answer/', views.SupplierAnswerView.as_view()),
    path('upload/', views.MassUpload.as_view()),
    path('download/', views.MassDownload.as_view()),
]
