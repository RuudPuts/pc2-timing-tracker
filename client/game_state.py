from models import Car, Participant, Track
from pcars import Packet, TelemetryPacket, ParticipantInfoStringsPacket


class GameState:
    def __init__(self):
        self.__last_telemetry_packet = None
        self.__last_participants_info_packet = None

        self.driver = None
        self.car = None
        self.track = None

        self.current_lap = None
        self.speed = None
        self.current_gear = None
        self.number_of_gears = None

        self.current_lap_time = None
        self.last_lap_time = None
        self.session_best_lap_time = None
        self.personal_best_lap_time = None

        self.participants = []

    def process_packet(self, packet: Packet):
        if isinstance(packet, TelemetryPacket):
            self.__process_telemetry_packet(packet)
        elif isinstance(packet, ParticipantInfoStringsPacket):
            self.__process_participant_info_packet(packet)
        else:
            print("🔥 Got unknown packet {}".format(packet.__class__.__name__))
            print(packet._data)

        self.__process_participants()

    @property
    def has_telemetry_data(self):
        return self.__last_telemetry_packet is not None

    @property
    def has_player_data(self):
        return self.__last_participants_info_packet is not None

    @property
    def has_participants_data(self):
        return self.participants is not None

    def __process_telemetry_packet(self, packet: TelemetryPacket):
        self.__last_telemetry_packet = packet

        self.current_lap = packet['participants'][0]['currentLap']
        self.speed = packet['speed']
        self.current_gear = packet['gear']
        self.number_of_gears = packet['numGears']

        self.current_lap_time = packet['currentTime']
        self.last_lap_time = packet['lastLapTime']
        self.session_best_lap_time = packet['bestLapTime']
        self.personal_best_lap_time = packet['personalFastestLapTime']

    def __process_participant_info_packet(self, packet: ParticipantInfoStringsPacket):
        self.__last_participants_info_packet = packet

        participants = packet['participants']
        self.driver = participants[0]["name"] if len(participants) > 0 else None
        self.car = Car(packet["carName"], packet["carClassName"])
        self.track = Car(packet["trackLocation"], packet["trackVariation"])

    def __process_participants(self):
        if self.__last_telemetry_packet is None or self.__last_participants_info_packet is None:
            return

        participants_info = self.__last_participants_info_packet["participants"]
        participants_telemetry = self.__last_telemetry_packet["participants"]

        participants = []
        for idx, participant_info in enumerate(participants_info):
            participant_telemetry = participants_telemetry[idx]

            participant_data = {**participant_telemetry, **participant_info}
            participants.append(Participant(
                participant_data["name"],
                participant_data["racePosition"],
                participant_data["currentLap"],
            ))

        self.participants = sorted(participants, key=lambda p: p.position)


