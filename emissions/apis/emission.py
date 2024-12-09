from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
import csv
import os
from datetime import datetime, timedelta
from django.core.cache import cache
import json


class EmissionView(APIView):
    class QueryParamSerializer(serializers.Serializer):
        start_date = serializers.DateField(input_formats=["%d-%m-%Y"])
        end_date = serializers.DateField(input_formats=["%d-%m-%Y"])
        business_facilities = serializers.ListField(
            child=serializers.CharField(), required=True
        )

    def get_granular_cache_key(self, date, facility):
        return f"{date}:{facility}"

    def get_range_cache_key(self, start_date, end_date, business_facilities):
        return f"{start_date}:{end_date}:{','.join(sorted(business_facilities))}"

    def get(self, request):
        # Validate the query parameters
        serializer = self.QueryParamSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(
                content_type="application/json",
                status=HTTP_400_BAD_REQUEST,
                data={"errors": serializer.errors},
            )

        validated_data = serializer.validated_data
        start_date = validated_data["start_date"]
        end_date = validated_data["end_date"]
        business_facilities = validated_data["business_facilities"]

        # Check range-level cache
        range_cache_key = self.get_range_cache_key(start_date, end_date, business_facilities)
        cached_range_data = cache.get(range_cache_key)
        if cached_range_data:
            return Response(
                data=json.loads(cached_range_data),
                status=HTTP_200_OK,
                content_type="application/json",
            )

        # Initialize result and missing data tracker
        total_emission_per_facility = {facility: 0 for facility in business_facilities}
        missing_data = {}

        # Check granular cache for each date and facility
        current_date = start_date
        while current_date <= end_date:
            for facility in business_facilities:
                granular_cache_key = self.get_granular_cache_key(current_date.isoformat(), facility)
                cached_value = cache.get(granular_cache_key)
                if cached_value is not None:
                    total_emission_per_facility[facility] += cached_value
                else:
                    if current_date not in missing_data:
                        missing_data[current_date] = []
                    missing_data[current_date].append(facility)
            current_date += timedelta(days=1)

        # If no data is missing, return from cache
        if not missing_data:
            cache.set(range_cache_key, json.dumps(total_emission_per_facility), timeout=3600)
            return Response(
                data=total_emission_per_facility,
                status=HTTP_200_OK,
                content_type="application/json",
            )

        # Read and process CSV for missing data
        csv_path = os.path.join(os.getcwd(), "emissions_data.csv")
        try:
            with open(csv_path, mode="r") as csvfile:
                csv_reader = csv.DictReader(csvfile)
                next(csv_reader)  # Skip the header row
                for row in csv_reader:
                    transaction_date = datetime.strptime(row["TRANSACTION DATE"], "%d-%m-%Y").date()
                    facility = row["Business Facility"]
                    co2_item = float(row["CO2_ITEM"]) if row["CO2_ITEM"].strip() else 0

                    if transaction_date in missing_data and facility in missing_data[transaction_date]:
                        total_emission_per_facility[facility] += co2_item

                        # Cache the processed data
                        granular_cache_key = self.get_granular_cache_key(transaction_date.isoformat(), facility)
                        cache.set(granular_cache_key, co2_item, timeout=3600)

        except FileNotFoundError:
            return Response(
                data={"error": "CSV file not found."},
                status=HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(data={"error": str(e)}, status=HTTP_400_BAD_REQUEST)

        # Update range-level cache
        cache.set(range_cache_key, json.dumps(total_emission_per_facility), timeout=3600)

        return Response(
            data=total_emission_per_facility,
            status=HTTP_200_OK,
            content_type="application/json",
        )
