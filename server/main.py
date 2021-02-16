from bson import ObjectId
from flask import Flask, Response, request, render_template
from flask_bootstrap import Bootstrap
from mongoengine import DoesNotExist

from database import *
from util import sec2time, sec2date

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'connect': False,
    'host': 'mongodb://mongo:password@localhost/timing_tracker?authSource=admin'
}
initialize_db(app)
bootstrap = Bootstrap(app)


class LeaderboardEntry:
    def __init__(self, rank: int, driver: Driver, car: Car, time: str, recorded_at: str):
        self.rank = rank
        self.driver = driver
        self.car = car
        self.time = time
        self.recorded_at = recorded_at


class Leaderboard:
    def __init__(self, track: Track, entries: [LeaderboardEntry]):
        self.track = track
        self.entries = entries


@app.route("/")
def index():
    leaderboards = []
    for track in Track.objects().order_by('name'):
        best_time_per_driver = LapTime.objects(track=track).aggregate([
            {
                "$group": {
                    "_id": "$driver",
                    "time": {
                        "$min": "$time"
                    }
                }
            },
            {
                "$sort": {"time": 1}
            }
        ])

        best_track_lap_times = map(lambda driver_time:
                                   LapTime.objects(track=track, driver=ObjectId(driver_time["_id"]),
                                                   time=driver_time["time"])[0], best_time_per_driver)

        leaderboard_entries = []
        for idx, lap_time in enumerate(best_track_lap_times):
            leaderboard_entries.append(LeaderboardEntry(idx + 1, lap_time.driver, lap_time.car,
                                                        sec2time(lap_time.time), sec2date(lap_time.recorded_at)))

        leaderboards.append(Leaderboard(track, leaderboard_entries))

    return render_template('index.html', leaderboards=leaderboards)


@app.route("/laptimes")
def get_lap_times():
    print(LapTime.objects().select_related())
    return Response(LapTime.objects().to_json(), mimetype='application/json')


@app.route("/laptime/submit", methods=['POST'])
def submit_lap_time():
    data = request.get_json()

    data_driver = data["driver"]
    data_car_name = data["car"]["name"]
    data_car_class = data["car"]["class"]
    data_track_name = data["track"]["name"]
    data_track_variant = data["track"]["variant"]
    data_session_type = data["session_type"]
    data_recorded_at = data["date"]
    data_lap_time = data["time"]

    print("Receiving lap time...")

    # Fetch or store driver
    try:
        driver = Driver.objects.get(name=data_driver)
    except DoesNotExist:
        driver = Driver(name=data_driver).save()

    print(driver.to_json())

    # Fetch or store car
    try:
        car = Car.objects.get(name=data_car_name, type=data_car_class)
    except DoesNotExist:
        car = Car(name=data_car_name, type=data_car_class).save()

    print(car.to_json())

    # Fetch or store track
    try:
        track = Track.objects.get(name=data_track_name, variant=data_track_variant)
    except DoesNotExist:
        track = Track(name=data_track_name, variant=data_track_variant).save()

    print(track.to_json())

    # Fetch or store time
    try:
        lap_time = LapTime.objects.get(driver=driver, car=car, track=track,
                                       session_type=data_session_type, recorded_at=data_recorded_at)
    except DoesNotExist:
        lap_time = LapTime(driver=driver, car=car, track=track, time=data_lap_time,
                           session_type=data_session_type, recorded_at=data_recorded_at).save()

    print(lap_time.to_json())

    return Response(None, mimetype='application/json')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
