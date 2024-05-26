#!/usr/bin/env python

class Pilot:
    def __init__(self, id, licenseNumber, firstName, lastName, pseudo, elo):
        self.id = id
        self.licenseNumber = licenseNumber
        self.firstName = firstName
        self.lastName = lastName
        self.pseudo = pseudo
        self.elo = elo

    def update_elo(self, elo):
        self.elo = elo