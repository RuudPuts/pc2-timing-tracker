# Project Cars 2 lap time  tracker

This project contains a Python 3 client to read from the Project Cars 2 UDP stream and track when a lap has been completed. These laptimes are recorded on the server which can list top times per track.

## Installation

```
$ pip3 install -r requirements.txt
```

## Client

```
python3 client.py
```

This is the application which records the laptimes. It needs a server passed when running on which the laptimes will be stored.
In case sending of laptimes fails it'll cache them locally and sent on the next restart of the application.

## Server

```
docker-compose up -d 
python3 server.py
```

This hosts the webserver to list leaderboards and transmit times to. It stores all data in a Mongo database which can be deployed using `docker-compose`.