from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    path('v1/photos/', include('photos.urls', namespace='photos-v1')),
]
