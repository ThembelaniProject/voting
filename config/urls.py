from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "Pheli FM 95.0 Competition Control"
admin.site.site_title = "Pheli FM Admin"
admin.site.index_title = "Manage DJs and weekly survival rounds"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("competition.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
