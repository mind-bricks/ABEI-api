from django.urls import (
    include,
    path,
)
from rest_framework import (
    routers,
)

from .views import (
    ProcedureRunViewSet,
)

app_name = 'executors'
router = routers.DefaultRouter()
router.register(
    'runs',
    ProcedureRunViewSet,
    basename='runs',
)

urlpatterns = [
    path('', include(router.urls)),
]
