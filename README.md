
Emissions Project
A Django-based project that provides an API to compute and return total emissions data based on specified filters. This API processes emissions data from a CSV file and supports caching for efficient performance.

API Documentation
Endpoint
URL:
{host}/emissions/{query_string}

HTTP Method:
GET

Query Parameters:
start_date (required):
Format: dd-mm-yyyy
Description: Specifies the start date for filtering emission records.

end_date (required):
Format: dd-mm-yyyy
Description: Specifies the end date for filtering emission records.

business_facilities (required):
Format: A comma-separated list of facility names.
Description: Filters emissions data for the given business facilities.

Example Request
http
GET /emissions/?start_date=01-01-2020&end_date=31-12-2023&business_facilities=GreenEat%20Changi,GreenEat%20Marina%20Bay%20Financial%20Tower
Response
Returns the total emissions for the specified filters as a JSON object.

Example Response:

json
{
    "GreenEat Changi": 37970.58006212602,
    "GreenEat Marina Bay Financial Tower": 24830.78011232411
}
Features
Filter Emissions Data:

Supports filtering by date range (start_date and end_date).
Filters by one or more business facilities.
Caching for Performance:

Speeds up requests with the same or overlapping filters using an intelligent cache layer.
Reduces computational load on large datasets by reusing cached results for similar filters.
Scalable and Optimized:

Processes datasets with hundreds of thousands of rows efficiently.
Designed to handle increasing data volume while ensuring low latency.
Setup Instructions
Prerequisites
Python 3.8+
Django 4.0+
Emissions data CSV file (emissions_data.csv)
Installation
Clone the repository:

bash
git clone https://github.com/your-repo/emissions.git
cd emissions
Create and activate a virtual environment:

bash
python -m venv venv
source venv/bin/activate  # For Linux/Mac
venv\Scripts\activate     # For Windows
Install dependencies:

bash
pip install -r requirements.txt
Place the emissions_data.csv file in the project root directory.



bash
python manage.py runserver
