import requests
import argparse
import logging
import coloredlogs
from flask import Flask, request, jsonify
from flask_swagger import swagger
from waitress import serve
import subprocess
from kafka import KafkaProducer
from kafka.errors import KafkaError
from kafka.future import log
import json

app = Flask(__name__)
logger = logging.getLogger("DCMRestClient")
kafka_port = "9092"
signalling_metric_infrastructure = "signalling.metric.infrastructure"
signalling_metric_application = "signalling.metric.application"
signalling_kpi = "signalling.kpi"

"""
The creation of MirrorMaker processes has been moved to dedicated systemd services.
This allows to check logs more easily, setup restart on failure.
We leave this code for future reference.
"""
# Start one MirrorMaker per each site, blacklisting signalling and)
# def start_mirror(site):
#     """
#     Opens a mirrormaker with a site in order to mirror metric topics.
#     Signalling and KPI topics are blacklisted with regex.
#     """
#     print("Start MirrorMaker for " + site);
#     subprocess.Popen(
#         [
#             "/bin/bash",
#             "/opt/kafka/bin/kafka-run-class.sh",
#             "kafka.tools.MirrorMaker",
#             "--consumer.config",
#             "/usr/bin/dcm/" + site + "_consumer.config",
#             "--num.streams",
#             "2",
#             "--producer.config",
#             "/usr/bin/dcm/producer.config",
#             "--whitelist",
#             "'^.*\.application_metric\..*$,^.*\.infrastructure_metric\..*$'",
#         ],
#         stdout=subprocess.PIPE,
#         stderr=subprocess.STDOUT,
#     )
# start_mirror("spanish")
# start_mirror("italian")
# start_mirror("french")
# start_mirror("greek")

@app.route('/', methods=['GET'])
def server_status():
    """
    Get status.
    ---
    describe: get status
    responses:
      200:
        description: OK
    """
    logger.info("GET /")
    return '', 200

@app.route("/spec", methods=['GET'])
def spec():
    """
    Get swagger specification.
    ---
    describe: get swagger specification
    responses:
      swagger:
        description: swagger specification
    """
    swag = swagger(app)
    swag['info']['version'] = "1.0"
    swag['info']['title'] = "DCM REST API"
    return jsonify(swag)

def create_kafka_topic(topic):
    logger.info("Creating topic %s in Kafka", topic)

    # TODO (if needed). 2 partitions minimum without key

    if "signalling." in topic:
        subprocess.call(['/bin/bash', '/opt/kafka/bin/kafka-topics.sh', '--create', '--zookeeper', dcm_ip_address+":2181", '--replication-factor', '1', '--partitions', '1', '--topic', topic])
    elif ".kpi." in topic:
        subprocess.call(['/bin/bash', '/opt/kafka/bin/kafka-topics.sh', '--create', '--zookeeper', dcm_ip_address+":2181", '--replication-factor', '1', '--partitions', '1', '--topic', topic])
    elif ".spain_" in topic:
        subprocess.call(['/bin/bash', '/opt/kafka/bin/kafka-topics.sh', '--create', '--zookeeper', dcm_ip_address+":2181", '--replication-factor', '1', '--partitions', '1', '--topic', topic])
        # Then, send the topic name to the corresponding broker
        logger.info("Sending topic %s to Spanish site", topic)
        r = requests.post(spanish_site_url + topic)
        logger.info("Response from Spanish site: Code %s", r)
        if r.status_code == 500:
            raise Exception("Topic %s not created in Spanish site", topic)
    elif ".italy_" in topic:
        subprocess.call(['/bin/bash', '/opt/kafka/bin/kafka-topics.sh', '--create', '--zookeeper', dcm_ip_address+":2181", '--replication-factor', '1', '--partitions', '1', '--topic', topic])
        # Then, send the topic name to the corresponding broker
        logger.info("Sending topic %s to Italian site", topic)
        r = requests.post(italian_site_url + topic)
        logger.info("Response from Italian site: Code %s", r)
        if r.status_code == 500:
            raise Exception("Topic %s not created in Italian site", topic)
    elif ".france_" in topic:
        subprocess.call(['/bin/bash', '/opt/kafka/bin/kafka-topics.sh', '--create', '--zookeeper', dcm_ip_address+":2181", '--replication-factor', '1', '--partitions', '1', '--topic', topic])
        # Then, send the topic name to the corresponding broker
        logger.info("Sending topic %s to French site", topic)
        r = requests.post(french_site_url + topic)
        logger.info("Response from French site: Code %s", r)
        if r.status_code == 500:
            raise Exception("Topic %s not created in French site", topic)
    elif ".greece_" in topic:
        subprocess.call(['/bin/bash', '/opt/kafka/bin/kafka-topics.sh', '--create', '--zookeeper', dcm_ip_address+":2181", '--replication-factor', '1', '--partitions', '1', '--topic', topic])
        # Then, send the topic name to the corresponding broker
        logger.info("Sending topic %s to Greek site", topic)
        r = requests.post(greek_site_url + topic)
        logger.info("Response from Greek site: Code %s", r)
        if r.status_code == 500:
            raise Exception("Topic %s not created in Greek site", topic)
    else:
        raise Exception("The topic %s has a bad format", topic)

