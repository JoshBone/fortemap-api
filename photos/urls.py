from django.urls import path

from photos.views import PhotosList, PhotosDetail

app_name = 'photos'

urlpatterns = [
    path('', PhotosList.as_view(), name='photos-list'),
    path('<int:pk>/', PhotosDetail.as_view(), name='photos-detail'),
]