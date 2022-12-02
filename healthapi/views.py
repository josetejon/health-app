from enum import Enum

import bson
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from dateutil.parser import parse
from .serializers import ObservationSerializer, AggregationSerializer, ErrorSerializer
from .models import Observation, Component


class Resources(Enum):
    observation = Observation


class Utils:
    serializer_class = ObservationSerializer

    def get_linked_components(self, observation_list):
        observation_list_with_components = []
        for observation in observation_list:
            observation = self.delete_null_empty_from_dict(observation)
            queryset_components = Component.objects.filter(observation_parent=observation.get("_id"))
            component_list = [component._data for component in queryset_components]
            if component_list:
                observation.setdefault("components", component_list)
            observation_list_with_components.append(observation)

        return observation_list_with_components

    @staticmethod
    def delete_null_empty_from_dict(dictionary):
        return {k: v for k, v in dictionary.items() if v}


class MonitoredObservationApiView(APIView):
    serializer_class = ObservationSerializer
    VALID_QUERY_PARAMS = ["observation_name"]
    utils = Utils()

    def get(self, request, monitored_id, collection):
        resources_dict = {"observations": self.get_observations}

        if collection not in resources_dict.keys():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        params = request.query_params.dict()

        kwargs = {key: value for key, value in params.items() if key in self.VALID_QUERY_PARAMS}

        kwargs.setdefault("monitored_id", monitored_id)

        func = resources_dict.get(collection)
        observation_list_to_serialize = func(kwargs, request)
        serializer = self.serializer_class(observation_list_to_serialize, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_observations(self, input_dict, request):
        if request.query_params.get("latest") == "true":
            queryset_observations = [Observation.objects.filter(input_dict).order_by("-issued").first()]

        else:
            queryset_observations = Observation.objects.filter(**input_dict)
        observation_list = [observation._data for observation in queryset_observations]
        observation_list_to_serialize = self.utils.get_linked_components(observation_list=observation_list)
        return observation_list_to_serialize

class ObservationApiView(APIView):
    VALID_QUERY_PARAMS = ["observation_name"]
    utils = Utils()

    def get(self, request):
        params = request.query_params.dict()

        kwargs = {key: value for key, value in params.items() if key in self.VALID_QUERY_PARAMS}

        queryset_observations = Observation.objects.filter(**kwargs)

        if params.get("aggregator") == "mean":
            if not kwargs.get("observation_name"):
                error = {"error_description": "The field observation_name is required for this operation"}
                serializer_error = ErrorSerializer(data=error)
                if serializer_error.is_valid():
                    return Response(serializer_error.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            output_list = self.get_mean_dict(queryset_observations)
            serializer = AggregationSerializer(data=output_list, many=True)
        else:
            observation_list = [observation._data for observation in queryset_observations]
            observation_list_with_components = self.utils.get_linked_components(observation_list=observation_list)
            serializer = ObservationSerializer(data=observation_list_with_components, many=True)

        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # This method will return the output in dict format
    def get_mean_dict(self, queryset_observations):
        observation_list = [observation._data for observation in queryset_observations]
        observation_list_with_components = self.utils.get_linked_components(observation_list=observation_list)

        mean_dict = {}
        for observation in observation_list_with_components:
            if (components := observation.get("components", None)) is not None:
                for component in components:
                    value = float(component.get("value"))
                    mean_dict.setdefault(component.get("observation_name"), {}).setdefault(component.get(
                        "value_unit"), []).append(value)
            else:
                value = float(observation.get("value"))
                mean_dict.setdefault(observation.get("observation_name"), {}).setdefault(observation.get(
                    "value_units"), []).append(value)

        output_list = []
        for observation_name, observation in mean_dict.items():
            for unit, value_list in observation.items():
                mean = sum(value_list) / len(value_list)

                output_dict = {"aggregator": "mean",
                               "observation_name": observation_name,
                               "value_unit": unit,
                               "value": str(mean)}

                output_list.append(output_dict)
        return output_list

    def post(self, request):
        data_received = Utils.delete_null_empty_from_dict(request.data)
        data_received["issued"] = parse(data_received["issued"])
        observation_id = bson.objectid.ObjectId()
        data_received.setdefault("_id", str(observation_id))
        serializer = ObservationSerializer(data=data_received)
        if serializer.is_valid():
            components = data_received.get("components", None)
            if components:
                data_received.pop("components")
                for component_dict in components:
                    component_dict.setdefault("observation_parent", observation_id)
                    component = Component(**component_dict)
                    component.save()

            observation_model = Observation(**data_received)
            observation_model.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)
