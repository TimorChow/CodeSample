"""
Last Updated:
    03/29/2021
Description:
    Controller/Interface between hardware and database
"""
import datetime
import os
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from .ConnectPool import Connector

url = os.getenv("INFLUX_URL")
org = os.getenv("INFLUX_ORG")
bucket = os.getenv("INFLUX_BUCKET")
token = os.getenv("INFLUX_TOKEN")

"""
Database Table Name
"""
MINER_MINER = 'miners_miner'
MINER_LOG = 'miners_log'

SENSOR_LOG = 'sensor_log'
SENSOR_SENSOR = 'sensor_sensor'


class Operator(object):
    """
    A base operator provides basic data fetching function
    """

    @staticmethod
    def get_setting(name):
        querystring = "SELECT `value`,`dataType` FROM setting_setting WHERE name='{name}'".format(name=name)
        with Connector() as connector:
            return connector.get_one(querystring)

    def get_voltage(self) -> int:
        return int(self.get_setting('voltage')[0])


class MinerOperator(Operator):
    """
    Design for Channel Object, provides all method to interact with database
    """

    @staticmethod
    def upload_log(miner_id, value):
        with InfluxDBClient(url=url, token=token) as client:
            write_api = client.write_api(write_options=SYNCHRONOUS)
            data = "ct,id={miner_id} value={value}".format(miner_id=miner_id, value=value)
            write_api.write(bucket, org, data)

    @staticmethod
    def read_consumption(miner_id) -> int:
        """
        Read curCons of a Miner
        """
        with InfluxDBClient(url=url, token=token) as client:
            query = 'from(bucket: "Hardware")' \
                    '|> range(start: -1m)' \
                    '|> filter(fn: (r) => r._measurement == "ct")' \
                    '|> filter(fn: (r) => r["id"] == "{}") |> last() '.format(miner_id)

            tables = client.query_api().query(query, org=org)
            for t in tables:
                for c in t.records:
                    return (int(c['_value']))

    @staticmethod
    def get_status_list():
        querystring = "SELECT status FROM {table}".format(table=MINER_MINER)
        with Connector() as connector:
            return connector.get_all(querystring)

    @staticmethod
    def set_miner(miner_id, name, value) -> int:
        """
        turned off: set_miner(9, 'status', 1)
        """
        querystring = "UPDATE {table} SET {name}={value} WHERE id={id}".format(
            table=MINER_MINER, name=name, value=value, id=miner_id)
        with Connector() as connector:
            return connector.update(querystring)


class SensorOperator(Operator):
    @staticmethod
    def upload_log(name, value):
        with InfluxDBClient(url=url, token=token) as client:
            write_api = client.write_api(write_options=SYNCHRONOUS)
            data = "sensor,name={name} value={value}".format(name=name, value=value)
            write_api.write(bucket, org, data)
