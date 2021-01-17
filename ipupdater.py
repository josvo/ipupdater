#!/usr/bin/env python3
from ns1 import Config
from ns1 import NS1
from requests import get, exceptions
from time import time, sleep
from ipaddress import ip_address
import logging
import os

# ---------------------------------------------------------------------
# All variables can be set via ENV variables or they use the standard value in case
# there is no ENV variable found

# Pass a list of records
# e.g. RECORDS="example.net;test.example.net"
resource_records = os.getenv('RECORDS', "www.example.com;test.example.com").split(';')

# Wait query_frequency seconds before doing a new query; defaults to 10 s
query_frequency = os.getenv("QUERY_FREQUENCY", 10)

# Update NS1 IP address every ns1_update_frequency seconds
ns1_update_frequency = os.getenv("UPDATE_FREQUENCY", 600)

# See https://www.ipify.org/
ipify_url = "https://api.ipify.org"

# Either pass an environment variable with your API Key or create a config file
ns1_apikey = os.getenv("NS1_APIKEY", "")
ns1_config = "/etc/ns1/config.json"

# Set log level (one of DEBUG, INFO, WARNING, ERROR, CRITICAL)
loglevel = os.getenv("LOGLEVEL", "INFO")
# ---------------------------------------------------------------------


def check_ip_address(ip, ip_type):
    try:
        ip_address(ip)
        logging.debug("{} IP address is valid: {}.".format(ip_type, ip))
        return True
    except ValueError:
        logging.error('{} IP address invalid: {}.'.format(ip_type, ip))
    except Exception as e:
        logging.critical('{} IP: An unknown error in check_ip_address has occurred, {} {}'.format(ip_type, ip, e))
    return False


def get_ns1_ip(myapi, rr):
    # Just choose the first A record as current IP
    logging.debug("Updating IP address from NS1")
    rec = myapi.loadRecord(rr[0], "A")
    return rec.data["answers"][0]["answer"][0]


def set_ns1_ip(my_api, rr, dyn_ip):
    logging.debug("Writing ip address {} to {}".format(dyn_ip, rr))
    rec = my_api.loadRecord(rr, "A")
    rec.update(answers=[dyn_ip])


def get_dynamic_ip(url):
    logging.debug("Get dynamic ip address")
    try:
        return get(url).text
    except exceptions.Timeout:
        logging.warning("Timeout when calling {}".format(ipify_url))
    except exceptions.TooManyRedirects:
        logging.error("Bad URL {}".format(ipify_url))
    except exceptions.ConnectionError:
        logging.error("Error connecting to {}".format(ipify_url))
    except exceptions.RequestException as e:
        logging.critical("An unexpected error occured when calling {}: {}".format(ipify_url, e))
    return ""


logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=os.environ.get("LOGLEVEL", loglevel),
    datefmt='%Y-%m-%d %H:%M:%S')
logging.info("Starting up ipudater")
start_time = time()

config = Config()
if ns1_apikey:
    config.createFromAPIKey(ns1_apikey)
    api = NS1(config=config)
else:
    api = NS1(configFile=ns1_config)


ns1_ip = get_ns1_ip(api, resource_records)

while True:
    logging.debug("Starting next iteration")
    dynamic_ip = get_dynamic_ip(ipify_url)

    if check_ip_address(dynamic_ip, "Dynamic") and check_ip_address(ns1_ip, "NS1"):
        now_time = time()
        elapsed = now_time - start_time
        if elapsed >= ns1_update_frequency:
            logging.debug("Get actual NS1 IP address.")
            ns1_ip = get_ns1_ip(api, resource_records)
            start_time = time()

        if ns1_ip == dynamic_ip:
            logging.debug("Dynamic IP ({}) and NS1 IP ({}) are identical.".format(dynamic_ip, ns1_ip))
        else:
            logging.info("Dynamic IP ({}) differs from NS1 IP ({}).".format(dynamic_ip, ns1_ip))
            for r in resource_records:
                logging.info("Updating {} ".format(r))
                set_ns1_ip(api, r, dynamic_ip)
            # Put an extra sleep here to make sure the resource records are up to date...
            sleep(query_frequency)
            # And get the actual ip address back
            ns1_ip = get_ns1_ip(api, resource_records)
            start_time = time()

    else:
        logging.error("Invalid ip address: trying again in {}s".format(query_frequency))

    sleep(query_frequency)
