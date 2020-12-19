#!/usr/bin/env python
# -*- coding: utf-8 -*-

from influxdb import InfluxDBClient
from ruuvitag_sensor.ruuvi import RuuviTagSensor


# InfluxDB client
client = InfluxDBClient(host='localhost', port=8086, database='ruuvidata')


# All tags in range (name, mac)
tags = [
    ("tag1", "**:**:**:**:**:**"),
    ("tag2", "**:**:**:**:**:**")
]


# Params
timeout_in_sec = 4  # Timeout for search


# Class for tags
class RuuviTag:

    def __init__(self, mac, name):
        self._mac = mac
        self._name = name

    def get_data(self):
        data = RuuviTagSensor.get_data_for_sensors([self._mac], timeout_in_sec)
        return data[self._mac]


# Main
def main():
    # Iterate all tags
    for tag in tags:
        tag_name = tag[0]
        tag_mac = tag[1]
        current_tag = RuuviTag(tag_mac, tag_name)

        try:
            data = current_tag.get_data()
        except Exception:
            continue

        # Used in json -> influx db
        fields = {
            'temperature': data['temperature'] if ('temperature' in data) else None,
            'humidity': data['humidity'] if ('humidity' in data) else None,
            'pressure': data['pressure'] if ('pressure' in data) else None,
            'acceleration': data['acceleration'] if ('acceleration' in data) else None,
            'accelerationX': data['acceleration_x'] if ('acceleration_x' in data) else None,
            'accelerationY': data['acceleration_y'] if ('acceleration_y' in data) else None,
            'accelerationZ': data['acceleration_z'] if ('acceleration_z' in data) else None,
            'batteryVoltage': data['battery'] / 1000.0 if ('battery' in data) else None
        }

        # Create JSON based on influx db setup
        json_body = [
            {
                "measurement": "Ruuvitags",
                "tags": {
                    "room": tag_name,
                    "sensor": tag_mac
                },
                "fields": fields
            }
        ]

        client.write_points(json_body)


if __name__ == '__main__':
    main()
