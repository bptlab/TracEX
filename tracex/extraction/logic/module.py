import os
from abc import ABC
from pandas import DataFrame


class Module(ABC):
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

    def execute(self) -> DataFrame:
        pass


class ActivityLabeler(Module):
    def execute(self):
        pass


class PreProcessor(Module):
    pass


class TimeExtractor(Module):
    pass


class LocationExtractor(Module):
    pass


class EventTypeClassifier(Module):
    pass


class Visualizer(Module):
    pass
