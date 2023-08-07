from django.urls import path

from modems.views import ModemListView, FeatureSettingsUpdateView, RotateAllModemsView, RotateSpecificModemView, \
    CustomRotView, ClearTaskInterval

urlpatterns = [
    path('list_modems/', ModemListView.as_view(), name='modem-list'),
    path('crit_mode/', FeatureSettingsUpdateView.as_view(), name='critical-mode-update'),
    path('rotate/', RotateAllModemsView.as_view(), name='rotate-all-modems'),
    path('reboot_modem/', RotateSpecificModemView.as_view(), name='reboot-modem'),
    path('custom_rot/', CustomRotView.as_view(), name='custom-rot'),
    path('clear_rot/', ClearTaskInterval.as_view(), name='clear-rot'),
]
