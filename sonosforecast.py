#!/usr/bin/env python
# Plays BBC Radio 4 on my sonos for a specified duration, then restores
# the sonos state to what it was before.
#
# Used to always play the shipping forecast, by cronning it to run at
# 0048, for a duration of 12 minutes, until the radio 4 shutdown at 0100.
#
# Dogger, Fisher, German Bight...
#
import sys
import time
import soco

# Where to play, and how loud
ZONES_AND_VOLUMES = {
    'Office': 15,
    'Master Bedroom': 12
}


def get_state(device):
    current_state = device.get_current_transport_info().get("current_transport_state")
    track_info = device.get_current_track_info()
    playlist_position = int(track_info["playlist_position"]) - 1
    position = track_info["position"]
    title = track_info["title"]
    print "Current state in %s is %s playing %s at position %s at %s" % (device.player_name, current_state, title, playlist_position, position)
    return {'playback_state': current_state,
            'playlist_pos': playlist_position,
            'seek_pos': position,
            'volume': device.volume}


def restore_state(device, state):
    device.play_from_queue(state['playlist_pos'])
    device.seek(state['seek_pos'])
    if state['playback_state'] == "PAUSED_PLAYBACK":
        device.pause()
    elif state['playback_state'] != "PLAYING":
        device.stop()
    device.volume = state['volume']


def find_station(z, title):
    # NB: doesn't handle pagination, assumes its in first page:
    return [r for r in z.get_favorite_radio_stations()['favorites'] if r['title'] == title][0]


def play_station(z, station):
    meta_template = """
    <DIDL-Lite xmlns:dc="http://purl.org/dc/elements/1.1/"
        xmlns:upnp="urn:schemas-upnp-org:metadata-1-0/upnp/"
        xmlns:r="urn:schemas-rinconnetworks-com:metadata-1-0/"
        xmlns="urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/">
        <item id="R:0/0/0" parentID="R:0/0" restricted="true">
            <dc:title>{title}</dc:title>
            <upnp:class>object.item.audioItem.audioBroadcast</upnp:class>
            <desc id="cdudn" nameSpace="urn:schemas-rinconnetworks-com:metadata-1-0/">
                {service}
            </desc>
        </item>
    </DIDL-Lite>' """

    tunein_service = 'SA_RINCON65031_'
    # TODO seems at least & needs to be escaped - should move this to
    # play_uri and maybe escape other chars.
    uri = station['uri'].replace('&', '&amp;')
    metadata = meta_template.format(title=station['title'], service=tunein_service)
    return z.play_uri(uri, metadata)


def find_controller(name):
    for s in list(soco.discover()):
        if s.player_name != name:
            continue
        ip = s.group.coordinator.ip_address
        return soco.SoCo(ip)
    return None


if __name__ == "__main__":
    initial_states = {}

    for zname in ZONES_AND_VOLUMES:
        z = find_controller(zname)
        initial_states[zname] = get_state(z)
        r4 = find_station(z, "BBC Radio 4")
        print "Playing Radio 4 in %s" % zname
        play_station(z, r4)
        z.volume = ZONES_AND_VOLUMES[zname]

    # The shipping forecast is typically on between 0048 and 0100 (12 minutes)
    duration = 12 * 60
    if len(sys.argv) == 2:
        duration = int(sys.argv[1])
    print "Waiting %d seconds..." % duration
    time.sleep(duration)

    for zname in ZONES_AND_VOLUMES:
        z = find_controller(zname)
        print "Restoring state in %s" % zname
        restore_state(z, initial_states[zname])
