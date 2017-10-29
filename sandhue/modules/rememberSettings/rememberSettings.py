import qhue
import enum
import time

import sandhue.api.credentials.credentials as credentials


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
        print "Light just turned off:", id
        print "Light brightness stored:", light_brightness[id]
        print ""
        light_states[id] = LightStatesEnum.OFF
    elif not light_is_reachable and light_states[id] != LightStatesEnum.ON:
        light_states[id] = LightStatesEnum.OFF
    elif light_is_reachable and light_states[id] == LightStatesEnum.UNKNOWN:
        light_states[id] = LightStatesEnum.ON
        light_brightness[id] = snapshot[id]['state']['bri']
        print "Light went from 'unknown' to 'on':", id
        print "Light brightness stored:", light_brightness[id]
        print ""
    elif light_is_reachable and light_states[id] == LightStatesEnum.OFF:
        print "Light just turned on:", id
        print ""
        light_states[id] = LightStatesEnum.JUST_TURNED_ON
    else:  # it is reachable and it was ON, so keep it and save brightness
        light_states[id] = LightStatesEnum.ON
        previous_brightness = light_brightness[id]
        light_brightness[id] = snapshot[id]['state']['bri']
        if previous_brightness != light_brightness[id]:
            print "Brightness of", id, "changed to:", light_brightness[id]
            print ""


def update_light_states(light_states, light_brightness, snapshot):
    for light in light_states:
        update_light_state(light_states, light_brightness, snapshot, light)


def reset_light_brightness(light_states, light_brightness, id):
    if light_states[id] == LightStatesEnum.JUST_TURNED_ON:
        previous_brightness = light_brightness[id]
        lights[id].state(bri=previous_brightness)
        light_states[id] = LightStatesEnum.ON
        print "Jus reset brightness of", id, "to:", previous_brightness
        print ""


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

            # for light in lights():
            #     print "state of light", light, ":", light_states[light]
            #     print "brightness of light", light, ":", light_brightness[light]
            # print
            # print
            # print
        except Exception as e:
            print "An exception occurred"
            print "type(e):    ", type(e)
            print "e.args:     ", e.args
            print "e:          ", e

        time.sleep(0.2)
