"""Config flow for Room Occupancy integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigFlow,
    ConfigFlowResult,
    ConfigEntry,
    OptionsFlow,
)
from homeassistant.const import CONF_NAME
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv


from .const import (
    CONF_ACTIVE_STATES,
    CONF_ENTITIES_KEEP,
    CONF_ENTITIES_TOGGLE,
    CONF_TIMEOUT,
    DEFAULT_ACTIVE_STATES,
    DEFAULT_NAME,
    DEFAULT_TIMEOUT,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class OptionsFlowHandler(OptionsFlow):
    """Options flow for room occupancy."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        # self.options = dict(config_entry.options)
        # _LOGGER.debug("OptionsFlow:Init: got triggered for: %s", config_entry)
        # _LOGGER.debug("Options:")
        # _LOGGER.debug(self.options)

    # async def async_end(self):
    #     """Finalize the ConfigEntry creation."""
    #     _LOGGER.debug(
    #         "Recreating entry %s due to configuration change",
    #         self.config_entry.entry_id,
    #     )
    #     self.hass.config_entries.async_update_entry(
    #         self.config_entry, data=self.options
    #     )
    #     return self.async_create_entry(title=None, data=None)

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        _LOGGER.debug("OptionsFlow:AsyncStepInit: got triggered")
        _LOGGER.debug(self.config_entry)
        _LOGGER.debug("entry_id: %s", self.config_entry.entry_id)

        if user_input is not None:
            _LOGGER.debug("Userinput found:")
            _LOGGER.debug(user_input)
            if "timeout" in self.config_entry.data:
                _LOGGER.debug(
                    "timeout found, adding %s", self.config_entry.data["timeout"]
                )
                # user_input["timeout"] = self.config_entry.data["timeout"]
            # user_input.name = self.config_entry.data["name"]
            _LOGGER.debug("config entry data:")
            _LOGGER.debug(self.config_entry.data)  # this is the old config
            user_input["name"] = self.config_entry.data["name"]
            _LOGGER.debug("modified Userinput:")
            _LOGGER.debug(user_input)  # this is the new config
            self.hass.config_entries.async_update_entry(
                self.config_entry, data=user_input, options=self.config_entry.options
            )
            return self.async_create_entry(title="", data=user_input)

        all_entities = []
        for domain in (
            "sensor",
            "binary_sensor",
            "timer",
            "input_boolean",
            "media_player",
        ):
            all_entities += self.hass.states.async_entity_ids(domain)
        _LOGGER.debug("all entities: %s", all_entities)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_TIMEOUT,
                        default=self.config_entry.data["timeout"],
                    ): cv.positive_int,
                    vol.Required(
                        CONF_ENTITIES_TOGGLE,
                        default=self.config_entry.data["entities_toggle"],
                    ): cv.multi_select(sorted(all_entities)),
                    vol.Optional(
                        CONF_ENTITIES_KEEP,
                        default=self.config_entry.data["entities_keep"],
                    ): cv.multi_select(sorted(all_entities)),
                    vol.Optional(
                        CONF_ACTIVE_STATES,
                        default=self.config_entry.data["active_states"],
                    ): cv.string,
                }
            ),
        )


class RoomOccupancyConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Room Occupancy."""

    VERSION = 1

    @staticmethod
    # @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        all_entities = []
        for domain in (
            "sensor",
            "binary_sensor",
            "timer",
            "input_boolean",
            "media_player",
        ):
            all_entities += self.hass.states.async_entity_ids(domain)
        _LOGGER.debug("all entities: %s", all_entities)
        errors: dict[str, str] = {}
        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data=user_input,
            )
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default=DEFAULT_NAME): cv.string,
                    vol.Required(
                        CONF_TIMEOUT, default=DEFAULT_TIMEOUT
                    ): cv.positive_int,
                    vol.Required(CONF_ENTITIES_TOGGLE, default=[]): cv.multi_select(
                        sorted(all_entities)
                    ),
                    vol.Required(CONF_ENTITIES_KEEP, default=[]): cv.multi_select(
                        sorted(all_entities)
                    ),
                    vol.Optional(
                        CONF_ACTIVE_STATES, default=DEFAULT_ACTIVE_STATES
                    ): cv.string,
                }
            ),
            errors=errors,
        )
