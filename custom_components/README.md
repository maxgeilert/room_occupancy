# Room cccupancy sensor for Home Assistant

## Overview

This component evaluates the state of multiple sensors to determine if a room is occupied or not. This combined with a timeout function results in a
reliable aggregated occupancy sensor which could then be used to trigger automations.

---

## Features

- **Multi-entity aggregation**: Monitor any mix of sensors (motion detectors, contact sensors, ble tracking, mmwave,...).
- **Support for custom states**: Define which states should be considered "true", handy for custom sensors like ble room tracking
- **Customizable timeout**: Define how long after the last activity the room should be considered vacant.
- **Single source of truth for automations**: One entity to define the state of the room


---

## Installation via HACS

1. Go to **HACS → Integrations → Explore & Add Repositories**.
2. Add this repo as a custom repository.
3. Install the integration.
4. Restart Home Assistant.

---

Concepts
---
To ensure that the room won't get turned on by unreliable sensors, entities are split in two groups:

### Toggle entities
These entities are able to turn on the sensor, so they should be as reliable as posible and don't produce false positives, for example classic motion sensors.

### Keep entities
These entities on the other hand are only allowed to keep the sensor on if it already is, for things like milimeter wave sensors or ble tracking, which could sometimes produce false positives.


## Configuration

Add a new sensor under **Settings → Devices & Services → Add Integration**).

Supply the following:
- Name of the sensor (e.g. Livingroom)
- Timeout in seconds
- Toggle entitites
- Keep entitites
- States considered true
