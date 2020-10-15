from django.urls import (
    include,
    path,
)
from rest_framework_swagger.views import (
    get_swagger_view
)

urlpatterns = [
    path('', include('apps.editors.urls')),
    path('', include('apps.executors.urls')),
    path('swagger/', get_swagger_view(title='ABEI API')),
]
