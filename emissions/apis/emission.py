from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
import csv

class EmissionView(APIView):
    class QueryParamSerializer(serializers.Serializer):
        start_date= serializers.DateField()
        end_date= serializers.DateField()
        buisness_facilities= serializers.ListField(child= serializers.CharField())

    def get(self,request):
        serializer= self.QueryParamSerializer(data=request.GET)
        if not serializer.is_valid():
            return Response(content_type="application/json",status=HTTP_400_BAD_REQUEST, data={"errors": serializer.errors})
        csv_reader = csv.DictReader()
        