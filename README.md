# VDV736GTFSRT
This package provides a VDV736 compatible GTFS-RT ServiceAlerts converter. It uses a publish/subscribe or request/response connection to a VDV736 compliant datahub and publishes GTFS-RT ServiceAlerts via a configurable GET endpoint or alternatively as differential GTFS-RT feed to a MQTT broker.

## Basic Idea
Incident information or service alerts are part of realtime passenger information. However, in most OpenData sets, there're no GTFS-RT or even SIRI-SX alerts available. The purpose of this package is to provide a full VDV736 compliant converter to generate GTFS-RT service alerts.

Therefore, the application uses a [pyvdv736](https://github.com/sebastianknopf/pyvdv736) subscriber to connect to VDV736 compliant data hub. Both request patterns, publish/subscribe and request/response are supported. After receiving some `PtSituationElement`s, they're converted to GTFS-RT service alerts using different adapters and exposed using a minimal [uvicorn](https://github.com/encode/uvicorn) webserver or alternatively pushed to a MQTT broker as differential GTFS-RT feed.

The purpose of different adapters is to react to different implementations of the delivered VDV736 / SIRI-SX data. There's a `VdvStandardAdaper` strongly following the VDV736 sepcs, which used by default. You can use different adapters by configuration.

## Installation
There're different options to use vdv736gtfsrt. You can use it by cloning this repository and install it into your virtual environment directly:
```bash
git clone https://github.com/sebastianknopf/vdv736gtfsrt.git
cd vdv736gtfsrt

pip install .
```
and run it by using
```bash
python -m vdv736gtfsrt server ./config/your-config.yaml -h 127.0.0.1 -p 8080
```
This is especially good for development.

If you simply want to run vdv736gtfsrt on your server (e.g. behind a reverse-proxy), you also can use docker:

```bash
docker run 
   --rm
   -v /host/etc/vdv736gtfsrt/config.yaml:/app/config/config.yaml
   -v /host/etc/vdv736gtfsrt/participants.yaml:/app/config/participants.yaml
   -p 8080:8080
   -p 9091:9091
   sebastianknopf/vdv736gtfsrt:latest
   server -p 8080 -h 0.0.0.0
```

_Note: In this example there're two ports configured: One port for the GTFS-RT server (8080) and one port for the VDV736 subscriber (9091). The latter port depends on
the participant configuration in `participants.yaml` as well as the used pattern (publish/subscribe or request/response)._

## Configuration
The configuration YAML file enables you to customize the vdv736gtfsrt instance for your needs. See [config/default.yaml](./config/default.yaml) for further assistance.

### Participant Configuration
As a typical VDV realtime system, there're many different participants (sometimes also known as 'Leitstelle' with a 'Leitstellenkennung'). Additionally to the config file, a participants config file is required. By default, the file `./config/participants.yaml` is used. If you want to specify another participants config file, set the key `app.participants` to the corresponding value.

The keys `app.subscriber` and `app.publisher` are used to set the participant IDs for the subscriber and the publisher which should be subscribed (or requested).

For more information about the participants configuration, see [pyvdv736](https://github.com/sebastianknopf/pyvdv736).

### Running in Request/Reponse Pattern
By default, vdv736gtfsrt uses the more complexe publish/subscribe pattern to act as realtime capable system. However, the request/response pattern is much easier to setup. Simply set the key `app.pattern` to `request/response` to put vdv736gtfsrt into request/response mode.

### Publishing differential GTFS-RT to MQTT Broker
Instead of running a GTFS-RT server, you can also run a MQTT publisher. This makes the system fully realtime capable. To run a MQTT publisher, use the command

```bash
python -m vdv736gtfsrt mqtt ./config/your-config.yaml -m mqtt://[username]:[password]@[domain]/here/is/your/topic/for/alert/[alertId]
```

or alternatively docker

```bash
docker run 
   --rm
   -v /host/etc/vdv736gtfsrt/config.yaml:/app/config/config.yaml
   -v /host/etc/vdv736gtfsrt/participants.yaml:/app/config/participants.yaml
   -p 9091:9091
   sebastianknopf/vdv736gtfsrt:latest
   mqtt -m mqtt://[username]:[password]@[domain]/here/is/your/topic/for/alert/[alertId]
```

Replace `[username]`, `[password]`, `[domain]` by your values. The key `[alertId]` is replaced with the entity ID.

_Note: In this example there're two ports configured: One port for the GTFS-RT server (8080) and one port for the VDV736 subscriber (9091). The latter port depends on
the participant configuration in `participants.yaml` as well as the used pattern (publish/subscribe or request/response)._

## License
This project is licensed under the Apache License. See [LICENSE.md](LICENSE.md) for more information.