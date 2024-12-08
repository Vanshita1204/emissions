from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
import csv
import os
from datetime import datetime

class EmissionView(APIView):
    class QueryParamSerializer(serializers.Serializer):
        start_date = serializers.DateField(input_formats=['%d-%m-%Y',])
        end_date = serializers.DateField(input_formats=['%d-%m-%Y'])
        business_facilities = serializers.ListField(
            child=serializers.CharField(),
            required=True
        )

    def get(self, request):
        # Decode and preprocess `business_facilities`
        query_params = request.query_params.copy()
        
        # Validate the query parameters
        serializer = self.QueryParamSerializer(data=query_params)
        if not serializer.is_valid():
            return Response(
                content_type="application/json",
                status=HTTP_400_BAD_REQUEST,
                data={"errors": serializer.errors},
            )
        validated_data = serializer.validated_data

        # Read and process the CSV file
        csv_path = os.path.join(os.getcwd(), "emissions_data.csv")
        data = {}

        try:
            with open(csv_path, mode='r') as csvfile:
                csv_reader = csv.DictReader(csvfile, fieldnames=[
                    '', 'TRANSACTION DATE', 'SUPPLIER NAME', 'ITEM DESCRIPTION',
                    'ITEM PRICE/UNIT', 'TRANSACTION AMOUNT', 'TRANSACTION CURRENCY',
                    'TRANSACTION ID', 'Business Facility', 'SUPPLIER COUNTRY', 'SPEND-CAT',
                    'UNIT_PRICE', 'UNITS', 'CO2_ITEM', 'EF_ITEM', 'CALC-TYPE', 'MAX-MATCH',
                    'DISTANCE', 'TRANS_TYPE', 'EF_TRANS', 'CO2_PGS', 'CO2_GOODS', 'CO2_NRG',
                    'CO2_U_TRANS', 'CO2_WASTE', 'CO2_BUSINESS', 'CO2_EMPLOY', 'CO2_U_LEASE',
                    'CO2_D_TRANS', 'CO2_PROCESS_SOLD', 'CO2_USE_SOLD', 'CO2_END_LIFE',
                    'CO2_D_LEASE', 'CO2_FRANCHISE', 'CO2_INVEST', 'SCOPE'
                ])
                next(csv_reader)  # Skip the header row

                for row in csv_reader:
                    transaction_date = datetime.strptime(row['TRANSACTION DATE'], "%d-%m-%Y").date()
                    business_facility = row['Business Facility']
                    co2_item = float(row['CO2_ITEM']) if row['CO2_ITEM'] and row['CO2_ITEM'].strip() else 0
                    
                    key = (transaction_date, business_facility)
                    data[key] = data.get(key, 0) + co2_item

            # Filter and aggregate emissions
            total_emission_per_facility = {}
            for (transaction_date, business_facility), co2_total in data.items():
                if (
                    validated_data['start_date'] <= transaction_date <= validated_data['end_date'] and
                    business_facility in validated_data['business_facilities']
                ):
                    total_emission_per_facility[business_facility] = total_emission_per_facility.get(business_facility, 0) + co2_total

            return Response(data=total_emission_per_facility, status=HTTP_200_OK, content_type="application/json")

        except FileNotFoundError:
            return Response(data={"error": "CSV file not found."}, status=HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(data={"error": str(e)}, status=HTTP_400_BAD_REQUEST)
