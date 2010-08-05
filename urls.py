from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$',     'hive.main.views.welcome'),
    url(r'^missing$', 'hive.main.views.missing', name='missing'),

    url(r'^similar$', 'hive.users.views.similar', name='similar'),
    url(r'^similar/(?P<start>\d+)/(?P<n>\d+)$', 'hive.users.views.similar', name='similar-paged'),
    url(r'^recommend$', 'hive.main.views.recommend', name='recommend'),
    url(r'^recommend/(?P<category_slug>[\w-]*)$', 'hive.main.views.recommend', name='recommend-slugged'),
    url(r'^recommend/(?P<category_slug>[\w-]*)/(?P<start>\d+)/(?P<n>\d+)$', 'hive.main.views.recommend', name='recommend-paged'),

    (r'^account/', include('hive.account.urls')),
    (r'^wiki/', include('hive.wiki.urls')),
    (r'^test/', include('hive.testdata.urls')),
    (r'^user/', include('hive.users.urls')),

    url(r'^item/(?P<item_id>[0-9a-z]+)(?:/(.*))?$', 'hive.main.views.item', name='item'),
    (r'^opinion/set/(?P<item_id>[0-9a-z]+)/(?P<rating>[1-5])$', 'hive.main.views.opinion_set'),
    (r'^opinion/remove/(?P<item_id>[0-9a-z]+)$', 'hive.main.views.opinion_remove'),

    (r'^search$', 'hive.search.views.query'),

    # TEMPORARY, FOR DEVELOPMENT ONLY
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/drx/hive/media'}),
    (r'^favicon.ico$', 'django.views.generic.simple.redirect_to', {'url': '/media/favicon.ico', 'permanent': False}),

    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
)
