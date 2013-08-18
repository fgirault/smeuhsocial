from django.conf.urls import *


urlpatterns = patterns("",
    url(r'^account/', include('account.urls')),
)
