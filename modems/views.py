import json

from django_celery_beat.models import IntervalSchedule, PeriodicTask
from rest_framework import status
from rest_framework.generics import ListAPIView, UpdateAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from modems import StandardResultsSetPagination
from .models import Modem, FeatureSettings
from .serializers import ModemSerializer, CriticalModemSerializer, FeatureSettingsSerializer, RotationParamsSerializer


class ModemListView(ListAPIView):
    """
    View for listing Modems with optional critical mode serialization.

    This view retrieves a list of Modems from the database and serializes them using either the standard
    serializer or the critical modem serializer based on the critical_mode_enabled flag from the FeatureSettings model.
    If no FeatureSettings object exists, it creates one with critical_mode_enabled set to False.
    """

    queryset = Modem.objects.all()
    serializer_class = ModemSerializer
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        # Check if critical mode is enabled in FeatureSettings and use the appropriate serializer
        if FeatureSettings.objects.exists() and FeatureSettings.objects.first().critical_mode_enabled:
            return CriticalModemSerializer
        return super().get_serializer_class()

    def get_feature_settings(self):
        # Retrieve FeatureSettings object if it exists, or create a new one with critical_mode_enabled set to False
        if FeatureSettings.objects.exists():
            return FeatureSettings.objects.first()
        else:
            return FeatureSettings.objects.create(critical_mode_enabled=False)

    def list(self, request, *args, **kwargs):
        # Get the FeatureSettings object and list of Modems
        feature_settings = self.get_feature_settings()
        response = super().list(request, *args, **kwargs)

        return Response(response.data, status=status.HTTP_200_OK)


class FeatureSettingsUpdateView(UpdateAPIView):
    """
    View for updating FeatureSettings critical mode.

    This view handles updates to the FeatureSettings model's critical_mode_enabled field based on the 'toggle' query parameter
    received in the request.
    """
    serializer_class = FeatureSettingsSerializer

    def get_object(self, queryset=None):
        # Get the first FeatureSettings object from the database
        return FeatureSettings.objects.first()

    def update(self, request, *args, **kwargs):
        # Get the 'toggle' query parameter from the request
        toggle = request.query_params.get('toggle', None)

        # Check if 'toggle' parameter has a valid value ('enable' or 'disable')
        if toggle not in ['enable', 'disable']:
            return Response({'error': 'Invalid toggle value'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the FeatureSettings object
        instance = self.get_object()

        # Update the critical_mode_enabled field based on the 'toggle' parameter
        if toggle == 'enable':
            instance.critical_mode_enabled = True
        else:
            instance.critical_mode_enabled = False

        # Save the updated FeatureSettings object
        instance.save()

        # Serialize the updated object and return it with a 200 OK status
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RotateAllModemsView(APIView):
    """
    View for rotating all modems.

    This view triggers the rotation process for all modems in the database by calling the 'rotate_all()' method of the Modem model.
    """

    def get(self, request):
        # Trigger the 'rotate_all()' method of the Modem model
        Modem.rotate_all()
        return Response({"message": "All modems rotated successfully."})


class RotateSpecificModemView(APIView):
    """
    View for rotating a specific modem.

    This view rotates a specific modem identified by its 'index' query parameter
    by calling the 'reboot_modem()' method of the Modem model.
    """

    def get(self, request):
        # Get the 'index' query parameter from the request
        modem_index = request.query_params.get('index')

        # Retrieve the specific modem with the given 'index' from the database or raise a 404 error if not found
        modem = get_object_or_404(Modem, pk=modem_index)

        # Trigger the 'reboot_modem()' method of the Modem model for the specific modem
        modem.reboot_modem()

        return Response({"message": f"Modem {modem_index} rotated successfully."})


class CustomRotView(APIView):
    """
    View for custom IP rotation scheduling.

    This view handles GET requests to schedule custom IP rotation tasks for modems. It receives the 'index' query parameter
    to identify the modem and the 'day', 'hour', and 'min' query parameters to specify the rotation interval.
    """
    def get(self, request):
        # Deserialize and validate the 'index', 'day', 'hour', and 'min' query parameters
        serializer = RotationParamsSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        # Get the 'index' query parameter from the request
        dongle_index = request.query_params.get('index')

        # Get the validated rotation interval data from the serializer
        interval_data = serializer.validated_data
        day = interval_data.get('day', 0)
        hour = interval_data.get('hour', 0)
        minutes = interval_data.get('min', 0)

        # Check if any of the interval components is set to 0
        if day == hour == minutes == 0:
            return Response({"message": "Interval must be greater than 0"}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate the total rotation interval in minutes
        interval_in_minutes = day * 24 * 60 + hour * 60 + minutes

        if dongle_index.lower() == 'all':
            # Assign the IP rotation task to all modems
            modems = Modem.objects.all()
            for modem in modems:
                self._create_or_update_task(modem, interval_in_minutes)
            message = f"IP Rotation scheduled every {interval_in_minutes} minutes for all modems"
        else:
            # Assign the IP rotation task to the specified modem
            modem = get_object_or_404(Modem, pk=dongle_index)
            self._create_or_update_task(modem, interval_in_minutes)
            message = f"IP Rotation scheduled every {interval_in_minutes} minutes for Modem {dongle_index}"

        response_data = {"message": message}
        return Response(response_data)

    def _create_or_update_task(self, modem, interval_in_minutes):
        # Create or update the IP rotation task for the modem
        task_name = f'Rotating IP for Modem {modem.pk}'
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=interval_in_minutes,
            period=IntervalSchedule.MINUTES,
        )

        try:
            existing_task = PeriodicTask.objects.get(name=task_name)
            if existing_task.interval.every != interval_in_minutes:
                existing_task.interval = schedule
                existing_task.save()
            return existing_task
        except PeriodicTask.DoesNotExist:
            task_args = json.dumps([modem.pk])
            return PeriodicTask.objects.create(
                interval=schedule,
                name=task_name,
                task='modems.tasks.rotate_ip',
                args=task_args,
            )

class ClearTaskInterval(APIView):
    """
    View for clearing all IP rotation task intervals.
    """

    def get(self, request):
        # Clear all IP rotation task intervals
        PeriodicTask.objects.all().delete()
        IntervalSchedule.objects.all().delete()
        return Response({"message": "IP rotation intervals cleared successfully."})