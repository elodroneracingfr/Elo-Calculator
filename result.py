#!/usr/bin/env python


class Pilot:
    def __init__(self, licenseId, elo=1500, firstName='n/a', lastName='n/a', callName='n/a'):
        self.licenseId = licenseId
        self.elo = elo
        self.firstName = firstName
        self.lastName = lastName
        selt.callName = callName
        return None
    
    def update_elo(self, elo):
        self.elo = elo
        return None