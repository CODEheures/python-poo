from __future__ import annotations
import json
import math
import matplotlib.pyplot as plt

class Position:
    def __init__(self, latitude_degrees: float, longitude_degrees: float):
        self.latitude_degrees = latitude_degrees
        self.longitude_degrees = longitude_degrees

    @property
    def longitude(self):
        # Longitude in radians
        return self.longitude_degrees * math.pi / 180

    @property
    def latitude(self):
        # Latitude in radians
        return self.latitude_degrees * math.pi / 180

class Agent:
    def __init__(self, position: Position, **agent_attributes):
        self.position = position
        for attr_name, attr_value in agent_attributes.items():
            setattr(self, attr_name, attr_value)

class Zone:
    ZONES = []
    MIN_LATITUDE_DEGREES = -90
    MAX_LATITUDE_DEGREES = 90
    STEP_LATITUDE_DEGREES = 1
    MIN_LONGITUDE_DEGREES = -180
    MAX_LONGITUDE_DEGREES = 180
    STEP_LONGITUDE_DEGREES = 1
    EARTH_RADIUS_KILOMETERS = 6371

    def __init__(self, corner1, corner2):
        self.corner1 = corner1
        self.corner2 = corner2
        self.agents = []

    def add_agent(self, agent: Agent):
        self.agents.append(agent)

    @classmethod
    def __width(cls):
        return cls.STEP_LONGITUDE_DEGREES * math.pi/180 * cls.EARTH_RADIUS_KILOMETERS

    @classmethod
    def __height(cls):
        return cls.STEP_LATITUDE_DEGREES * math.pi / 180 * cls.EARTH_RADIUS_KILOMETERS

    @classmethod
    def area(cls):
        return cls.__width()*cls.__height()

    @property
    def density(self):
        return self.population / self.area()

    @property
    def agreeableness(self):
        if self.population == 0:
            return 0

        return sum([agent.agreeableness  for agent in self.agents]) / self.population

    @property
    def population(self):
        return len(self.agents)

    @classmethod
    def _initialize(cls):
        for latitude in range(cls.MIN_LATITUDE_DEGREES, cls.MAX_LATITUDE_DEGREES, cls.STEP_LATITUDE_DEGREES):
            for longitude in range(cls.MIN_LONGITUDE_DEGREES, cls.MAX_LONGITUDE_DEGREES, cls.STEP_LONGITUDE_DEGREES):
                bottom_left_corner = Position(longitude, latitude)
                top_right_corner = Position(longitude + cls.STEP_LONGITUDE_DEGREES, latitude + cls.STEP_LATITUDE_DEGREES)
                zone = Zone(bottom_left_corner, top_right_corner)
                cls.ZONES.append(zone)

    @classmethod
    def get_zone_by_position(cls, position: Position) -> Zone:
        if len(cls.ZONES) == 0:
            cls._initialize()
        longitude_index = int((position.longitude_degrees - cls.MIN_LONGITUDE_DEGREES) / cls.STEP_LONGITUDE_DEGREES)
        latitude_index = int((position.latitude_degrees - cls.MIN_LATITUDE_DEGREES) / cls.STEP_LATITUDE_DEGREES)
        longitude_bins = int(
            (cls.MAX_LONGITUDE_DEGREES - cls.MIN_LONGITUDE_DEGREES) / cls.STEP_LONGITUDE_DEGREES)  # 180-(-180) / 1
        zone_index = latitude_index * longitude_bins + longitude_index
        zone = cls.ZONES[zone_index]
        return zone

class BaseGraph:
    def __init__(self):
        self.title = "Your graph title"
        self.x_label = "X axis label"
        self.y_label = "Y axis label"
        self.show_grid = True

    def xy_values(self, zones: [Zone]):
        raise NotImplementedError

    def show(self, zones: [Zone]):
        plt.title(self.title)
        plt.xlabel(self.x_label)
        plt.ylabel(self.y_label)
        plt.grid(self.show_grid)
        x_values, y_values = self.xy_values(zones)
        plt.plot(x_values, y_values, '.')
        plt.show()

class AgreeablenessGraph(BaseGraph):
    def __init__(self):
        super().__init__()
        self.title = "Agreeableness"
        self.x_label = "density"
        self.y_label = "agreeableness"

    def xy_values(self, zones: [Zone]):
        x_values = [zone.density for zone in zones]
        y_values = [zone.agreeableness for zone in zones]
        return x_values, y_values


def main():
    with open("agents-100k.json") as file:
        agents = json.load(file)
        for attributes in agents:
            latitude_degrees = attributes.pop('latitude')
            longitude_degrees = attributes.pop('longitude')
            position = Position(latitude_degrees, longitude_degrees)
            agent = Agent(position, **attributes)
            zone_agent = Zone.get_zone_by_position(position)
            zone_agent.add_agent(agent)

    agreeablenessGraph = AgreeablenessGraph()
    agreeablenessGraph.show(Zone.ZONES)


if __name__ == "__main__":
    main()