DOMAIN = "room_occupancy"
PLATFORMS = ["binary_sensor"]
TIMEOUT = 2
ROOMNAME = "Livingroom"
ENTITIES_TOGGLE = ["binary_sensor.livingroom_motion"]
ENTITIES_KEEP = ["binary_sensor.livingroom_occupancy"]
ACTIVE_STATES = ["active", "on", True, "occupied"]
