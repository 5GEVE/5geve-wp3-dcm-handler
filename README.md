# 5geve-wp3-dcm-handler script

This repository contains the logic needed for providing a REST API to the Data Collection Manager, in order to handle automatically the life cycle of this component (related to topic subscription/withdrawal and publish operations).

Usage: `sudo python3 dcm_rest_client.py [--dcm_ip_address <dcm_ip_address>] [--port <port_number>] [--spanish_site_plugin_ip_port <spanish_site_plugin_ip_port>] [--italian_site_plugin_ip_port <italian_site_plugin_ip_port>] [--french_site_plugin_ip_port <french_site_plugin_ip_port>] [--greek_site_plugin_ip_port <greek_site_plugin_ip_port>] [--log <log_level>]`

Default DCM IP address is localhost, default port is 8090, default site brokers IP-ports are default:8090, and default log level is info.

## Application API

The REST API provided by the `dcm_rest_client.py` script can be seen in the corresponding api-docs files in this repository.

## Steps to be followed

First of all, install Python 3 in the server which will hold this script.

```shell
sudo apt install python3-pip
```

Then, export some variables related to the language.

```shell
export LC_ALL="en_US.UTF-8"
export LC_CTYPE="en_US.UTF-8"
sudo dpkg-reconfigure locales
```

After this, install the required packages for this Python script, which can be found in the requirements.txt file.

```shell
pip3 install -r requirements.txt
```

Finally, execute the script.

```shell
sudo python3 dcm_rest_client.py --dcm_ip_address localhost --port 8090 --spanish_site_plugin_ip_port localhost:8090 --italian_site_plugin_ip_port localhost:8090 --french_site_plugin_ip_port localhost:8090 --greek_site_plugin_ip_port localhost:8090 --log info
```

## Copyright

This work has been done by Telcaria Ideas S.L. for the 5G EVE European project under the [Apache 2.0 License](LICENSE).
