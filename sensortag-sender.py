from multiprocessing.dummy import Pool as ThreadPool 
from sensortag import SensorTagManager
import sched, time, json, requests, os, sys
import mqtt
import config

mqtt_conn = None
s = sched.scheduler(time.time, time.sleep)
pool = ThreadPool(config.sensors.__len__())
data = {'sensors' : {} }

def main():
	print(time.strftime("%H:%M") + " SensorTagSender started.")
	if config.mqtt_enabled:
		global mqtt_conn
		mqtt_conn = mqtt.connect_mqtt(config.mqtt_ipaddress, config.mqtt_port, config.mqtt_username, config.mqtt_password)
	results = pool.map(start, config.sensors)

def start(address):
	if address == "logger":
		s.enter(config.poll_period_seconds, 1, publish_temp_readings, (s,))
		s.run()
	else:
		SensorTagManager(address, data)
		print address
	    
def publish_temp_readings(sc):
	clear_screen()
	readings = []
	for sensorId in data['sensors']:
		has_data = False
		reading = {'sensorId': data['sensors'][sensorId]['id']}
		
		try:
			reading['ambientTemperature'] = data['sensors'][sensorId]['ambientTemperature']
			del data['sensors'][sensorId]['ambientTemperature']
			has_data = True
		except:
			pass
			
		try:
			reading['humidity'] = data['sensors'][sensorId]['humidity']
			del data['sensors'][sensorId]['humidity']
			has_data = True
		except:
			pass

		if has_data:
			readings.append(reading)
			if config.mqtt_enabled:
				mqtt.publish_temp(mqtt_conn, reading['sensorId'], reading['ambientTemperature'])

	if len(readings) > 0 and config.http_enabled:
		send_to_server(list_to_json(readings))
		
	if len(readings) == 0:
		print(time.strftime("%H:%M") + " No sensors found.")
	
	s.enter(config.poll_period_seconds, 1, publish_temp_readings, (sc,))


def list_to_json(list_obj):
	return json.dumps(list_obj)

def send_to_server(data_string):
	try:
		r = requests.post(config.http_url, data=data_string, headers=config.http_headers)
		print(data_string)
		print(time.strftime("%H:%M") + " Sent.")
	except:
		clear_screen()
		print(sys.exc_info()[0])
		print(time.strftime("%H:%M") + " Exception sending data.")
		pass
	
def clear_screen():
	os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    main()
