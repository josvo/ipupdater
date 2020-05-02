from ns1 import Config
from ns1 import NS1
from requests import get, exceptions
from time import time, sleep
from ipaddress import ip_address
import logging

# ---------------------------------------------------------------------
# All these resource records will be updated
resource_records = ["example.net", "www.example.net"]

# Wait sleep_time seconds before doing a new query of the dynamic ip
sleep_time = 10

# Update NS1 IP Address every ns1_update_frequency seconds
ns1_update_frequency = 600

# See https://www.ipify.org/
ipify_url = "https://api.ipify.org"

# Path to the NS1 config file
ns1_config = "/etc/ns1/config.json"

# Set log level (one of DEBUG, INFO, WARNING, ERROR, CRITICAL)
loglevel = logging.INFO
# ---------------------------------------------------------------------


def check_ip_address(ip, ip_type):
    try:
        ip_address(ip)
        logging.debug("{} IP address is valid: {}.".format(ip_type, ip))
        return True
    except ValueError:
        logging.error('{} IP address invalid: {}.'.format(ip_type, ip))
    except Exception as e:
        logging.critical('{} IP: An unknown error in check_ip_address has occured, {} {}'.format(ip_type, ip, e))
    return False


def get_ns1_ip(myapi, rr):
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


logging.basicConfig(format='%(levelname)s:%(message)s', level=loglevel)
logging.info("Starting up ipudater")
start_time = time()

config = Config()
api = NS1(configFile=ns1_config)

ns1_ip = get_ns1_ip(api, resource_records)

while True:
    logging.debug("Starting next iteration")
    dynamic_ip = get_dynamic_ip(ipify_url)

    if check_ip_address(dynamic_ip, "Dynamic") and check_ip_address(ns1_ip, "NS1"):
        now_time = time()
        elapsed = now_time - start_time
        if elapsed >= ns1_update_frequency:
            logging.info("Get actual NS1 IP address.")
            ns1_ip = get_ns1_ip(api, resource_records)
            start_time = time()

        if ns1_ip == dynamic_ip:
            logging.info("Dynamic IP ({}) and NS1 IP ({}) are identical.".format(dynamic_ip, ns1_ip))
        else:
            logging.info("Dynamic IP ({}) differs from NS1 IP ({}).".format(dynamic_ip, ns1_ip))
            for r in resource_records:
                logging.info("Updating {} ".format(r))
                set_ns1_ip(api, r, dynamic_ip)
            # Put an extra sleep here to make sure the resource records are up to date...
            sleep(sleep_time)
            # And get the actual ip address back
            ns1_ip = get_ns1_ip(api, resource_records)
            start_time = time()

    else:
        logging.error("Invalid ip address: trying again in {}s".format(sleep_time))

    sleep(sleep_time)
