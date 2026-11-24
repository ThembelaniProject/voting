from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Pheli FM 95.0 Competition Control"
admin.site.site_title = "Pheli FM Admin"
admin.site.index_title = "Manage DJs and weekly survival rounds"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("competition.urls")),
]
