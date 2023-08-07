from rest_framework import status
from rest_framework.exceptions import ParseError, NotFound
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from modems.models import Modem
from sms.serializers import SMSSerializer, ByPhoneSerializer
from sms.models import SMS


class SMSListView(ListAPIView):
    """
    A view to retrieve a list of SMS messages based on a provided modem index.

    This view allows fetching all SMS messages associated with a specific modem
    or all SMS messages if no index is provided.

    Args:
        index (int, optional): The ID of the modem to filter SMS messages.

    Returns:
        QuerySet: The queryset containing the SMS messages based on the provided index,
        or all SMS messages if no index is provided.

    Raises:
        ParseError: If the provided index value is not a valid integer.
        NotFound: If the modem with the provided index does not exist.
    """
    serializer_class = SMSSerializer

    def get_queryset(self):
        index = self.request.query_params.get('index')
        if index:
            try:
                index = int(index)
                modem = Modem.objects.get(id=index)
                return SMS.objects.filter(modem=modem)
            except ValueError:
                # If the provided index value is not a valid integer, raise a ParseError.
                raise ParseError({'message': 'Invalid index value. Please provide a valid integer.'})
            except Modem.DoesNotExist:
                # If the modem with the provided index does not exist, raise a NotFound error.
                raise NotFound({'message': 'Modem with the provided index does not exist.'})

        # If no index is provided, return all SMS messages from the database.
        return SMS.objects.all()


class SMSByPhoneNumberAPIView(ListAPIView):
    """
    A view to retrieve a list of modems based on a provided phone number.

    This view allows fetching all modems associated with a specific phone number.

    Args:
        phone_number (str, optional): The phone number to filter modems.

    Returns:
        QuerySet: The queryset containing the modems based on the provided phone number.

    Raises:
        None.
    """
    serializer_class = ByPhoneSerializer

    def get_queryset(self):
        phone_number = self.request.query_params.get('phone_number')

        if phone_number:
            return Modem.objects.filter(phone_number=phone_number)

        # If no 'phone_number' is provided, return an empty queryset.
        return Modem.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            # If no modems are found for the provided phone number, return a 404 NOT FOUND response.
            return Response(data={"message": "Phone number not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(queryset, many=True)
        # Return the serialized data in the response.
        return Response(serializer.data)
