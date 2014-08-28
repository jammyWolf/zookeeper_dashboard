from django.conf.urls.defaults import *

urlpatterns = patterns('zookeeper_dashboard.zkadmin.views',
    (r'^(?P<cluster_name>\w+)/$','detail'), 
    (r'^$','index'), 
)
