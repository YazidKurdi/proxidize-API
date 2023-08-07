from rest_framework import serializers

from modems.models import Modem
from sms.models import SMS


class SMSSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMS
        exclude = ('modem',)


class ByPhoneSerializer(serializers.ModelSerializer):

    message = serializers.SerializerMethodField()
    sms_messages = SMSSerializer(many=True, source="modem")

    class Meta:
        model = Modem
        fields = (
            "phone_number",
            "id",
            "message",
            "sms_messages"
        )

    def get_message(self, instance):
        return "SMS messages fetched successfully."
