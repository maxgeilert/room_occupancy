"""Combine multiple sensors into a room occupancy binary sensor."""
from __future__ import annotations

from collections import OrderedDict
import logging

import voluptuous as vol

from homeassistant.components.binary_sensor import (
    PLATFORM_SCHEMA,
    BinarySensorEntity,
    DEVICE_CLASS_OCCUPANCY,
)
from homeassistant.const import (
    CONF_ABOVE,
    CONF_BELOW,
    CONF_DEVICE_CLASS,
    CONF_ENTITY_ID,
    CONF_NAME,
    CONF_PLATFORM,
    CONF_STATE,
    CONF_VALUE_TEMPLATE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant, State, callback
from homeassistant.exceptions import ConditionError, TemplateError
from homeassistant.helpers import condition
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import (
    TrackTemplate,
    async_track_state_change_event,
    async_track_template_result,
)
from homeassistant.helpers.reload import async_setup_reload_service
from homeassistant.helpers.template import result_as_boolean
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import DOMAIN, PLATFORMS

ATTR_OBSERVATIONS = "observations"
# ATTR_OCCURRED_OBSERVATION_ENTITIES = "occurred_observation_entities"
# ATTR_PROBABILITY = "probability"
# ATTR_PROBABILITY_THRESHOLD = "probability_threshold"

# CONF_OBSERVATIONS = "observations"
# CONF_PRIOR = "prior"
# CONF_TEMPLATE = "template"
# CONF_PROBABILITY_THRESHOLD = "probability_threshold"
# CONF_P_GIVEN_F = "prob_given_false"
# CONF_P_GIVEN_T = "prob_given_true"
# CONF_TO_STATE = "to_state"

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "Room Occupancy Sensor"
CONF_ROOMNAME = "roomname"
DEFAULT_ROOMNAME = "exampleroom"
CONF_TIMEOUT = "timeout"
DEFAULT_TIMEOUT = 2
CONF_ENTITIES_TOGGLE = "entities_toggle"
CONF_ENTITITES_KEEP = "entities_keep"
CONF_ACTIVE_STATES = "active_states"
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Required(CONF_ROOMNAME, default=DEFAULT_ROOMNAME): cv.string,
        vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): cv.positive_int,
        vol.Required(CONF_ENTITIES_TOGGLE, default=[]): cv.ensure_list,
        vol.Required(CONF_ENTITITES_KEEP, default=[]): cv.ensure_list,
        vol.Optional(
            CONF_ACTIVE_STATES, default=["on", "occupied", 1, True, "active"]
        ): cv.ensure_list,
    }
)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Room Occupancy Binary sensor."""
    await async_setup_reload_service(hass, DOMAIN, PLATFORMS)

    name = config.get(CONF_NAME)
    roomname = config.get(CONF_ROOMNAME)
    timeout = config.get(CONF_TIMEOUT)
    entities_toggle = config.get(CONF_ENTITIES_TOGGLE)
    entities_keep = config.get(CONF_ENTITITES_KEEP)
    active_states = config.get(CONF_ACTIVE_STATES)

    async_add_entities(
        [
            RoomOccupancyBinarySensor(
                name, roomname, entities_toggle, entities_keep, timeout, active_states
            )
        ]
    )


class RoomOccupancyBinarySensor(BinarySensorEntity):
    def __init__(
        self, name, roomname, entities_toggle, entities_keep, timeout, active_states
    ):
        self._name = name
        self.roomname = roomname
        self.entities_toggle = entities_toggle
        self.entities_keep = entities_keep
        self.timeout = timeout
        self._state = False
        self.active_states = active_states

    @property
    def name(self):
        return self._name

    @property
    def is_on(self):
        return self._state

    @property
    def device_class(self):
        return DEVICE_CLASS_OCCUPANCY

    async def async_added_to_hass(self):
        """
        Call when entity about to be added.
        All relevant update logic for instance attributes occurs within this closure.
        Other methods in this class are designed to avoid directly modifying instance
        attributes, by instead focusing on returning relevant data back to this method.
        The goal of this method is to ensure that `self.current_observations` and `self.probability`
        are set on a best-effort basis when this entity is register with hass.
        In addition, this method must register the state listener defined within, which
        will be called any time a relevant entity changes its state.
        """

        @callback
        def async_room_occupancy_state_listener(event):
            """
            Handle sensor state changes.
            When a state changes, we must update our list of current states,
            and recheck the status of the sensor.
            """
            # new_state = event.data.get("new_state")

            # if new_state is None or new_state.state == STATE_UNKNOWN:
            #    return

            # changed_entity = event.data.get("entity_id")
            _LOGGER.debug("got event:\n%s", event)
            if (
                event.data.get("entity_id") in self.entities_toggle
                or self.entities_keep
            ):
                self.async_update(self)

    async def async_update(self, hass):
        """Get the latest data and update the states."""
        _LOGGER.debug("async_update triggered! ")
        # if the current state is unoccpied check only entites that are allowed to toggle
        if self._state is False:
            for entity in self.entities_toggle:
                state = hass.states.get(entity).state
                if state in self.active_states:
                    self._state = True
        # if the current state is occupied, check all entities
        else:
            for entity in self.entities_toggle + self.entities_keep:
                state = hass.states.get(entity).state
                if state in self.active_states:
                    self._state = True
        self.async_write_ha_state()
