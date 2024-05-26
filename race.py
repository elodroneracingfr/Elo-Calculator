#!/usr/bin/env python
from datetime import datetime
        
class Race:
    def __init__(self, id, name, date, fileName, weight, multiplier):
        self.id = id
        self.name = name
        self.date = date
        self.fileName = fileName
        self.weight = weight
        self.multiplier = multiplier