"""Heat Pump climate entity - bridges input_select/input_number to climate domain."""

import logging
from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
    HVACAction,
)
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.helpers.entity import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.restore_state import RestoreEntity

_LOGGER = logging.getLogger(__name__)

DOMAIN = "hp_climate"

INDOOR_SENSOR = "sensor.hp_indoor_temperature_averaged"
MODE_SELECT = "input_select.hp_mode"
COOL_TARGET = "input_number.hp_cool_target"
HEAT_TARGET = "input_number.hp_heat_target"
COOL_DEMAND = "switch.hp_cool_demand"
HEAT_DEMAND = "switch.hp_heat_demand"


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    async_add_entities([HeatPumpClimate(hass)])


class HeatPumpClimate(ClimateEntity, RestoreEntity):
    _attr_name = "Heat Pump"
    _attr_unique_id = "heat_pump_climate"
    _attr_temperature_unit = UnitOfTemperature.FAHRENHEIT
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.COOL, HVACMode.HEAT]
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )
    _attr_min_temp = 55
    _attr_max_temp = 82
    _attr_target_temperature_step = 1

    def __init__(self, hass):
        self.hass = hass
        self._attr_current_temperature = None
        self._attr_target_temperature = None
        self._attr_hvac_mode = HVACMode.OFF
        self._attr_hvac_action = HVACAction.IDLE

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        self._update_state()

        @callback
        def _state_changed(event):
            self._update_state()
            self.async_write_ha_state()

        tracked = [
            INDOOR_SENSOR,
            MODE_SELECT,
            COOL_TARGET,
            HEAT_TARGET,
            COOL_DEMAND,
            HEAT_DEMAND,
        ]
        self.async_on_remove(
            async_track_state_change_event(self.hass, tracked, _state_changed)
        )

    @callback
    def _update_state(self):
        self._attr_current_temperature = self._to_float(
            self.hass.states.get(INDOOR_SENSOR)
        )
        mode_state = self.hass.states.get(MODE_SELECT)
        mode = mode_state.state if mode_state else "off"
        self._attr_hvac_mode = {
            "off": HVACMode.OFF,
            "cool": HVACMode.COOL,
            "heat": HVACMode.HEAT,
        }.get(mode, HVACMode.OFF)

        if mode == "heat":
            self._attr_target_temperature = self._to_float(
                self.hass.states.get(HEAT_TARGET)
            )
        else:
            self._attr_target_temperature = self._to_float(
                self.hass.states.get(COOL_TARGET)
            )

        cool_on = self.hass.states.is_state(COOL_DEMAND, "on")
        heat_on = self.hass.states.is_state(HEAT_DEMAND, "on")
        if cool_on:
            self._attr_hvac_action = HVACAction.COOLING
        elif heat_on:
            self._attr_hvac_action = HVACAction.HEATING
        else:
            self._attr_hvac_action = HVACAction.IDLE

    @staticmethod
    def _to_float(state):
        if state is None or state.state in ("unknown", "unavailable", None):
            return None
        try:
            return float(state.state)
        except (ValueError, TypeError):
            return None

    async def async_set_hvac_mode(self, hvac_mode):
        mode_map = {HVACMode.OFF: "off", HVACMode.COOL: "cool", HVACMode.HEAT: "heat"}
        option = mode_map.get(hvac_mode, "off")
        await self.hass.services.async_call(
            "input_select",
            "select_option",
            {"entity_id": MODE_SELECT, "option": option},
        )

    async def async_set_temperature(self, **kwargs):
        temp = kwargs.get(ATTR_TEMPERATURE)
        if temp is None:
            return
        mode_state = self.hass.states.get(MODE_SELECT)
        mode = mode_state.state if mode_state else "off"
        target = HEAT_TARGET if mode == "heat" else COOL_TARGET
        await self.hass.services.async_call(
            "input_number", "set_value", {"entity_id": target, "value": float(temp)}
        )

    async def async_turn_on(self):
        await self.async_set_hvac_mode(HVACMode.COOL)

    async def async_turn_off(self):
        await self.async_set_hvac_mode(HVACMode.OFF)
