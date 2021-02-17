# Project Cars 2 lap time  tracker

This project contains a Python 3 client to read from the Project Cars 2 UDP stream and track when a lap has been completed. These laptimes are recorded on the server which can list top times per track.

## Setting up the game
- Select "Options" from the main menu along the top, then select the "System" tile as shown below.
![settings](https://static.wixstatic.com/media/910f3b_bddd4cb723664eefa85692fb009d7816~mv2.jpg "Settings")
- Set "UDP Frequency" to "1" (fastest), or a slower setting if required. If you are experiencing telemetry lag, please try UDP Frequency "4".
- Set "UDP Protocol Version" to "Project CARS 1".
![settings2](https://static.wixstatic.com/media/910f3b_9e8c91d751e54b4f9412d5b004559a4f~mv2.jpg "Settings2")

## Installation

```
$ pip3 install -r requirements.txt
```

## Running the client

```
$ cd client
$ python3 main.py --server [server]
i.e.
$ python3 main.py --server http://localhost:5000
```

This is the application which records the laptimes. It needs a server passed when running on which the laptimes will be stored.
In case sending of laptimes fails it'll cache them locally and sent on the next restart of the application.

## Running the server

```
$ cd server
$ docker-compose up -d 
$ python3 main.py
```

This hosts the webserver to list leaderboards and transmit times to. It stores all data in a Mongo database which can be deployed using `docker-compose`. The webserver will be hosted on port 5000.