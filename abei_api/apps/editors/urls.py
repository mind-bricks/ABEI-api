from django.urls import (
    include,
    path,
)
from rest_framework_extensions.routers import (
    ExtendedDefaultRouter,
)

from .views import (
    ProcedureViewSet,
    ProcedureJointViewSet,
    ProcedureJointInputViewSet,
    ProcedureInputViewSet,
    ProcedureOutputViewSet,
    ProcedureSiteViewSet,
    ProcedureSiteBaseSitesViewSet,
)

app_name = 'editors'
router = ExtendedDefaultRouter()
router_site = router.register(
    r'sites',
    ProcedureSiteViewSet,
    basename='sites',
)
router_site.register(
    r'base-sites',
    ProcedureSiteBaseSitesViewSet,
    basename='site-base-sites',
    parents_query_lookups=['sub__signature'],
)
router_procedure = router.register(
    r'procedures',
    ProcedureViewSet,
    basename='procedures',
)
router_procedure.register(
    r'inputs',
    ProcedureInputViewSet,
    basename='procedure-inputs',
    parents_query_lookups=['procedure__signature'],
)
router_procedure.register(
    r'outputs',
    ProcedureOutputViewSet,
    basename='procedure-outputs',
    parents_query_lookups=['procedure__signature'],
)
router_joints = router_procedure.register(
    r'joints',
    ProcedureJointViewSet,
    basename='procedure-joints',
    parents_query_lookups=['outer_procedure__signature'],
)
router_joints.register(
    r'inputs',
    ProcedureJointInputViewSet,
    basename='procedure-joint-inputs',
    parents_query_lookups=[
        'joint__outer_procedure__signature',
        'joint__signature',
    ],
)

urlpatterns = [
    path('', include(router.urls)),
]