@app.route('/dcm/subscribe', methods=['POST'])
def subscribe():
    """
    Subscribe to signalling topic.
    ---
    describe: subscribe to signalling topic
    parameters:
      - in: body
        name: signalling_topic_data
        schema:
          id: signalling_topic_data
          properties:
            expId:
              type: string
              description: expId set to 'internal'
            topic:
              type: string
              description: signalling topic name
    responses:
      201:
        description: accepted request
      400:
        description: error processing the request
    """
    logger.info("Request received - POST /dcm/subscribe")
    if not request.is_json:
        logger.warning("Format not valid")
        return 'Format not valid', 400
    try:
        # TODO (if needed). Check client-id and group-id. Group-id should ensure an unique consumer. If we have severeal consumers in a group, data can be shared and we don't want it.
        data = request.get_json()
        logger.info("Data received: %s", data)
        create_kafka_topic(data["topic"])
    except Exception as e:
        logger.error("Error while parsing request")
        logger.exception(e)
        return str(e), 400
    return '', 201

def delete_kafka_topic(topic):
    # Do not forget to set delete.topic.enable=true in config/server.properties.

    if "signalling." in topic:
        logger.info("Deleting topic %s in Kafka", topic)
        subprocess.call(['/bin/bash', '/opt/kafka/bin/kafka-topics.sh', '--delete', '--zookeeper', dcm_ip_address+":2181", '--topic', topic])
    elif ".kpi." in topic:
        logger.info("Deleting topic %s in Kafka", topic)
        subprocess.call(['/bin/bash', '/opt/kafka/bin/kafka-topics.sh', '--delete', '--zookeeper', dcm_ip_address+":2181", '--topic', topic])
    elif ".spain_" in topic:
        # Then, send the topic name to the corresponding broker
        logger.info("Sending topic %s to Spanish site", topic)
        r = requests.delete(spanish_site_url + topic)
        logger.info("Response from Spanish site: Code %s", r)
        if r.status_code == 200:
            # Finally, delete the topic
            logger.info("Deleting topic %s in Kafka", topic)
            subprocess.call(['/bin/bash', '/opt/kafka/bin/kafka-topics.sh', '--delete', '--zookeeper', dcm_ip_address+":2181", '--topic', topic])
        elif r.status_code == 500:
            raise Exception("Topic %s not deleted in Spanish site", topic)
    elif ".italy_" in topic:
        # Then, send the topic name to the corresponding broker
        logger.info("Sending topic %s to Italian site", topic)
        r = requests.delete(italian_site_url + topic)
        logger.info("Response from Italian site: Code %s", r)
        if r.status_code == 200:
            # Finally, delete the topic
            logger.info("Deleting topic %s in Kafka", topic)
            subprocess.call(['/bin/bash', '/opt/kafka/bin/kafka-topics.sh', '--delete', '--zookeeper', dcm_ip_address+":2181", '--topic', topic])
        elif r.status_code == 500:
            raise Exception("Topic %s not deleted in Italian site", topic)
    elif ".france_" in topic:
        # Then, send the topic name to the corresponding broker
        logger.info("Sending topic %s to French site", topic)
        r = requests.delete(french_site_url + topic)
        logger.info("Response from French site: Code %s", r)
        if r.status_code == 200:
            # Finally, delete the topic
            logger.info("Deleting topic %s in Kafka", topic)
            subprocess.call(['/bin/bash', '/opt/kafka/bin/kafka-topics.sh', '--delete', '--zookeeper', dcm_ip_address+":2181", '--topic', topic])
        elif r.status_code == 500:
            raise Exception("Topic %s not deleted in French site", topic)
    elif ".greece_" in topic:
        # Then, send the topic name to the corresponding broker
        logger.info("Sending topic %s to Greek site", topic)
        r = requests.delete(greek_site_url + topic)
        logger.info("Response from Greek site: Code %s", r)
        if r.status_code == 200:
            # Finally, delete the topic
            logger.info("Deleting topic %s in Kafka", topic)
            subprocess.call(['/bin/bash', '/opt/kafka/bin/kafka-topics.sh', '--delete', '--zookeeper', dcm_ip_address+":2181", '--topic', topic])
        elif r.status_code == 500:
            raise Exception("Topic %s not deleted in Greek site", topic)
    else:
        raise Exception("The topic %s has a bad format", topic)

