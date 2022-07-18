"""Room Occupancy Binary Sensor"""
from __future__ import annotations

import logging
from sqlalchemy import true

import voluptuous as vol
from homeassistant import config_entries

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


async def async_setup(hass, config):
    """Set up the Hue platform."""
    _LOGGER.debug("__init__.py async_setup triggered! config: %s" % config)
    # hass.async_create_task(
    #    hass.config_entries.async_forward_entry_setup(config, "binary_sensor")
    # )

    return True


async def async_setup_entry(hass, entry):
    """Add entity"""
    _LOGGER.debug("__init__.py async_setup_entry triggerd!")
    for field in entry.as_dict():
        _LOGGER.debug("%s: %s", field, entry.as_dict()[field])
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
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "binary_sensor")
    )
    return True
