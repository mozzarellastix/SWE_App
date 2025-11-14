from django.contrib import admin

from django.urls import path, include

# Register your models here.


# just testing stuff out - ash
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('polls.urls')),
]