@app.route('/dcm/unsubscribe', methods=['DELETE'])
def unsubscribe():
    """
    Unsubscribe to signalling topic.
    ---
    describe: unsubscribe to signalling topic
    parameters:
      - in: body
        name: signalling_topic_data
        schema:
          id: signalling_topic_data
          properties:
            expId:
              type: string
              description: expId set to 'internal'
            topic:
              type: string
              description: signalling topic name
    responses:
      201:
        description: accepted request
      400:
        description: error processing the request
    """
    logger.info("Request received - DELETE /dcm/unsubscribe")
    if not request.is_json:
        logger.warning("Format not valid")
        return 'Format not valid', 400
    try:
        data = request.get_json()
        logger.info("Data received: %s", data)
        delete_kafka_topic(data["topic"])
    except Exception as e:
        logger.error("Error while parsing request")
        logger.exception(e)
        return str(e), 400
    return '', 201

def publish_in_kafka(topic, data):
    logger.info("Publish data in Kafka topic %s", topic)
    # TODO (if needed). Key? No, do RR between partitions. If I use the same key, it uses the same partition.
    futures = producer.send(topic=topic, value=json.dumps(data))
    response = futures.get()
    logger.info("Response from Kafka: %s", response)

@app.route('/dcm/publish/<topic>', methods=['POST'])
def publish(topic):
    """
    Publish data in a topic.
    ---
    describe: publish data in a topic
    definitions:
      - schema:
          id: record
          properties:
            value:
                description: value included in the records list
                schema:
                    id: value
                    properties:
                        topic:
                         type: string
                         description: topic name
                        expId:
                         type: string
                         description: experiment ID
                        action:
                         type: string
                         description: either subscribe or unsubscribe
                        context:
                         description: additional information
                         schema:
                            id: context
                            properties:
                                metricId:
                                    type: string
                                    description: metric ID (if topic is related to a metric)
                                kpiId:
                                    type: string
                                    description: KPI ID (if topic is related to a KPI)
                                metricCollectionType:
                                    type: string
                                    description: metric collection type (if topic is related to a metric)
                                graph:
                                    type: string
                                    description: graph type (LIE, PIE, GAUGE) 
                                name:
                                    type: string
                                    description: metric name
                                unit:
                                    type: string
                                    description: metric unit
                                interval:
                                    type: string
                                    description: time interval to capture the metric
    parameters:
      - in: path
        name: topic
        type: string
        description: topic name
      - in: body
        name: records
        type: array
        description: records sent in the message
        items:
          $ref: "#/definitions/record"
    responses:
      201:
        description: accepted request
      400:
        description: error processing the request
    """
    logger.info("Request received - POST /dcm/publish/%s", topic)
    if not request.is_json:
        logger.warning("Format not valid")
        return 'Format not valid', 400
    try:
        logger.info("Data received in topic %s", topic)
        data = request.get_json()
        if "signalling" in topic:
            # Data received from a signalling topic, whose data model is well-known.
            records = data["records"]
            logger.info("Records raw list: %s", records)
            for value in records:
                
                if value["value"]["topic"].count('.') != 4 or value["value"]["topic"].count(' ') != 0 or value["value"]["topic"].count(',') != 0:
                    raise Exception("Incorrect format in topic name: %s", value["value"]["topic"])
                else:
                    logger.info("Value received: topic %s - expId %s - action %s - context %s", value["value"]["topic"], value["value"]["expId"], value["value"]["action"], value["value"]["context"])
                    
                    if value["value"]["action"] == "subscribe":

                        kafka_topic = value["value"]["topic"]

                        if subprocess.check_output(['/bin/bash', '/opt/kafka/bin/kafka-topics.sh', '--list', '--zookeeper', dcm_ip_address+":2181"]).decode("utf-8").find(kafka_topic) == -1:
                            
                            # Subscribe operation: create the Kafka topic.
                            # Notify subscribers from the corresponding signalling topic.
                            if "application" in topic and ".application_metric." in kafka_topic:
                                create_kafka_topic(kafka_topic)
                                publish_in_kafka(signalling_metric_application, value["value"])
                            elif "infrastructure" in topic and ".infrastructure_metric." in kafka_topic:
                                create_kafka_topic(kafka_topic)
                                publish_in_kafka(signalling_metric_infrastructure, value["value"])
                            elif "kpi" in topic and ".kpi." in kafka_topic:
                                create_kafka_topic(kafka_topic)
                                publish_in_kafka(signalling_kpi, value["value"])
                            else:
                                logger.warning("No data sent to Kafka")
                        else:
                            logger.warning("The topic %s already exists in Kafka", kafka_topic)
                    else:

                        kafka_topic = value["value"]["topic"]

                        if subprocess.check_output(['/bin/bash', '/opt/kafka/bin/kafka-topics.sh', '--list', '--zookeeper', dcm_ip_address+":2181"]).decode("utf-8").find(kafka_topic) != -1:

                            # Notify subscribers from the corresponding signalling topic.
                            # Unsubscribe operation: delete the Kafka topic.
                            if "application" in topic and ".application_metric." in kafka_topic:
                                publish_in_kafka(signalling_metric_application, value["value"])
                                delete_kafka_topic(kafka_topic)
                            elif "infrastructure" in topic and ".infrastructure_metric." in kafka_topic:
                                publish_in_kafka(signalling_metric_infrastructure, value["value"])
                                delete_kafka_topic(kafka_topic)
                            elif "kpi" in topic and ".kpi." in kafka_topic:
                                publish_in_kafka(signalling_kpi, value["value"])
                                delete_kafka_topic(kafka_topic)
                            else:
                                logger.warning("No data sent to Kafka")
                        else:
                            logger.warning("The topic %s does not exist in Kafka", kafka_topic)

        else:
            # Data received from another component (e.g. Data Shipper using the REST API). Just publish the JSON chain received.
            # In this case, it is supposed that topic has been already created in Kafka beforehand.
            # TODO (if needed). Review this publish operation.
            publish_in_kafka(topic, data)
    except Exception as e:
        logger.error("Error while parsing request")
        logger.exception(e)
        return str(e), 400
    return '', 201

