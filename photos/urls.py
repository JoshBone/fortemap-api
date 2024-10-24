from django.urls import path

from photos.views import PhotosList, PhotosDetail, PlacesList, LocationsList, LocationsDetail, LocationsCreate, \
    EditorList, PlaceList, LocationsBatchCreate, StatisticsList, PhotoBatchStatusModify

app_name = 'photos'

urlpatterns = [
    path('', PhotosList.as_view(), name='photos-list'),
    path('<int:pk>/', PhotosDetail.as_view(), name='photos-detail'),
    path('<int:pk>/photo_table_filter=<str:photo_table_filter>', PhotosDetail.as_view(), name='photos-detail'),

    path('places/', PlacesList.as_view(), name='places-list'),

    path('stats/', StatisticsList.as_view(), name='statistics-list'),

    path('batch-status/', PhotoBatchStatusModify.as_view(), name='photos-batch-status'),

    path('locations/', LocationsList.as_view(), name='locations-list'),
    path('locations/<int:pk>/', LocationsDetail.as_view(), name='locations-detail'),
    path('locations/create/', LocationsCreate.as_view(), name='locations-create'),
    path('locations/batch-create/', LocationsBatchCreate.as_view(), name='locations-batch-create'),

    path('select/editors', EditorList.as_view(), name='select-editors'),
    path('select/places', PlaceList.as_view(), name='select-places'),
]