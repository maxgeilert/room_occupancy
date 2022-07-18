from homeassistant import config_entries
from .const import DOMAIN
import voluptuous as vol
import logging
from homeassistant.const import CONF_NAME
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from typing import Any, Dict, Optional
from .const import *

_LOGGER = logging.getLogger(__name__)

SENSOR_SCHEMA = {
    vol.Required(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Required(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): cv.port,
    vol.Required(CONF_ENTITIES_TOGGLE, default=[]): cv.string,
    vol.Required(CONF_ENTITIES_KEEP, default=[]): cv.string,
    vol.Optional(CONF_ACTIVE_STATES, default=DEFAULT_ACTIVE_STATES): cv.string,
    vol.Optional("add_another"): cv.boolean,
}


class RoomOccupancyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Example config flow."""

    async def async_step_user(self, user_input=None):
        _LOGGER.debug("async_step_user triggered, user_input: %s" % user_input)
        if user_input is not None:
            _LOGGER.debug("user_input is not none!")
            # self.attr = {
            #    CONF_ROOMNAME: user_input[CONF_ROOMNAME],
            #    CONF_TIMEOUT: user_input[CONF_TIMEOUT],
            #    CONF_ENTITIES_TOGGLE: user_input[CONF_ENTITIES_TOGGLE],
            #    CONF_ENTITIES_KEEP: user_input[CONF_ENTITIES_KEEP],
            #    CONF_ACTIVE_STATES: user_input[CONF_ACTIVE_STATES],
            # }
            # self._name = user_input[CONF_NAME]
            _LOGGER.debug(user_input)
            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        _LOGGER.debug("returning async_show_form!")
        return await self._show_setup_form(None, "user")

    async def _show_setup_form(self, errors=None, step_id="user"):
        """Show the setup form to the user"""
        for domain in ["sensor", "binary_sensor", "timer", "input_boolean"]:
            all_entities = []
            all_entities = all_entities + [
                entity for entity in self.hass.states.async_entity_ids(domain)
            ]
        return self.async_show_form(
            step_id=step_id,
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default=DEFAULT_NAME): cv.string,
                    vol.Required(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): cv.port,
                    vol.Required(CONF_ENTITIES_TOGGLE, default=[]): cv.multi_select(
                        sorted(all_entities)
                    ),
                    vol.Required(CONF_ENTITIES_KEEP, default=[]): cv.multi_select(
                        sorted(all_entities)
                    ),
                    vol.Optional(
                        CONF_ACTIVE_STATES, default=DEFAULT_ACTIVE_STATES
                    ): cv.string,
                    vol.Optional("add_another"): cv.boolean,
                }
            ),
        )
