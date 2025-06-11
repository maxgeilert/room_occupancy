"""Support for room occupancy binary sensors."""

from collections.abc import Callable
import logging
from typing import Optional

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant, Event
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_call_later, async_track_state_change_event

from .const import (
    CONF_ACTIVE_STATES,
    CONF_ENTITIES_KEEP,
    CONF_ENTITIES_TOGGLE,
    CONF_TIMEOUT,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Add entity."""
    _LOGGER.debug("binary_sensor.py async_setup_entry triggered!")
    _LOGGER.debug("entry: %s", entry.as_dict())
    async_add_entities(
        [
            RoomOccupancyBinarySensor(
                hass,
                entry,
            )
        ]
    )


class RoomOccupancyBinarySensor(BinarySensorEntity):
    """Representation of a room occupancy binary sensor."""

    _attr_should_poll = False
    _attr_has_entity_name = True
    _attr_device_class = BinarySensorDeviceClass.OCCUPANCY

    def __init__(self, hass: HomeAssistant, config) -> None:
        """Init."""
        _LOGGER.debug("Init triggered, config: %s", config.as_dict())
        data = config.as_dict()["data"]
        _LOGGER.debug("data: %s", data)
        self.hass = hass
        self.attr = {
            CONF_TIMEOUT: data[CONF_TIMEOUT],
            CONF_ENTITIES_TOGGLE: data[CONF_ENTITIES_TOGGLE],
            CONF_ENTITIES_KEEP: data[CONF_ENTITIES_KEEP],
            CONF_ACTIVE_STATES: data[CONF_ACTIVE_STATES],
            "device_class": BinarySensorDeviceClass.OCCUPANCY,
            "friendly_name": data[CONF_NAME],
        }
        self._state = STATE_OFF
        self._name = data[CONF_NAME]
        self._timeout_handle: Optional[Callable[[], None]] = None
        self.entity_id = (
            "binary_sensor." + self._name.lower().replace(" ", "_") + "_occupancy"
        )
        self._attr_device_class = BinarySensorDeviceClass.OCCUPANCY

        watched_entities = (
            self.attr[CONF_ENTITIES_TOGGLE] + self.attr[CONF_ENTITIES_KEEP]
        )
        for entity in watched_entities:
            async_track_state_change_event(self.hass, entity, self._handle_state_change)

    async def _handle_state_change(self, event: Event) -> None:
        """Handle a state change event for a watched entity."""
        await self.async_update()

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        _LOGGER.debug("update triggered for %s!", self.entity_id)
        found = self.check_states()
        if found:
            self._state = STATE_ON
            self.hass.states.async_set(
                entity_id=self.entity_id,
                new_state=self._state,
                attributes=self.attr,
            )
            if self._timeout_handle is not None:
                _LOGGER.debug("cancelling previous timeout: %s", self._timeout_handle)
                self._timeout_handle()
                self._timeout_handle = None
        elif self._state != STATE_OFF:
            _LOGGER.debug("state is off, setting a timeout")
            self._timeout_handle = async_call_later(
                self.hass, self.attr[CONF_TIMEOUT], self.timeout_func
            )
            _LOGGER.debug("timeout set: %s", self._timeout_handle)

    async def timeout_func(self, *args) -> None:
        """Set the state to off after the timeout."""
        _LOGGER.debug("timeout reached, setting state to off")
        self._state = STATE_OFF
        self.hass.states.async_set(
            entity_id=self.entity_id,
            new_state=self._state,
            attributes=self.attr,
        )
        self._timeout_handle = None

    def check_states(self) -> bool:
        """Check state of all entities."""
        found = False
        if self._state == STATE_ON:
            use_entities = (
                self.attr[CONF_ENTITIES_TOGGLE] + self.attr[CONF_ENTITIES_KEEP]
            )
        else:
            use_entities = self.attr[CONF_ENTITIES_TOGGLE]
        for entity in use_entities:
            state = self.hass.states.get(entity)
            if state is not None and state.state in self.attr[CONF_ACTIVE_STATES]:
                found = True
        return found

    async def update_listener(self, entry):
        """Handle options update."""
        _LOGGER.debug("update_listener triggered!")
        _LOGGER.debug("entry: %s", entry.as_dict())

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def device_class(self) -> BinarySensorDeviceClass:
        """Return the device class of the sensor."""
        return BinarySensorDeviceClass.OCCUPANCY

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self.entity_id}P"
