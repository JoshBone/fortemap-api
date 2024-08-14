from django.urls import path

from photos.views import PhotosList, PhotosDetail, PlacesList

app_name = 'photos'

urlpatterns = [
    path('', PhotosList.as_view(), name='photos-list'),
    path('<int:pk>/', PhotosDetail.as_view(), name='photos-detail'),

    path('places/', PlacesList.as_view(), name='places-list'),
]