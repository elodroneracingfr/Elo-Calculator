import sqlite3
from race import Race
from pilot import Pilot
from race_result import RaceResult

class Database:
    def __init__(self):
        return
        
    def create(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.create_tables()
    
    def create_tables(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS race
                     (id INTEGER PRIMARY KEY, name TEXT, date DATE, fileName TEXT, weight INTEGER, multiplier INTEGER)''')
        c.execute('''CREATE TABLE IF NOT EXISTS pilot
                     (id INTEGER PRIMARY KEY, licenseNumber TEXT, firstName TEXT, lastName TEXT, pseudo TEXT, elo INTEGER)''')
        c.execute('''CREATE TABLE IF NOT EXISTS race_result
                     (id INTEGER PRIMARY KEY, race_id INTEGER, pilot_id INTEGER, rank INTEGER,
                     FOREIGN KEY(race_id) REFERENCES race(id),
                     FOREIGN KEY(pilot_id) REFERENCES pilot(id))''')
        self.conn.commit()

    def add_race(self, race):
        c = self.conn.cursor()
        c.execute("INSERT INTO race ( name, date, fileName, weight, multiplier) VALUES (?, ?, ?, ?, ?)", (race.name, race.date, race.fileName, race.weight, race.multiplier))
        self.conn.commit()

    def add_pilot(self, pilot):
        c = self.conn.cursor()
        c.execute("INSERT INTO pilot (licenseNumber, firstName, lastName, pseudo, elo) VALUES (?, ?, ?, ?, ?)",
                  (pilot.licenseNumber, pilot.firstName, pilot.lastName, pilot.pseudo, pilot.elo))
        self.conn.commit()

    def add_race_result(self, race_result):
        c = self.conn.cursor()
        c.execute("INSERT INTO race_result (race_id, pilot_id, rank) VALUES (?, ?, ?)",
                  (race_result.race.id, race_result.pilot.id, race_result.rank))
        self.conn.commit()

    def get_race_by_name_and_date(self, name, date):
        c = self.conn.cursor()
        c.execute("SELECT * FROM race WHERE name = ? AND date = ?", (name, date))
        row = c.fetchone()
        if row is not None:
            return Race(*row)
            
    def update_all_races_weight(self, weight):
        c = self.conn.cursor()
        c.execute(f"UPDATE race SET weight = {weight}")
        self.conn.commit()

    def update_race_weight(self, race, weight):
        c = self.conn.cursor()
        c.execute("UPDATE race SET weight = ? WHERE id = ?", (weight, race.id))
        self.conn.commit()
        d = self.conn.cursor()
        d.execute(f"SELECT * FROM race WHERE id = {race.id}")
        row = d.fetchone()
        if row is not None:
            return Race(*row)

    def update_race_multiplier(self, race, multiplier):
        c = self.conn.cursor()
        c.execute("UPDATE race SET multiplier = ? WHERE id = ?", (multiplier, race.id))
        self.conn.commit()
        d = self.conn.cursor()
        d.execute(f"SELECT * FROM race WHERE id = {race.id}")
        row = d.fetchone()
        if row is not None:
            return Race(*row)

    def get_all_races_by_date(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM Race ORDER BY date ASC")
        rows = c.fetchall()
        return [Race(*row) for row in rows]

    def get_sorted_race_results_per_race(self, raceId):
        c = self.conn.cursor()
        c.execute("SELECT * FROM race_result WHERE race_id = ? ORDER BY rank ASC", (raceId,))
        rows = c.fetchall()
        return [RaceResult(*row) for row in rows]

    def get_pilot_by_id(self, id):
        c = self.conn.cursor()
        c.execute("SELECT * FROM pilot WHERE id = ?", (id,))
        row = c.fetchone()
        if row is not None:
            return Pilot(*row)

    def get_pilot_by_licenseNumber(self, licenseNumber):
        c = self.conn.cursor()
        c.execute("SELECT * FROM pilot WHERE licenseNumber = ?", (licenseNumber,))
        row = c.fetchone()
        if row is not None:
            return Pilot(*row)
        
    def get_avg_pilots_elo_per_race(self, race):
        c = self.conn.cursor()
        c.execute("SELECT AVG(pilot.elo) from pilot WHERE pilot.id IN (SELECT pilot_id FROM race_result WHERE race_id = ?)", (race.id,))
        row = c.fetchone()
        if row is not None:
            return int(*row)

    def get_all_pilots_by_rank(self, numberOfRaces):
        query = f"SELECT * FROM pilot WHERE pilot.id IN ( SELECT pilot_id FROM race_result GROUP BY pilot_id HAVING COUNT(DISTINCT race_id) >= {numberOfRaces}) ORDER BY elo DESC;"
        c = self.conn.cursor()
        c.execute(query)
        rows = c.fetchall()
        return [Pilot(*row) for row in rows]

    def update_pilot_elo(self, pilot_id, new_elo):
        c = self.conn.cursor()
        c.execute("UPDATE pilot SET elo = ? WHERE id = ?", (new_elo, pilot_id))
        self.conn.commit()

    def close(self):
        self.conn.close()
