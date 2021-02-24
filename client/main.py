import argparse

from log_messages import log_message, log_messages
from lap_time_sender import LapTimeSender
from game_state import GameState
from packet_receiver import PacketReceiver
from util import sec2time, mps2kph
from prettytable import PrettyTable


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
        log.append("Lap    #{}".format(state.current_lap_number))
        log.append("")
        log.append("Speed  {:.0f} Km/h".format(mps2kph(state.speed)))
        log.append("Gear   {}/{}".format(state.current_gear, state.number_of_gears))
        log.append("")
        log.append("Current lap       {} ({})".format(sec2time(state.current_lap_time),
                                                      "✅ Valid lap" if state.current_lap_valid else "❌ Invalid lap"))
        log.append("Last lap          {}".format(sec2time(state.last_lap_time)))
        log.append("Session best lap  {}".format(sec2time(state.session_best_lap_time)))
        log.append("Personal best lap {}".format(sec2time(state.personal_best_lap_time)))
        log.append("")
        log.append("")

    if len(state.laps) > 1:
        log.append("Last 5 laps")
        sorted_laps = sorted(state.laps, key=lambda l: l.number)

        table = PrettyTable(['Lap #', 'Time', "Valid"])
        for i in range(0, min(len(sorted_laps), 5)):
            lap = sorted_laps[len(sorted_laps) - 2 - i]
            table.add_row([lap.number, lap.time, "✅ Valid" if lap.is_valid else "❌ Invalid"])
        log.append(table.get_string())
        log.append("")
        log.append("")

    if state.has_participants_data and len(state.participants) > 0 and state.car and state.track:
        log.append("Leaderboard")
        table = PrettyTable(['Position', 'Driver', "In lap"])
        for participant in state.participants:
            table.add_row([participant.position, participant.name, participant.current_lap])
        log.append(table.get_string())
        log.append("")
        log.append("")

    if len(log_messages) > 0:
        log.append("Status messages")
        for i in range(min(len(log_messages), 10)):
            log.append(log_messages[len(log_messages) - 1 - i])
        log.append("")
        log.append("")

    if len(log) > 0:
        while len(log) < 40:
            log.append("")

        print("\n".join(log))


if __name__ == '__main__':
    launch_arguments = parse_launch_arguments()

    game_state = GameState()
    packet_receiver = PacketReceiver()
    lap_time_sender = LapTimeSender(launch_arguments.server)

    last_sent_lap_number = -1

    while True:
        packet = packet_receiver.read_packet()
        game_state.process_packet(packet)

        last_lap = game_state.laps[len(game_state.laps) - 1] if len(game_state.laps) > 0 else None
        if last_lap and last_lap.number != last_sent_lap_number:
            last_sent_lap_number = last_lap.number
            if len(game_state.laps) > 1:
                log_message("[main] 🏁 Lap {} finished - Time {} - Is valid {}"
                            .format(last_lap.number, sec2time(last_lap.time), last_lap.is_valid))
            if last_lap.is_valid:
                lap_time_sender.send_lap_time(game_state)

        log_game_state(game_state)
