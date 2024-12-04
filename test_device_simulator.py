import asyncio
import random
from datetime import datetime, timedelta
import logging
from twilio.rest import Client
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load Twilio credentials from environment variables
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock Bluetooth Device Class
class MockBluetoothDevice:
    def __init__(self, name="Test Fitness Band", address="00:11:22:33:44:55"):
        self.name = name
        self.address = address
        self.heart_rate = 70
        self.steps = 0
        self.calories = 0
        self.distance = 0.0
        self.sleep_duration = random.uniform(6, 8)  # Random sleep duration in hours
        self.is_connected = False
        self.start_time = None

    def simulate_heart_rate(self):
        variation = random.uniform(-5, 5)
        self.heart_rate = max(60, min(180, self.heart_rate + variation))
        return self.heart_rate

    def simulate_steps(self):
        new_steps = random.randint(10, 30)
        self.steps += new_steps
        self.distance += new_steps * 0.0008  # Assume average step length of 0.8 meters
        return self.steps

    def simulate_calories(self):
        self.calories += random.uniform(0.05, 0.15)  # Simulate calorie burn per second
        return self.calories

    def get_data(self):
        return {
            'heart_rate': round(self.simulate_heart_rate()),
            'steps': self.simulate_steps(),
            'calories': round(self.simulate_calories(), 2),
            'distance': round(self.distance, 2),
            'timestamp': datetime.now().isoformat()
        }

# Simulator Class
class TestDeviceSimulator:
    def __init__(self):
        self.devices = [
            MockBluetoothDevice("Mi Band 6", "12:34:56:78:90:AB"),
            MockBluetoothDevice("Fitbit Charge 5", "AB:CD:EF:12:34:56"),
            MockBluetoothDevice("Apple Watch", "98:76:54:32:10:EF")
        ]
        self.connected_device = None

    async def scan_devices(self):
        await asyncio.sleep(2)
        return [{"name": d.name, "address": d.address} for d in self.devices]

    async def connect_device(self, address):
        await asyncio.sleep(1)
        device = next((d for d in self.devices if d.address == address), None)
        if device:
            device.is_connected = True
            device.start_time = datetime.now()
            self.connected_device = device
            return True
        return False

    async def get_monitoring_data(self, duration_seconds=10):
        if not self.connected_device:
            return None

        data_points = []
        current_time = self.connected_device.start_time or datetime.now()
        for _ in range(duration_seconds):
            data_point = self.connected_device.get_data()
            data_points.append(data_point)
            current_time += timedelta(seconds=1)
            await asyncio.sleep(0.1)

        heart_rates = [d['heart_rate'] for d in data_points]
        steps = max([d['steps'] for d in data_points])
        calories = max([d['calories'] for d in data_points])
        distance = max([d['distance'] for d in data_points])
        avg_hr = sum(heart_rates) / len(heart_rates)

        return {
            'status': 'success',
            'data': {
                'raw_data': data_points,
                'statistics': {
                    'avg_heart_rate': avg_hr,
                    'max_heart_rate': max(heart_rates),
                    'total_steps': steps,
                    'calories_burned': calories,
                    'distance_traveled_km': round(distance / 1000, 2),
                    'activity_duration': duration_seconds / 60,
                    'sleep_duration_hours': self.connected_device.sleep_duration
                },
                'alerts': self._generate_alerts(heart_rates)
 }
        }

    def _generate_alerts(self, heart_rates):
        alerts = []
        avg_hr = sum(heart_rates) / len(heart_rates)
        hr_std = (sum((x - avg_hr) ** 2 for x in heart_rates) / len(heart_rates)) ** 0.5

        for hr in heart_rates:
            if abs(hr - avg_hr) > 2 * hr_std:
                alert_message = f'Unusual heart rate detected: {hr} BPM'
                alerts.append({
                    'type': 'anomaly',
                    'message': alert_message,
                    'value': hr,
                    'timestamp': datetime.now().isoformat()
                })
                # Send alert to investigator
                self.send_alert('+919022381018', alert_message)

        return alerts

    def send_alert(self, phone_number, message):
        """Send an alert message to the specified phone number using Twilio."""
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        try:
            client.messages.create(
                body=message,
                from_=TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            logger.info(f'Alert sent to {phone_number}: {message}')
        except Exception as e:
            logger.error(f'Failed to send alert: {e}')

simulator = TestDeviceSimulator()