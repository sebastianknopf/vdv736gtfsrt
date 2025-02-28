import click
import uvicorn

from vdv736gtfsrt.server import GtfsRealtimeServer
from vdv736gtfsrt.version import version

@click.group()
@click.version_option(version)
def cli():
    pass

@cli.command()
@click.argument('config')
@click.option('--host', '-h', default='0.0.0.0', help='Hostname for the server to listen')
@click.option('--port', '-p', default='8080', help='Port for the server to listen')
def run(config, host, port):
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

if __name__ == '__main__':
    cli()