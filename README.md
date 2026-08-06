# ha-custom-components

Custom Home Assistant components for the thekao.net homelab.

## Components

| Component | Description | Status |
|---|---|---|
| [`hp_climate`](custom_components/hp_climate/) | Climate entity that bridges `input_select.hp_mode` + `input_number.hp_cool_target`/`hp_heat_target` into a standard `climate` entity for thermostat-card UI. Pairs with the `heatpump.yaml` package (see `home-ops-prod`/`talos-ops-prod`). | v1.0.0 — production |

## Install via HACS

1. Add this repo as a custom repository in HACS (Settings → Custom repositories → URL: `lenaxia/ha-custom-components`, category: Integration)
2. Install the component you want
3. Restart Home Assistant
4. Add `climate:` platform config to your `packages/heatpump.yaml` (or `configuration.yaml`):

```yaml
climate:
  - platform: hp_climate
```

## Development

Each component lives in `custom_components/<domain>/` with the standard HA layout (`manifest.json`, `<domain>.py`). Bump `version` in `manifest.json` to release — HACS picks up new versions on its periodic scan.

## Repository conventions

- One component per directory under `custom_components/`
- Semantic versioning per component (independent `version` in each manifest)
- No cross-component dependencies
- Testable in isolation
