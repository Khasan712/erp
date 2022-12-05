from django.urls import path
from .views import ItemListView, ItemDetailView

urlpatterns = [
    path('', ItemListView.as_view()),
    path('get/detail/<id>', ItemDetailView.as_view())
]