# dcm-python script

This repository contains the logic needed for providing a REST API to the Data Collection Manager, in order to handle automatically the life cycle of this component (related to topic subscription/withdrawal and publish operations).

Usage: `sudo python3 dcm_rest_client.py [--dcm_ip_address <dcm_ip_address>] [--zookeeper_ip_address <zookeeper_ip_address>] [--kafka_port <kafka_port_number>] [--port <port_number>] [--log <log_level>]`

Default DCM and ZooKeeper IP addresses are localhost, default Kafka port is 9092, default listening port is 8090, and default log level is info.

Note that this version corresponds to the Dockerized environment of the Monitoring platform.

## Application API

The REST API provided by the `dcm_rest_client.py` script implements the following interface:

| Endpoint | Description | Input | Output |
| --- | --- | --- | --- |
| GET / | Check if this logic is running or not | - | 200 - OK |
| POST /dcm/subscribe | Subscribe to a given topic | It receives the following JSON chain in the request body: `{'expId': <exp_id>, 'topic': <topic_name>}` | 201 - accepted, 400 - error parsing request |
| DELETE /dcm/unsubscribe | Unsubscribe to a given topic | It receives the following JSON chain in the request body: `{'expId': <exp_id>, 'topic': <topic_name>}` | 201 - accepted, 400 - error parsing request |
| POST /dcm/publish/<topic> | Publish data in the topic <topic> | It receives the topic name, <topic>, in the URL. It receives the following JSON chain in the request body in the case of signalling topics: `{'records': [{'value': {'expId': <exp_id>, 'action': ['subscribe'\|'unsubscribe'], 'topic': <topic_name>}}, ...]}`. However, in case of requesting from a Data shipper, the format depends on the component that is publishing the data. | 201 - accepted, 400 - error parsing request |

(TODO - OpenAPI & new fields in messages received)

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
sudo python3 dcm_rest_client.py --dcm_ip_address localhost --zookeeer_ip_address localhost --kafka_port 9092 --port 8090 --log info
```

## Copyright

This work has been done by Telcaria Ideas S.L. for the 5G EVE European project under the [Apache 2.0 License](LICENSE).
