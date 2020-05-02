# ipupdater
This program behaves like a DynDNS service for your own domain. It checks if your (dynamic) 
IP has changed and updates it as soon as differs from the set ip. 
https://api.ipify.org is used for getting your actual (dynamic) ip address. 
Check out their resources to learn more
 
## Installation
You have to install some python libraries
- ns1-python
- logging (likely installed by default)
- requests (likely installed by default)

To make this program run:
- get a (free) account for NS1 DNS service (https://ns1.com/)
- create an API key
- copy config.json to /etc/ns1/config.json
- replace the API key in config.json 
```json
...
"key": "---putYourKeyhere---",
...
```
- copy ipupdater.py to /usr/sbin/ipupdater.py
- replace the resource records in ipupdater.py
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

In case of problems, try to increase the log level. 
