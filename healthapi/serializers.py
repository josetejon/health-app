from rest_framework_mongoengine import serializers
from rest_framework import serializers as serial

from .models import Observation, Component


class ComponentSerializer(serializers.DocumentSerializer):
    class Meta:
        model = Component
        fields = ("observation_name", "value", "value_type", "value_unit")


class ObservationSerializer(serializers.DocumentSerializer):
    components = ComponentSerializer(many=True, required=False)

    class Meta:
        model = Observation
        fields = ("monitored_id", "observation_name", "issued", "value", "value_type", "value_unit", "components")


class AggregationSerializer(serial.Serializer):

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    aggregator = serial.CharField(max_length=200, required=True)
    observation_name = serial.CharField(max_length=200, required=True)
    value = serial.CharField(max_length=20, required=True)
    value_unit = serial.CharField(max_length=20, required=True)


class ErrorSerializer(serial.Serializer):
    def update(self, instance, validated_data):
        pass
    def create(self, validated_data):
        pass

    error_description = serial.CharField(max_length=500, required=True)

