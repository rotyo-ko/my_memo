from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from memo import api_views as memo_api_views

router = routers.DefaultRouter()
router.register("memo", memo_api_views.MemoViewSet, basename="memo")


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("memo.urls")),
    path("accounts/", include("accounts.urls")),
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
]
