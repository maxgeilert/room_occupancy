"""Use multiple sensors to control a binary sensor."""
from __future__ import annotations

import logging

import voluptuous as vol

import homeassistant.helpers.event as eventHelper
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    PLATFORM_SCHEMA,
    DEVICE_CLASS_OCCUPANCY,
)
from homeassistant.const import (
    CONF_DEVICE_CLASS,
    CONF_ENTITY_ID,
    CONF_NAME,
    CONF_PLATFORM,
    CONF_STATE,
    CONF_VALUE_TEMPLATE,
    STATE_OFF,
    STATE_ON,
)
from homeassistant.core import HomeAssistant, State, callback
from homeassistant.exceptions import ConditionError, TemplateError
from homeassistant.helpers import condition
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from homeassistant.helpers.template import result_as_boolean
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import *

_LOGGER = logging.getLogger(__name__)


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): cv.positive_int,
        vol.Required(CONF_ENTITIES_TOGGLE, default=[]): cv.ensure_list,
        vol.Required(CONF_ENTITIES_KEEP, default=[]): cv.ensure_list,
        vol.Optional(
            CONF_ACTIVE_STATES, default='["on", "occupied", 1, True, "active"]'
        ): cv.ensure_list,
    }
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Setup room occupancy entities"""
    name = config.get(CONF_NAME)
    timeout = config.get(CONF_TIMEOUT)
    entities_toggle = config.get(CONF_ENTITIES_TOGGLE)
    entities_keep = config.get(CONF_ENTITIES_KEEP)
    active_states = config.get(CONF_ACTIVE_STATES)

    _LOGGER.debug("binary_sensor.py setup_platform triggered!")
    _LOGGER.debug(
        "name: %s, timeout %i, entities_toggle %s, entities_keep %s, active_states %s",
        name,
        timeout,
        entities_toggle,
        entities_keep,
        active_states,
    )
    await async_add_entities(
        [
            RoomOccupancyBinarySensor(
                hass,
                config,
            )
        ]
    )


async def async_setup_entry(hass, entry, async_add_entities):
    """Add entity"""
    _LOGGER.debug("binary_sensor.py async_setup_entry triggerd!")
    data = entry.as_dict()["data"]
    name = data[CONF_NAME]
    timeout = data[CONF_TIMEOUT]
    entities_toggle = data[CONF_ENTITIES_TOGGLE]
    entities_keep = data[CONF_ENTITIES_KEEP]
    active_states = data[CONF_ACTIVE_STATES]
    _LOGGER.debug(
        "name: %s, timeout %i, entities_toggle %s, entities_keep %s, active_states %s",
        name,
        timeout,
        entities_toggle,
        entities_keep,
        active_states,
    )
    async_add_entities(
        [
            RoomOccupancyBinarySensor(
                hass,
                entry,
            )
        ]
    )


class RoomOccupancyBinarySensor(BinarySensorEntity):
    def __init__(self, hass, config):
        _LOGGER.debug(
            "binary_sensor.py __init__ triggered! config: %s" % config.as_dict()
        )
        data = config.as_dict()["data"]
        _LOGGER.debug(data)
        self.hass = hass
        self.attr = {
            CONF_TIMEOUT: data[CONF_TIMEOUT],
            CONF_ENTITIES_TOGGLE: data[CONF_ENTITIES_TOGGLE],
            CONF_ENTITIES_KEEP: data[CONF_ENTITIES_KEEP],
            CONF_ACTIVE_STATES: data[CONF_ACTIVE_STATES],
        }
        self._state = STATE_OFF
        self._name = data[CONF_NAME]
        _LOGGER.debug(
            "name: %s, entities_toggle: %s, entities_keep: %s, timeout: %i, state: %s, active_states: %s",
            self._name,
            self.attr[CONF_ENTITIES_TOGGLE],
            self.attr[CONF_ENTITIES_KEEP],
            self.attr[CONF_TIMEOUT],
            self._state,
            self.attr[CONF_ACTIVE_STATES],
        )

        eventHelper.async_track_state_change(
            self.hass,
            self.attr[CONF_ENTITIES_TOGGLE] + self.attr[CONF_ENTITIES_KEEP],
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
        _LOGGER.debug("update triggered for %s!" % self.entity_id)
        found = False

        if self._state == STATE_ON:
            use_entities = (
                self.attr[CONF_ENTITIES_TOGGLE] + self.attr[CONF_ENTITIES_KEEP]
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
            self._state = STATE_ON
            # self.hass.state.set()
        else:
            self._state = STATE_OFF
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
