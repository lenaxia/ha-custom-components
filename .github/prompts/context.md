# Project Context: ha-custom-components

## What this project is

Custom Home Assistant components for the thekao.net homelab. Each component
lives in `custom_components/<domain>/` with the standard HA layout
(`manifest.json`, `<domain>.py`).

## Components

- **hp_climate** (v1.0.0, production): a `climate` entity that bridges
  `input_select.hp_mode` + `input_number.hp_cool_target` /
  `hp_heat_target` into a standard climate entity for the thermostat-card
  UI. Pairs with the `heatpump.yaml` package in talos-ops-prod/home-ops-prod.
  - `iot_class: local_polling`, `config_flow: false`, no dependencies.
  - Installed via HACS (custom repository, category: Integration).

## Repository conventions

- One component per directory under `custom_components/`
- Semantic versioning per component (independent `version` in each manifest)
- No cross-component dependencies
- Testable in isolation

## Key design constraints

- HA core compatibility matters: a bump in HA core APIs can break custom
  components — check which HA version the component targets.
- `manifest.json` / `hacs.json` schema changes must be validated.
- The `climate` platform contract: expose the standard HA climate services
  and state attributes the thermostat-card expects.
