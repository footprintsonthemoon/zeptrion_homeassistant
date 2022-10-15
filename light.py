"""Support for Zeptrion  bulbs."""
from __future__ import annotations

import logging
from typing import Any

from pyzeptrion.bulb import ZeptrionBulb
from pyzeptrion.device import ZeptrionDevice
from pyzeptrion.exceptions import ZeptrionConnectionError
from pyzeptrion.const import BULB_ON, ON_STATE, OFF_STATE
import voluptuous as vol

from homeassistant.components.light import (
    PLATFORM_SCHEMA,
    LightEntity,
    LightEntityFeature,
)

from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import PlatformNotReady
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "Zeptrion bulb"
CONF_CHN = "chn"
DOMAIN = "zeptrion"
#_LOGGER.warning("In setup: %s", chn)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_CHN, default=1): cv.positive_int,
    }
)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Zeptrion light integration."""
    host = config.get(CONF_HOST)
    chn = config.get(CONF_CHN)

    bulb = await ZeptrionBulb.create(ZeptrionBulb,host, chn)
    async_add_entities([ZeptrionLight(bulb)], True)

class ZeptrionLight(LightEntity):
    """Representation of the Zeptrion bulb."""

    def __init__(self, bulb):
        """Initialize the light."""
        self._bulb = bulb
        self._host = bulb.host
        self._chn = bulb.chn
        self._attr_name = bulb.name
        self._name = bulb.name
        self._unique_id = bulb.dev_id
        self._state = bulb.state
        self._available = False
        self._brightness = 0

    @property
    def name(self):
        """Return the display name of this light."""
        return self._name

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def brightness(self):
        """Return the brightness of the light."""
        return self._brightness


    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available


    @property
    def is_on(self):
        """Return true if light is on."""
        return self._state

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        try:
                await self._bulb.turn_on()
                self._state = ON_STATE
                self._brightness = 255
        except ZeptrionConnectionError:
            _LOGGER.warning("No route to Zeptrion bulb")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the bulb."""
        try:
            await self._bulb.turn_off()
            self._state = OFF_STATE
            self._brightness = 0
        except ZeptrionConnectionError:
            _LOGGER.warning("Turn OFF: he Zeptrion bulb is not online")

    async def async_update(self) -> None:
        """Fetch new state data for this light."""
        try:
            self._state = await self._bulb.get_state()
            self._available = True
        except ZeptrionConnectionError:
            _LOGGER.warning("Turn ON: he Zeptrion bulb is not online")
            self._available = False