import datetime
import logging

import requests

from src.models import Reservation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class HospitableAPI:
    def __init__(self, token):
        self.bearer_token = token
        self.base_api_url = "https://public.api.hospitable.com/v2"
        self.url_properties = f"{self.base_api_url}/properties"
        self.url_reservation = f"{self.base_api_url}/reservations"

    def create_headers(self):
        return {
            "accept": "application/json",
            "Content-Type": "application/json",
            "authorization": f"Bearer {self.bearer_token}"
        }

    async def sync_reservations(self):
        properties = self.get_all_properties()
        for property in properties:
            reservations = self.get_reservations(property.get("id"))
            for reservation in reservations:
                reservation_id = reservation.get("id")
                reservation_obj = Reservation(**reservation)
                await reservation_obj.save()
        return True

    def get_complete_cleaning(self):
        properties = self.get_all_properties()
        for property in properties:
            reservations = self.get_reservations(property.get("id"))
            property["reservation"] = reservations
        schedule = self.generate_checkin_schedule(properties)
        html = self.generate_html_from_schedule(schedule=schedule)
        return html

    def get_all_properties(self):
        headers = self.create_headers()
        response = requests.get(self.url_properties, headers=headers, params={
                                'page': 1, 'per_page': 2})
        data = response.json()
        total_pages = data['meta']['last_page']
        all_properties = []

        for page in range(1, total_pages + 1):
            response = requests.get(self.url_properties, headers=headers, params={
                                    'page': page, 'per_page': 2})
            page_data = response.json()
            all_properties.extend(page_data['data'])

        return all_properties

    def get_reservations(self, property_id):
        start_date, end_date = self.get_dates()
        page = 1
        per_page = 10
        headers = self.create_headers()
        reservations = []

        while True:
            params = {
                'page': page,
                'per_page': per_page,
                'properties[]': property_id,
                'start_date': start_date,
                'end_date': end_date,
                'date_query': 'checkin'
            }
            response = requests.get(
                self.url_reservation, headers=headers, params=params)
            if response.status_code != 200:
                logger.debug(f"Error fetching data: {response.status_code}")
                break

            data = response.json()
            reservations.extend(data.get('data', []))

            if data.get('meta', {}).get('current_page') == data.get('meta', {}).get('last_page'):
                break

            page += 1

        return reservations

    def generate_checkin_schedule(self, data):
        """
        Generates a cleaning schedule based on the arrival date of accepted property reservations.

        Args:
        data (list): A list of property data, each with address and reservation details.

        Returns:
        dict: A dictionary with cleaning dates as keys, and a list of dictionaries containing address and next guest count as values.
        """
        checkin_schedule = {}

        for property in data:
            address = property["address"]["display"]
            reservations = [res for res in property.get("reservation", [])
                            if "cancel" not in res["status"]
                            and "void" not in res["status"]
                            and "denied" not in res["status"]
                            and "payment_request_sent" not in res["status"]
                            ]
            reservations.sort(key=lambda x: x["arrival_date"])

            for i, reservation in enumerate(reservations):
                # Set cleaning date as one day before the arrival date
                arrival_date = datetime.datetime.strptime(
                    reservation["arrival_date"], "%Y-%m-%dT%H:%M:%S%z").date()
                departure_date = datetime.datetime.strptime(
                    reservation["departure_date"], "%Y-%m-%dT%H:%M:%S%z").date()
                guests_count = reservation["guests"]["total"]
                status = reservation['status']

                # Format arrival_date and departure_date to only include the date part
                arrival_date_str = arrival_date.strftime('%Y-%m-%d')
                departure_date_str = departure_date.strftime('%Y-%m-%d')

                # Add arrival dates
                if arrival_date_str in checkin_schedule:
                    # If date already exists, append the property info to the list
                    checkin_schedule[arrival_date_str].append({
                        "address": address,
                        "guests_count": guests_count,
                        "departure_date": departure_date_str,
                        "status": status
                    })
                else:
                    # If date does not exist, create a new list with the property info
                    checkin_schedule[arrival_date_str] = [{
                        "address": address,
                        "guests_count": guests_count,
                        "departure_date": departure_date_str,
                        "status": status
                    }]

        return checkin_schedule

    def generate_html_from_schedule(self, schedule):
        current_date = datetime.datetime.now().date()
        html = "<html><body>"
        html += "<h1>Cleaning Schedule</h1>"
        html += "<table border='1'>"
        html += "<tr><th>Date</th><th>Address</th><th>Guests Count</th><th>Checkout Date</th><th>Booking Status</th></tr>"

        for date, properties in schedule.items():
            for details in properties:
                check_in_date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
                check_out_date = datetime.datetime.strptime(details['departure_date'], '%Y-%m-%d').date()
                row_color = " style='background-color: yellow;'" if check_in_date <= current_date <= check_out_date else ""
                html += f"<tr{row_color}><td>{date}</td><td>{details['address']}</td><td>{details['guests_count']}</td><td>{details['departure_date']}</td><td>{details['status']}</td></tr>"
            
        html += "</table>"
        html += "</body></html>"

        return html

    def get_dates(self):
        start_date = datetime.datetime.now() + datetime.timedelta(days=-30)
        end_date = datetime.datetime.now() + datetime.timedelta(days=30)
        return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')

