from django.urls import include, path
from . import views

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path(r'observations', views.ObservationApiView.as_view()),
    path(r'components', views.ObservationApiView.as_view()),
    path('monitored/<int:monitored_id>/observations', views.MonitoredObservationApiView.as_view()),
    path(r'api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]