# Showroom VDV736GTFSRT
In this little showroom, you can see several examples how this project is used in production including a working GoogleMaps integration.

## Lifecycle of a VDV736 Situation Object
While a GTFS-RT has normally only one state in its lifecycle, a typical VDV736 situation object has an extended lifecycle with three message types: The first message, the main message and the final message. The first message is the first message published to passengers with basic information about the incident. Once a dispatcher or traffic agency added more information (e.g. divertions, moved stops, ...), the first message becomes the main message which can be enhanced and changed during this state as often as neccessary. When the incident is passed by, typically a final message is shown stating that the public transport operations are normalizing at the moment.

VDV736GTFSRT is capable to handle all those message types. First and main message is simply converted to the corresponding GTFS-RT pendant including their effects, their causes and active periods. The active periods are taken from the element `ValidityPeriod` in the VDV736 data structure. See the following example for a typical message shown in GoogleMaps:

![Departure Table with Service Alert](gmaps_departures_view.jpg) ![Full Service Alert View](gmaps_full_view.jpg)

After the final message is sent or fetched from the datahub, this message is slightly modified regardning the effect and the active periods. Effects are manipulating routing results in several cases (e.g. NO_SERVICE at a stop means all departures are removed for this stop!). As the final message states that the incident is finally passed by, there's no effect in that manner anymore. Hence, the `effect` property of the GTFS-RT service alert is turned to `NO_EFFECT` to avoid these manipulations at all. As active periods are derived from `ValidityPeriod` elements, the time range of the active period does normally _not_ cover the time range for showing the final message. Hence, the `end` property of the active periods in the corresponding GTFS-RT service alert is removed to show the alert 'forever'. See the following examples with a main and final message:

![Main Message](gmaps_main_message.jpg) ![Final Message](gmaps_final_message.jpg)

As the underlaying VDV736 situation becomes finally 'closed' after showing the final message for a certain time range, the GTFS-RT service alert ist finally removed from the GTFS-RT stream. GoogleMaps does not see the service alert anymore when fetching data, so it also does not show up the service alert anymore.

## Behaviour in MQTT Streaming
When using the MQTT streaming functionality, the alerts do not simply disappear, but become deleted using the `is_deleted` flag set to `True` in a last message published to the corresponding MQTT topic after the underlaying VDV736 situation object was 'closed'. This ensures, that all consuming systems using this differential GTFS-RT feed are able to detect that the service alert became invalid and shall be removed.