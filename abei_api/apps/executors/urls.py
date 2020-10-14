from django.urls import (
    include,
    path,
)
from rest_framework_extensions import (
    routers,
)

from .views import (
    ProcedureSiteViewSet,
    ProcedureViewSet,
    ProcedureRunViewSet,
    ProcedureRunLogViewSet,
)

app_name = 'executors'
router = routers.ExtendedDefaultRouter()
router.register(
    'sites',
    ProcedureSiteViewSet,
    basename='sites',
).register(
    'procedures',
    ProcedureViewSet,
    basename='procedures',
    parents_query_lookups=['site__signature'],
).register(
    'runs',
    ProcedureRunViewSet,
    basename='runs',
    parents_query_lookups=[
        'procedure__site__signature',
        'procedure__signature',
    ],
)
router.register(
    'run-logs',
    ProcedureRunLogViewSet,
    basename='run-logs',
)

urlpatterns = [
    path('', include(router.urls)),
]
