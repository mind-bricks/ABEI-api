from django.urls import (
    include,
    path,
)
from rest_framework_extensions import (
    routers,
)

from .views import (
    ProcedureViewSet,
    ProcedureJointViewSet,
    ProcedureJointLinkViewSet,
    ProcedureInputViewSet,
    ProcedureOutputViewSet,
    ProcedureSiteViewSet,
    ProcedureSiteBaseSitesViewSet,
)

app_name = 'editors'
router = routers.ExtendedDefaultRouter()
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
router_procedure = router_site.register(
    r'procedures',
    ProcedureViewSet,
    basename='procedures',
    parents_query_lookups=['site__signature'],
)
router_procedure.register(
    r'inputs',
    ProcedureInputViewSet,
    basename='procedure-inputs',
    parents_query_lookups=[
        'procedure__site__signature',
        'procedure__signature',
    ],
)
router_procedure.register(
    r'outputs',
    ProcedureOutputViewSet,
    basename='procedure-outputs',
    parents_query_lookups=[
        'procedure__site__signature',
        'procedure__signature'
    ],
)
router_joints = router_procedure.register(
    r'joints',
    ProcedureJointViewSet,
    basename='procedure-joints',
    parents_query_lookups=[
        'outer_procedure__site__signature',
        'outer_procedure__signature',
    ],
)
router_joints.register(
    r'links',
    ProcedureJointLinkViewSet,
    basename='procedure-joint-links',
    parents_query_lookups=[
        'joint__outer_procedure__site__signature',
        'joint__outer_procedure__signature',
        'joint__signature',
    ],
)

urlpatterns = [
    path('', include(router.urls)),
]
