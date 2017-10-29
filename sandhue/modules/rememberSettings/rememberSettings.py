from sandhue.api.logging import log
import qhue
import enum
import time
import sys
import requests.exceptions

import sandhue.api.credentials.credentials as credentials
from sandhue.api.credentials.credentials import getName

sys.tracebacklimit = 0 # TODO find another solution.


class LightStatesEnum(enum.Enum):
    UNKNOWN        = 0
    OFF            = 1
    ON             = 2
    JUST_TURNED_ON = 3


def reachable(id, snapshot):
    return snapshot[id]['state']['reachable']


def update_light_state(light_states, light_brightness, snapshot, id):
    light_is_reachable = reachable(id, snapshot)
    if not light_is_reachable and light_states[id] == LightStatesEnum.ON:
        log.info("Light just turned off: %s" % getName(id))
        log.info("Light brightness for '%s'stored: %d" % (getName(id), light_brightness[id]))
        light_states[id] = LightStatesEnum.OFF
    elif not light_is_reachable and light_states[id] != LightStatesEnum.ON:
        light_states[id] = LightStatesEnum.OFF
    elif light_is_reachable and light_states[id] == LightStatesEnum.UNKNOWN:
        light_states[id] = LightStatesEnum.ON
        light_brightness[id] = snapshot[id]['state']['bri']
        log.info("Light on '%s' went from 'unknown' to 'on':" % getName(id))
        log.info("Light brightness for '%s' stored: %d" % (getName(id), light_brightness[id]))
    elif light_is_reachable and light_states[id] == LightStatesEnum.OFF:
        log.info("Light just turned on: %s" % getName(id))
        light_states[id] = LightStatesEnum.JUST_TURNED_ON
    else:  # it is reachable and it was ON, so keep it and save brightness
        light_states[id] = LightStatesEnum.ON
        previous_brightness = light_brightness[id]
        light_brightness[id] = snapshot[id]['state']['bri']
        if previous_brightness != light_brightness[id]:
            log.info("Brightness of '%s' changed to: %d" % (getName(id), light_brightness[id]))


def update_light_states(light_states, light_brightness, snapshot):
    for light in light_states:
        update_light_state(light_states, light_brightness, snapshot, light)


def reset_light_brightness(light_states, light_brightness, id):
    if light_states[id] == LightStatesEnum.JUST_TURNED_ON:
        previous_brightness = light_brightness[id]
        lights[id].state(bri=previous_brightness)
        light_states[id] = LightStatesEnum.ON
        log.info("Just reset brightness of %s to: %d" % (id, previous_brightness))


def reset_all_light_brightnesses(light_states, light_brightness):
    for light in light_states:
        reset_light_brightness(light_states, light_brightness, light)


if __name__ == "__main__":
    b = qhue.Bridge(credentials.BRIDGE_IP, credentials.USERNAME)
    lights = b.lights

    light_states = {}
    for light in lights():
        light_states[light] = LightStatesEnum.UNKNOWN
    light_brightness = {}
    for light in lights():
        light_brightness[light] = -1

    while True:
        try:
            snapShot = lights()
            update_light_states(light_states, light_brightness, snapShot)
            reset_all_light_brightnesses(light_states, light_brightness)

        except requests.exceptions.ChunkedEncodingError as e:
            log.exception("ChunkedEncodingError")

        except Exception as e:
            log.exception("An exception occurred")
            log.exception("type(e):    %s" % str(type(e)))
            log.exception("e.args:     %s" % str(e.args))
            log.exception("e:          %s" % str(e))

        time.sleep(0.2)
