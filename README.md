# VDV736GTFSRT
This package provides a VDV736 compatible GTFS-RT ServiceAlerts converter. It uses a publish/subscribe or request/response connection to a VDV736 compliant datahub and publishes GTFS-RT ServiceAlerts via a configurable GET endpoint or alternatively as differential GTFS-RT feed to a MQTT broker.

## Basic Idea
Incident information or service alerts are part of realtime passenger information. However, in most OpenData sets, there're no GTFS-RT or even SIRI-SX alerts available. The purpose of this package is to provide a full VDV736 compliant converter to generate GTFS-RT service alerts.

Therefore, the application uses a [pyvdv736](https://github.com/sebastianknopf/pyvdv736) subscriber to connect to VDV736 compliant data hub. Both request patterns, publish/subscribe and request/response are supported. After receiving some `PtSituationElement`s, they're converted to GTFS-RT service alerts using different adapters and exposed using a minimal [uvicorn](https://github.com/encode/uvicorn) webserver or alternatively pushed to a MQTT broker as differential GTFS-RT feed.

The purpose of different adapters is to react to different implementations of the delivered VDV736 / SIRI-SX data. There's a `VdvStandardAdaper` strongly following the VDV736 sepcs, which used by default. You can use different adapters by configuration.

## Installation
There're different options to use vdv736gtfsrt. You can use it by cloning this repository and install it into your virtual environment directly:
```
git clone https://github.com/sebastianknopf/vdv736gtfsrt.git
cd vdv736gtfsrt

pip install .
```
and run it by using
```
python -m vdv736gtfsrt server ./config/your-config.yaml -h 127.0.0.1 -p 8080
```
This is especially good for development.