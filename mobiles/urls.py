from django.conf.urls import url, include

from rest_framework import routers, serializers, viewsets

from .models import Mobile
from . import views


# # Serializers define the API representation.
# class MobileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Mobile
#         fields = ('phone_number', 'owner', 'created_date', 'last_texted', 'state')
#
#
# # ViewSets define the view behavior.
# class MobileViewSet(viewsets.ModelViewSet):
#     queryset = Mobile.objects.all()
#     serializer_class = MobileSerializer
#
# router = routers.DefaultRouter()
# router.register(r'mobiles', MobileViewSet)

urlpatterns = [
    # url(r'^$', views.textivist_account_list, name='textivist_account_list'),
    # url(r'^', include(router.urls)),

    # Endpoint for Twilio messages
    url(r'^sms_received$', views.sms_received, name='sms_received'),

    # ex: /
    url(r'^$', views.index, name='index'),
    # ex: /textivist/5/
    url(r'^textivist/(?P<textivist_id>[0-9]+)/$', views.tt_account, name='tt_account'),
    # ex: /textivist/5/organisation/4/
    url(r'^textivist/(?P<textivist_id>[0-9]+)/organisation/(?P<organisation_id>[0-9]+)/$', views.organisation, name='organisation'),
    # ex: /batch/add
    url(r'^batch/add/$', views.create_batch, name='create_batch'),
    # ex: /mobile/5/
    url(r'^mobile/(?P<mobile_id>.+)/$', views.mobile, name='mobile'),
    # ex: /help
    url(r'^help/$', views.help, name='help'),
]