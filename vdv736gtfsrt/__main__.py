import click
import uvicorn

from urllib.parse import urlparse
from vdv736gtfsrt.server import GtfsRealtimeServer
from vdv736gtfsrt.mqtt import GtfsRealtimePublisher
from vdv736gtfsrt.version import version

@click.group()
@click.version_option(version)
def cli():
    pass

@cli.command()
@click.argument('config', default='/app/config/config.yaml')
@click.option('--host', '-h', default='0.0.0.0', help='Hostname for the server to listen')
@click.option('--port', '-p', default='8080', help='Port for the server to listen')
def server(config, host, port):
    server = GtfsRealtimeServer(config)
    
    uvicorn.run(
        app=server.create(), 
        host=host, 
        port=int(port), 
        proxy_headers=True,
        forwarded_allow_ips=[
            '172.17.0.1',
            '127.0.0.1'
        ]
    )

@cli.command()
@click.argument('config', default='/app/config/config.yaml')
@click.option('--mqtt', '-m', help='MQTT connection and topic URI')
def mqtt(config, mqtt):

    mqtt_uri = urlparse(mqtt)
    mqtt_params = mqtt_uri.netloc.split('@')
    mqtt_topic = mqtt_uri.path

    if len(mqtt_params) == 1:
        mqtt_username, mqtt_password = None, None
        mqtt_host, mqtt_port = mqtt_params[0].split(':')
    elif len(mqtt_params) == 2:
        mqtt_username, mqtt_password = mqtt_params[0].split(':')
        mqtt_host, mqtt_port = mqtt_params[1].split(':')

    publisher = GtfsRealtimePublisher(config, mqtt_host, mqtt_port, mqtt_username, mqtt_password, mqtt_topic, 300)
    publisher.run()


if __name__ == '__main__':
    cli()