from django.urls import path

from sms.views import SMSListView, SMSByPhoneNumberAPIView

urlpatterns = [
    path('sms/get/', SMSListView.as_view(), name='sms-list-index'),
    path('sms/fetch_sms_phone_number/', SMSByPhoneNumberAPIView.as_view(), name='sms-list-number'),
]
