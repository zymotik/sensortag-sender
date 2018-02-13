import mqtt
import config

global mqtt_conn

mqtt_conn = mqtt.connect_mqtt(config.mqtt_ipaddress, config.mqtt_port, config.mqtt_username, config.mqtt_password)

mqtt.publish_temp(mqtt_conn, 123123, 12.3)

mqtt.disconnect_mqtt(mqtt_conn)