from flask import Flask, render_template, request, redirect, url_for
from digital_twin_service import DigitalTwin
import asyncio

app = Flask(__name__)
digital_twin = DigitalTwin()

@app.route('/')
def index():
    """Homepage"""
    return render_template('index.html')

@app.route('/scan', methods=['GET'])
def scan_devices():
    """Scan for devices"""
    devices = asyncio.run(digital_twin.scan_devices())
    return render_template('devices.html', devices=devices)

@app.route('/connect', methods=['POST'])
def connect_device():
    """Connect to a device"""
    address = request.form['device_address']
    connected = asyncio.run(digital_twin.connect_device(address))
    if connected:
        return redirect(url_for('monitoring'))
    return render_template('devices.html', error="Failed to connect to the device.")

@app.route('/monitor', methods=['GET'])
def monitoring():
    """Monitor device data"""
    data = asyncio.run(digital_twin.get_monitoring_data(10))  # Monitor for 10 seconds
    if data:
        return render_template(
            'monitoring.html', 
            stats=data['data']['statistics'], 
            alerts=data['data']['alerts']
        )
    # Just render the page without an error message
    return render_template('monitoring.html')  

if __name__ == '__main__':
    app.run(debug=True)