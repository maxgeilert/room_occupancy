# Room Occupancy Sensor

You need quiet a few sensors to reliably tell if a room is occupied or not. This ranges from motion- and presence sensors over door contacts to media players and input booleans. This integration combines all of those into a neat package and adds a timeout functionality, making it easy to base automations on a simple binary sensor.

When adding the integration, the following configuration is necessary:

### Name

| name            | description                                                                    | required | type    |
| --------------- | ------------------------------------------------------------------------------ | -------- | ------- |
| name            | The name of the sensor, most likely a room name                                | true     | string  |
| timeout         | Number of seconds it takes to set the sensor to off.                           | true     | integer |
| entities_toggle | List of entities which are allowed to turn the sensor on (e.g. motion sensors) | true     | list    |
| entities_keep   | List of entities which are allowed to keep the sensor on (e.g. mmwave sensors) | false    | list    |

## Example automations

To use this sensor, you've to create automations to control your room.

### Light automation

```yaml
- alias: room light
  description: "occupancy light control"
  trigger:
    - platform: state
      entity_id: binary_sensor.room_occupancy
      id: "on"
      to: detected
    - platform: state
      entity_id: binary_sensor.room_occupancy
      id: "on"
      to: clear
  condition: []
  action:
    - choose:
        - conditions:
            - condition: trigger
              id: "on"
          sequence:
            - service: light.turn_on
              target:
                entity_id: light.my_light
        - conditions:
            - condition: trigger
              id: "off"
          sequence:
            - service: light.turn_off
              target:
                entity_id: light.my_light
      default: []
  mode: single
  id: someid
```

### Music automation

````yaml
- alias: room music
  description: 'occupancy music control'
  trigger:
  - platform: state
    entity_id: binary_sensor.room_occupancy
    id: 'on'
    to: detected
  - platform: state
    entity_id: binary_sensor.room_occupancy
    id: 'on'
    to: clear
  condition: []
  action:
  - choose:
    - conditions:
      - condition: trigger
        id: 'on'
      sequence:
      - service: media_player.volume_mute
        data:
          is_volume_muted: false
        target:
          entity_id:
            - media_player.room
    - conditions:
      - condition: trigger
        id: 'off'
      sequence:
      - service: media_player.volume_mute
        data:
          is_volume_muted: true
        target:
          entity_id:
            - media_player.room
    default: []
  mode: single
  id: someid
```
````
