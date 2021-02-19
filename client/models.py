class Car:
    def __init__(self, name: str, className: str):
        self.name = name
        self.className = className

    def to_json(self):
        return {
            "name": self.name,
            "class": self.className
        }


class Participant:
    def __init__(self, name: str, position: int, current_lap: int):
        self.name = name
        self.position = position
        self.current_lap = current_lap


class Lap:
    def __init__(self, number: int, time: int, is_valid: bool):
        self.number = number
        self.time = time
        self.is_valid = is_valid


class Track:
    def __init__(self, name: str, variant: str):
        self.name = name
        self.variant = variant

    def to_json(self):
        return {
            "name": self.name,
            "variant": self.variant
        }
