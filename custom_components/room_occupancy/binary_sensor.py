"""Use Bayesian Inference to trigger a binary sensor."""
from __future__ import annotations

import logging
from sqlalchemy import false

import voluptuous as vol

import homeassistant.helpers.event as eventHelper
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    PLATFORM_SCHEMA,
    DOMAIN,
    STATE_OFF,
    STATE_ON,
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
    STATE_OFF,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant, State, callback
from homeassistant.exceptions import ConditionError, TemplateError
from homeassistant.helpers import condition
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from homeassistant.helpers.template import result_as_boolean
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import DOMAIN, PLATFORMS

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


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Setup room occupancy entities"""
    name = config.get(CONF_NAME)
    roomname = config.get(CONF_ROOMNAME)
    timeout = config.get(CONF_TIMEOUT)
    entities_toggle = config.get(CONF_ENTITIES_TOGGLE)
    entities_keep = config.get(CONF_ENTITITES_KEEP)
    active_states = config.get(CONF_ACTIVE_STATES)

    _LOGGER.debug("setup_platform triggered!")
    _LOGGER.debug(
        "name: %s, roomname %s, timeout %i, entities_toggle %s, entities_keep %s, active_states %s",
        name,
        roomname,
        timeout,
        entities_toggle,
        entities_keep,
        active_states,
    )
    add_entities(
        [
            RoomOccupancyBinarySensor(
                hass,
                config,
            )
        ]
    )


class RoomOccupancyBinarySensor(BinarySensorEntity):
    def __init__(self, hass, config):
        self.hass = hass
        self.attr = {
            CONF_ROOMNAME: config.get(CONF_ROOMNAME),
            CONF_TIMEOUT: config.get(CONF_TIMEOUT),
            CONF_ENTITIES_TOGGLE: config.get(CONF_ENTITIES_TOGGLE),
            CONF_ENTITITES_KEEP: config.get(CONF_ENTITITES_KEEP),
            CONF_ACTIVE_STATES: config.get(CONF_ACTIVE_STATES),
        }
        self._state = STATE_OFF
        self._name = config.get(CONF_NAME)
        _LOGGER.debug("__init__ triggered!")
        _LOGGER.debug(
            "name: %s, roomname: %s, entities_toggle: %s, entities_keep: %s, timeout: %i, state: %s, active_states: %s",
            self._name,
            self.attr[CONF_ROOMNAME],
            self.attr[CONF_ENTITIES_TOGGLE],
            self.attr[CONF_ENTITITES_KEEP],
            self.attr[CONF_TIMEOUT],
            self._state,
            self.attr[CONF_ACTIVE_STATES],
        )

        eventHelper.track_state_change(
            self.hass,
            self.attr[CONF_ENTITIES_TOGGLE] + self.attr[CONF_ENTITITES_KEEP],
            self.entity_state_changed,
        )

    #     eventHelper.track_time_change(self.hass, self.time_changed)

    def entity_state_changed(self, entity_id, old_state, new_state):
        _LOGGER.debug(
            "entity_state_changed triggered! entity: %s, old_state: %s, new_state: %s"
            % (entity_id, old_state, new_state)
        )
        self.update()

    # def time_changed(self, time):
    #    self.update()

    def update(self):
        # if state is false, check all entities
        _LOGGER.debug("update triggered!")
        found = False

        if self._state is "occupied":
            use_entities = (
                self.attr[CONF_ENTITIES_TOGGLE] + self.attr[CONF_ENTITITES_KEEP]
            )
        else:
            use_entities = self.attr[CONF_ENTITIES_TOGGLE]
        _LOGGER.debug("checking the following entities: %s", use_entities)
        _LOGGER.debug(
            "the following states are considered true: %s"
            % self.attr[CONF_ACTIVE_STATES]
        )
        for entity in use_entities:
            _LOGGER.debug("checking entity %s" % entity)
            state = self.hass.states.get(entity).state
            _LOGGER.debug("state is: %s" % state)
            if state in self.attr[CONF_ACTIVE_STATES]:
                _LOGGER.debug("entity is active!")
                found = True
            else:
                _LOGGER.debug("entity is inactive!")
        if found:
            self._state = "occupied"
            #self.hass.state.set()
        else:
            self._state = "not occupied"
        _LOGGER.debug("finished setting state, _state is: %s" % self._state)
        self.hass.states.set("room_occupancy." + self._name, self._state, self.attr)

    @property
    def name(self):
        return self._name

    @property
    def is_on(self):
        return self._state

    @property
    def device_class(self):
        return DEVICE_CLASS_OCCUPANCY
