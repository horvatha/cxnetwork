from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('cxnetwork.randomnet.views',
    (r'^$',  'main'),
    (r'^dobokocka/$',  'dice'),
    (r'^dobokocka/(?P<num>\d+)/$',  'dice'),
    (r'^dobokocka/(?P<num>\d+)/flags=(?P<flags>[GDW]{,3})/$',  'dice'),
)