def checkValidPort(value):
    ivalue = int(value)
    # RFC 793
    if ivalue < 0 or ivalue > 65535:
        raise argparse.ArgumentTypeError("%s is not a valid port" % value)
    return value

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dcm_ip_address",
        help='DCM IP address, default IP is localhost',
        default='localhost')
    parser.add_argument(
        "--port",
        type=checkValidPort,
        help='The port you want to use as an endpoint, default port is 8090',
        default="8090")
    parser.add_argument(
        "--spanish_site_plugin_ip_port",
        help='Spanish Kafka broker site plugin IP:port',
        default='localhost:8090')
    parser.add_argument(
        "--italian_site_plugin_ip_port",
        help='Italian Kafka broker site plugin IP:port',
        default='localhost:8090')
    parser.add_argument(
        "--french_site_plugin_ip_port",
        help='French Kafka broker site plugin IP:port',
        default='localhost:8090')
    parser.add_argument(
        "--greek_site_plugin_ip_port",
        help='Greek Kafka broker site plugin IP:port',
        default='localhost:8090')
    parser.add_argument(
        "--log",
        help='Sets the Log Level output, default level is "info"',
        choices=[
            "info",
            "debug",
            "error",
            "warning"],
        nargs='?',
        default='info')

    args = parser.parse_args()
    numeric_level = getattr(logging, str(args.log).upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    coloredlogs.install(
        fmt='%(asctime)s %(levelname)s %(message)s',
        datefmt='%d/%m/%Y %H:%M:%S',
        level=numeric_level)
    logging.getLogger("DCMRestClient").setLevel(numeric_level)
    logging.getLogger("requests.packages.urllib3").setLevel(logging.ERROR)

    args = parser.parse_args()
    global dcm_ip_address 
    dcm_ip_address= str(args.dcm_ip_address)
    global producer 
    producer = KafkaProducer(bootstrap_servers = dcm_ip_address + ":" + kafka_port, value_serializer=lambda x: json.dumps(x).encode('utf-8'))

    global spanish_site_url 
    spanish_site_url = "http://" + str(args.spanish_site_plugin_ip_port) + "/dcm_plugin/"
    global italian_site_url 
    italian_site_url = "http://" + str(args.italian_site_plugin_ip_port) + "/dcm_plugin/"
    global french_site_url 
    french_site_url = "http://" + str(args.french_site_plugin_ip_port) + "/dcm_plugin/"
    global greek_site_url 
    greek_site_url = "http://" + str(args.greek_site_plugin_ip_port) + "/dcm_plugin/"


    logger.info("Serving DCMRestClient on port %s", str(args.port))
    serve(app, host='0.0.0.0', port=args.port)
