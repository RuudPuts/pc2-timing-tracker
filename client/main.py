import requests
import socket
import time
import json
from io import BytesIO
from lib import Packet, TelemetryPacket, ParticipantInfoStringsPacket
from util import sec2time, mps2kph
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', help='URL of the server to sent data to', required=True)
    args = parser.parse_args()
    server_host = args.server

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", 5606))

    print("Server started, waiting for data...")

    last_received_lap_time = None
    last_sent_lap_time = None
    telemetry_packet = None
    participant_info_packet = None
    additional_participant_info_packet = None

    while True:
        data, address = sock.recvfrom(1500)

        packet = Packet.read_from(BytesIO(data))
        # print(packet._data)

        if isinstance(packet, TelemetryPacket):
            telemetry_packet = packet
        elif isinstance(packet, ParticipantInfoStringsPacket):
            participant_info_packet = packet
        else:
            print("🔥 Got unknown packet {}".format(packet.__class__.__name__))
            print(packet._data)

        print("")
        print("")

        # print("Driver {}".format(packet['currentTime']))
        if participant_info_packet is not None:
            print("Driver {}".format(participant_info_packet['participants'][0]["name"]))
            print("Car    {} [{}]".format(participant_info_packet['carName'], participant_info_packet['carClassName']))
            print("Track  {} ({})".format(participant_info_packet['trackLocation'], participant_info_packet['trackVariation']))
        else:
            print("Driver")
            print("Car")
            print("Track")

        if telemetry_packet is not None:
            last_received_lap_time = telemetry_packet['lastLapTime']
            print("Lap    #{}".format(telemetry_packet['participants'][0]['currentLap']))
            print("")
            print("Speed  {:.0f} Km/h".format(mps2kph(telemetry_packet['speed'])))
            print("Gear   {}/{}".format(telemetry_packet['gear'], telemetry_packet['numGears']))
            print("")
            print("Current lap       {}".format(sec2time(telemetry_packet['currentTime'])))
            print("Last lap          {}".format(sec2time(telemetry_packet['lastLapTime'])))
            print("Session best lap  {}".format(sec2time(telemetry_packet['bestLapTime'])))
            print("Personal best lap {}".format(sec2time(telemetry_packet['personalFastestLapTime'])))

        if participant_info_packet is not None and telemetry_packet is not None:
            telemetry_participants = telemetry_packet["participants"]
            participant_info_participants = participant_info_packet["participants"]

            print("")

            participants = []

            for idx, part_info in enumerate(participant_info_participants):
                part_tel = telemetry_participants[idx]
                participants.append({**part_tel, **part_info})

            participants = sorted(participants, key=lambda p: p['racePosition'])

            print("Leaderboard")
            for part in participants:
                print("{}. {} - Lap {}".format(part["racePosition"], part["name"], part["currentLap"]))

        if participant_info_packet is not None and last_received_lap_time is not None:
            if last_sent_lap_time is None:
                last_sent_lap_time = last_received_lap_time
                continue
            elif last_received_lap_time != last_sent_lap_time:
                last_sent_lap_time = last_received_lap_time

                data = json.dumps({
                    'date': time.time(),
                    'driver': participant_info_packet['participants'][0]["name"],
                    'track': {
                        'name': participant_info_packet['trackLocation'],
                        'variant': participant_info_packet['trackVariation'],
                    },
                    'car': {
                        'name': participant_info_packet['carName'],
                        'class': participant_info_packet['carClassName'],
                    },
                    'time': last_received_lap_time,
                    'session_type': 'time-trial' if len(participant_info_packet["participants"]) == 1 else 'race'
                })
                requests.post('{}/laptime/submit'.format(server_host), data=data)



