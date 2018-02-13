poll_period_seconds = 60
sensors = [ 'logger', 'BC:6A:29:AE:CB:AF' ]
features = { 'temperature': True, 'humidity': True }

#HTTP
http_enabled = True
http_url = ''
http_headers = { 'Content-Type': 'application/json' }

#MQTT
mqtt_enabled = True
mqtt_ipaddress = '192.168.0.5'
mqtt_port = 1883
mqtt_username = 'homeassistant'
mqtt_password = ''