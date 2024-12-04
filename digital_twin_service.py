import asyncio
from test_device_simulator import simulator
import logging
from twilio.rest import Client
import os
from dotenv import load_dotenv
import random
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Load Twilio credentials from environment variables
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DigitalTwin:
    def __init__(self):
        self.simulator = simulator

    async def scan_devices(self):
        """Scan for available BLE devices."""
        try:
            devices = await self.simulator.scan_devices()
            logger.info(f"Found {len(devices)} devices")
            return devices
        except Exception as e:
            logger.error(f"Failed to scan devices: {str(e)}")
            return []

    async def connect_device(self, address):
        """Connect to a specific device by address."""
        try:
            connected = await self.simulator.connect_device(address)
            if connected:
                logger.info(f"Connected to device: {address}")
            return connected
        except Exception as e:
            logger.error(f"Failed to connect: {str(e)}")
            return False

    async def get_monitoring_data(self, duration_seconds=10):
        """Get monitoring data from the device."""
        try:
            data = await self.simulator.get_monitoring_data(duration_seconds)
            return data
        except Exception as e:
            logger.error(f"Error getting monitoring data: {str(e)}")
            return None

    def send_alert(self, to_phone_number, message):
        """Send an alert SMS to the specified phone number."""
        try:
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)  # Ensure the Twilio client is initialized
            message = client.messages.create(
                body=message,
                from_=TWILIO_PHONE_NUMBER,
                to=to_phone_number
            )
            logger.info(f"Alert sent: {message.sid}")
        except Exception as e:
            logger.error(f"Failed to send alert: {str(e)}")

    def _generate_alerts(self, heart_rates):
        alerts = []
        avg_hr = sum(heart_rates) / len(heart_rates)
        hr_std = (sum((x - avg_hr) ** 2 for x in heart_rates) / len(heart_rates)) ** 0.5

        for hr in heart_rates:
            # Randomly generate an alert 50% of the time
            if random.random() < 0.5:
                alert_message = f'Random alert triggered: {hr} BPM'
                alerts.append({
                    'type': 'random_alert',
                    'message': alert_message,
                    'value': hr,
                    'timestamp': datetime.now().isoformat()
                })
                # Send alert to investigator
                self.send_alert('+919022381018', alert_message)

        return alerts