# ipupdater
This program behaves like a DynDNS service for your own domain. It checks if your (dynamic) 
IP has changed and updates it as soon as differs from the set ip. 
https://api.ipify.org is used for getting your actual (dynamic) ip address. 
Check out their resources to learn more
 
## Installation

- get a (free) account for NS1 DNS service (https://ns1.com/)
- create an API key
- Either copy config.json to /etc/ns1/config.json or use an environmental variable (see below)
- replace the API key in config.json 
```json
...
"key": "---putYourKeyhere---",
...
```


### Docker

To run it with minimal settings, use:
```shell script
docker build -t ipupdater .
docker run -d -e RECORDS="www.example.com;vpn.example.com" -e NS1_APIKEY="--NS1APKEY---" ipupdater
```

Possible env variables:

| ENV variable | Description | DEFAULT | Mandatory |
|---|---|---|---|
| RECORDS | All resource records you want to have updated | "www.example.com;example.com" | Yes |
| QUERY_FREQUENCY | How long to wait before calling the API again and doing a fresh check (in seconds) | 10| No |
| UPDATE_FREQUENCY | Update the IP address that is currently set in NS1 every so seconds | 600 | No |
| NS1_APIKEY | Pass your API Key via this env variable. The env variable has precedence over an existing conf file. | "" | Yes for Docker; for daemon install you can use a config file as well |
| LOGLEVEL | One of DEBUG, INFO, WARNING, ERROR, CRITICAL | INFO| No |


### Run it as daemon with systemd
You have to install some python libraries
- ns1-python
- logging (likely installed by default)
- requests (likely installed by default)

To make this program run:
- copy ipupdater.py to /usr/sbin/ipupdater.py
- make ipudater.py executable
```bash
chmod +x /usr/sbin/ipupdater.py
```
- replace the resource records in ipupdater.py (or use an environtmental variable)
```python
resource_records = ["example.net", "www.example.net"]
```
- make sure the resource record exist on NS1
- copy the ipudater.service file to /etc/systemd/system/ipudater.service
- Reload the systemd-daemon
```
systemctl daemon-reload
```
- start and enable ipupdater
```
systemctl start ipupdater
systemctl enable ipupdater
```
- You can see log entries with journalctl, as soon as the program runs.

In case of problems, try to increase the log level to find out where the error occurs.
