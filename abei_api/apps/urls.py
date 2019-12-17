from django.urls import (
    include,
    path,
)
from rest_framework_swagger.views import (
    get_swagger_view
)

urlpatterns = [
    path('editors/', include('apps.editors.urls')),
    path('executors/', include('apps.executors.urls')),
    path('documents/', get_swagger_view(title='ABEI API')),
]
