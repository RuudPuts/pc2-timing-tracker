from log_messages import log_message
from models import Car, Participant, Track, Lap
from pcars import Packet, TelemetryPacket, ParticipantInfoStringsPacket


class GameState:
    def __init__(self):
        self.driver = None
        self.car = None
        self.track = None

        self.__reset()

    def process_packet(self, packet: Packet):
        if isinstance(packet, TelemetryPacket):
            self.__process_telemetry_packet(packet)
        elif isinstance(packet, ParticipantInfoStringsPacket):
            self.__process_participant_info_packet(packet)
        else:
            print("🔥 Got unknown packet {}".format(packet.__class__.__name__))
            print(packet._data)

        self.__process_lap_time()
        self.__process_participants()

    @property
    def has_telemetry_data(self):
        if self.__last_telemetry_packet:
            return self.last_lap_time \
                   + self.last_lap_time \
                   + self.session_best_lap_time \
                   + self.personal_best_lap_time > 0

        return False

    @property
    def has_player_data(self):
        return self.__last_participants_info_packet is not None

    @property
    def has_participants_data(self):
        return self.participants is not None

    def __reset(self):
        self.__last_telemetry_packet = None
        self.__last_participants_info_packet = None
        self.__current_lap = None

        self.current_lap_number = None
        self.speed = None
        self.current_gear = None
        self.number_of_gears = None

        self.current_lap_time = None
        self.last_lap_time = None
        self.session_best_lap_time = None
        self.personal_best_lap_time = None

        self.laps = []
        self.participants = []

    def __process_telemetry_packet(self, packet: TelemetryPacket):
        if self.__detect_session_change_from_telemetry(packet):
            log_message("[GameState] 🏎  Session change detected in telemetry")
            self.__reset()

        self.__last_telemetry_packet = packet

        self.current_lap_number = packet['participants'][0]['currentLap']
        self.current_lap_valid = packet['lapInvalidated'] is False
        self.speed = packet['speed']
        self.current_gear = packet['gear']
        self.number_of_gears = packet['numGears']

        self.current_lap_time = packet['currentTime']
        self.last_lap_time = packet['lastLapTime']
        self.session_best_lap_time = packet['bestLapTime']
        self.personal_best_lap_time = packet['personalFastestLapTime']

    def __process_participant_info_packet(self, packet: ParticipantInfoStringsPacket):
        if self.__detect_session_change_from_participant_info(packet):
            log_message("[GameState] 🏎  Session change detected in player info")
            self.__reset()

        self.__last_participants_info_packet = packet

        participants = packet['participants']
        self.driver = participants[0]["name"] if len(participants) > 0 else None
        self.car = Car(packet["carName"], packet["carClassName"])
        self.track = Track(packet["trackLocation"], packet["trackVariation"])

    def __detect_session_change_from_telemetry(self, packet: TelemetryPacket):
        if not self.has_telemetry_data:
            return False

        return packet['participants'][0]['currentLap'] < self.current_lap_number

    def __detect_session_change_from_participant_info(self, packet: ParticipantInfoStringsPacket):
        if not self.has_player_data:
            return False

        participants = packet['participants']
        driver_changed = self.driver != participants[0]["name"] if len(participants) > 0 else False
        car_changed = self.car.name != packet["carName"] or self.car.className != packet["carClassName"]
        track_changed = self.track.name != packet["trackLocation"] or self.track.variant != packet["trackVariation"]

        return driver_changed or car_changed or track_changed

    def __process_lap_time(self):
        if len(self.laps) == 0 and self.current_lap_number:
            self.__current_lap = Lap(self.current_lap_number - 1, self.last_lap_time, False)
            self.laps.append(self.__current_lap)
        elif self.__current_lap and self.__current_lap.number != self.current_lap_number:
            self.laps.append(self.__current_lap)

        self.__current_lap = Lap(self.current_lap_number, self.current_lap_time, self.current_lap_valid)

    def __process_participants(self):
        if self.__last_telemetry_packet is None or self.__last_participants_info_packet is None:
            return

        participants_info = self.__last_participants_info_packet["participants"]
        participants_telemetry = self.__last_telemetry_packet["participants"]

        participants = []
        for idx, participant_info in enumerate(participants_info):
            if len(participant_info["name"]) == 0:
                break
            participant_telemetry = participants_telemetry[idx]

            participant_data = {**participant_telemetry, **participant_info}
            participants.append(Participant(
                participant_data["name"],
                participant_data["racePosition"],
                participant_data["currentLap"],
            ))

        self.participants = sorted(participants, key=lambda p: p.position)
