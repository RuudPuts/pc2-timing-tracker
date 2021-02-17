import argparse

from lap_time_sender import LapTimeSender
from game_state import GameState
from packet_receiver import PacketReceiver
from util import sec2time, mps2kph


def parse_launch_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', help='URL of the server to sent data to', required=True)

    return parser.parse_args()


def log_game_state(state: GameState):
    log = []

    if state.has_player_data:
        log.append("Driver {}".format(state.driver))
        log.append("Car    {} [{}]".format(state.car.name, state.car.className))
        log.append("Track  {} [{}]".format(state.track.name, state.track.variant))
        log.append("")
        log.append("")

    if state.has_telemetry_data:
        log.append("Lap    #{}".format(state.current_lap))
        log.append("")
        log.append("Speed  {:.0f} Km/h".format(mps2kph(state.speed)))
        log.append("Gear   {}/{}".format(state.current_gear, state.number_of_gears))
        log.append("")
        log.append("Current lap       {}".format(sec2time(state.current_lap_time)))
        log.append("Last lap          {}".format(sec2time(state.last_lap_time)))
        log.append("Session best lap  {}".format(sec2time(state.session_best_lap_time)))
        log.append("Personal best lap {}".format(sec2time(state.personalBest_lap_time)))
        log.append("")
        log.append("")

    if state.has_participants_data:
        log.append("Leaderboard")
        for participant in state.participants:
            print("{}. {} - Lap {}".format(participant.position, participant.name, participant.current_lap))

    print("\n".join(log))


if __name__ == '__main__':
    launch_arguments = parse_launch_arguments()

    game_state = GameState()
    packet_receiver = PacketReceiver()
    lap_time_sender = LapTimeSender(launch_arguments.server)

    last_sent_lap_time = None

    while True:
        packet = packet_receiver.read_packet()
        game_state.process_packet(packet)
        log_game_state(game_state)

        if game_state.last_lap_time and game_state.last_lap_time != last_sent_lap_time:
            last_sent_lap_time = lap_time_sender.send_lap_time(game_state)
