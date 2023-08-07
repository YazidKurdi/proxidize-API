from rest_framework import serializers
from .models import Modem, FeatureSettings


class ModemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modem
        fields = '__all__'


class CriticalModemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modem
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Scramble the response when critical_mode_enabled is True
        if FeatureSettings.objects.exists() and FeatureSettings.objects.first().critical_mode_enabled:
            # Mask IP fields
            data['public_ip'] = '***.***.***.***'
            data['ipv4'] = '***.***.***.***'
            data['ipv6'] = '****:****:****:****:****:****:****:****'
            # Mask all other fields (excluding IP fields)
            for field in data:
                if field not in ['id','public_ip', 'ipv4', 'ipv6']:
                    data[field] = '********'
        return data


class FeatureSettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = FeatureSettings
        fields = ['critical_mode_enabled']


class RotationParamsSerializer(serializers.Serializer):

    index = serializers.CharField(max_length=10)
    day = serializers.IntegerField(min_value=0, max_value=29, required=False)
    hour = serializers.IntegerField(min_value=0, max_value=22, required=False)
    min = serializers.IntegerField(min_value=0, max_value=58, required=False)

    def validate(self, data):
        count = sum(param is not None for param in [data.get('day'), data.get('hour'), data.get('min')])
        if count != 1:
            raise serializers.ValidationError("Please provide exactly one interval parameter.")
        return data