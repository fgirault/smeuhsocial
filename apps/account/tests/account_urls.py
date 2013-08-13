from django.conf.urls import *


urlpatterns = patterns("",
    url(r'^account/', include('pinax.apps.account.urls')),
)
