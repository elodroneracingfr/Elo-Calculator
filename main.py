#!/usr/bin/env python
# ELO CALCULATOR v. 2.0
# Author - Groupe Drone Sport FFAM
# TOOL FOR CALCULATING SEASONAL DRONE RACING RANKINGS

# TODO:

# v.2.0
# - Initial Github Release

# v.1.3
# - Added Export method default MD format for readme. Additional CSV is available JSON left to do 
# - Readme file created
# - Add option to set race Multiplier (FAI, Finals, ...) 

# v.1.2
# - Added Race Weight
# - Added Loss Limiter
# - Added Minimum number of races for rankings 
# - Added race.multiplier

# v.1.1
# - Added Menu with options
# - Added option to add one or multiple races at a time
# - Added option to list races

# v.1.0
# - Initial Release

# v.0.1
# - Initial creation

from pilot import Pilot
from race import Race
from race_result import RaceResult
from database import Database

import csv
import logging
import os
import argparse
import re
from datetime import datetime

########################################################################
# GLOBAL VARIABLES
########################################################################
VERSION = "2.0"
LOG_FILE = "elo.log"
EXPECTED_HEADERS = ['Rank', 'LicenseNumber', 'FirstName', 'LastName', 'Pseudo']

# ELO CALCULATOR BASE SETTINGS
MIN_NUM_RACES = 3
BASE_ELO = 1500
K_FACTOR = 20
# ELO CALCULATOR ADDITIONAL SETTINGS
USE_RACE_WEIGHT = False
RACE_WEIGHT_MAX_MULTIPLIER = 3
USE_LOSS_LIMITER = False
LOSS_LIMITER_DIVIDER = 2

# DATABASE
DB_NAME = 'database.db'
db = Database()

########################################################################
# FILE FUNCTIONS AND UTILS
########################################################################
# Define a function to log messages to the console and a log file
def log_message(msg, printToConsole=True):
    if printToConsole:
        print(msg)
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.debug(f"[{date}] {msg}")

# Get a sorted list of all CSV files in the results folder
def list_files_in_dir(path, fileFormat):
    fileNames = sorted([f for f in os.listdir(path) if f.endswith("."+fileFormat)])
    return fileNames

# Read the race results from a file
def read_race_results(folderPath, fileName, inputFormat):
    file = folderPath + '\\' + fileName
    if (inputFormat == 'csv'):
        with open(file, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            
            if reader.fieldnames != EXPECTED_HEADERS:
                raise ValueError(f"Unexpected headers: {reader.fieldnames}. Expected headers: {EXPECTED_HEADERS}")
            
            # Get RaceName and RaceDate from file name
            # File name format : YEAR-MONTH-DAY-RACE_NAME.csv
            # Check name format with regex \d{4}-\d{2}-\d{2}-[a-zA-Z\_]{3,}
            if not re.match(r'\d{4}-\d{2}-\d{2}-[a-zA-Z\_]{3,}', fileName):
                raise ValueError(f"Invalid file name format: {fileName}, Expected format: YEAR-MONTH-DAY-RACE_NAME.csv")
                return

            raceName = fileName.split('-')[3].split('.')[0]
            raceDate = datetime(int(fileName.split('-')[0]), int(fileName.split('-')[1]), int(fileName.split('-')[2]))
            # Format the date as day/month/year
            #raceDate = raceDate.strftime("%d/%m/%Y")
            
            data = {}
            data['FileName'] = fileName
            data['RaceName'] = raceName
            data['RaceDate'] = raceDate
            data['result'] = []

            for row in reader:
                if (row['LicenseNumber'] == '' or row['Rank'] == '' ): 
                    log_message(f"Missing required field in row: {row}")
                    continue
                else :
                    data['result'].append({
                        'FirstName': row['FirstName'],
                        'LastName': row['LastName'],
                        'Pseudo': row['Pseudo'],
                        'LicenseNumber': row['LicenseNumber'],
                        'Rank': row['Rank']
                    })
        return data
    
    elif (inputFormat == 'json'):
        print('TODO : IMPLEMENT PROPER HANDLING')
        return
    
    else : 
        print('TODO : IMPLEMENT PROPER HANDLING')
        return
    
# Scale a value from one range to another
# src = [min, max] of the source range
# dst = [min, max] of the destination range
# Output can't be bellow dst min value
def scale(val, src, dst):
    diff = val - src[0]
    if diff < 0:
        diff = 0
    return ((diff) / (src[1]-src[0])) * (dst[1]-dst[0]) + dst[0]

########################################################################
# DATABASE FUNCTIONS
########################################################################
# Get or create a race in the database based on the name and date
def get_or_create_race(name, date, fileName):
    race = db.get_race_by_name_and_date(name, date)
    if(race):
        return race
    else:
        race = Race('', name, date, fileName, 1500, 1)
        db.add_race(race)
        race = db.get_race_by_name_and_date(name, date)
        return race
        
def update_race_multiplier(race, multiplier):
    db.update_race_multiplier(race, multiplier)
    return

# Get or create a pilot in the database based on the license number
def get_or_create_pilot(firstName, lastName, pseudo, licenseNumber):
    pilot = db.get_pilot_by_licenseNumber(licenseNumber)
    if(pilot):
        return pilot
    else:
        pilot = Pilot('',licenseNumber, firstName, lastName, pseudo, BASE_ELO)
        db.add_pilot(pilot)
        pilot = db.get_pilot_by_licenseNumber(licenseNumber)
        return pilot

# Update the database with race results
def update_db_with_race_results(data):
    race = get_or_create_race(data["RaceName"], data['RaceDate'].date(), data['FileName'])
        
    for result in data['result']:
        pilot = get_or_create_pilot(result['FirstName'], result['LastName'], result['Pseudo'], result['LicenseNumber'])
        raceResult = RaceResult('', race, pilot, result['Rank'])
        db.add_race_result(raceResult)
    return

def list_races():
    log_message("List of all races", True)
    races = db.get_all_races_by_date()
    for race in races:
        log_message(str(race.id) +" | Multiplier: "+ str(race.multiplier) +" | "+ race.date +" | "+ race.name, True)

########################################################################
# ELO CALCULATOR FUNCTIONS
########################################################################

# Define a function to calculate the expected score for a racer in a given race
def expected_score(rating_a, rating_b):
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

# Update the rankings based on the single race results
# 1. Get the list of pilots
# 2. Calculate the expected score for each pilot
# 3. Calculate the delta for each pilot
# 4. Update the pilot's ELO
def update_rankings_per_race(race):
    raceResults = db.get_sorted_race_results_per_race(race.id)
    pilotsUpdated = []
    if USE_RACE_WEIGHT :
        finalMultiplier = race.multiplier * scale(race.weight, [1500,2000], [1, RACE_WEIGHT_MAX_MULTIPLIER])
    else:
        finalMultiplier = race.multiplier
    
    if USE_LOSS_LIMITER : 
        lossDivider = LOSS_LIMITER_DIVIDER
    else : 
        lossDivider = 1
    
    log_message(f"ENTERING RACE : {race.name}")
    for raceResult_a in raceResults:
        pilot_a = db.get_pilot_by_id(raceResult_a.pilot)
        finalDelta = 0
        for raceResult_b in raceResults:
            pilot_b = db.get_pilot_by_id(raceResult_b.pilot)
            expected = expected_score(pilot_a.elo, pilot_b.elo)
            delta = 0
            if (raceResult_a.rank < raceResult_b.rank):
                delta = K_FACTOR * (1 - expected) * finalMultiplier 
            elif (raceResult_a.rank > raceResult_b.rank):
                delta = K_FACTOR * (0 - expected) * finalMultiplier / lossDivider
            finalDelta += delta
            
        pilot_a.update_elo(pilot_a.elo+finalDelta)
        pilotsUpdated.append(pilot_a)
    
    for pilotUpdated in pilotsUpdated:
        log_message("New Elo for Pilot" + pilotUpdated.pseudo + " = " + str(pilotUpdated.elo))
        db.update_pilot_elo(pilotUpdated.id, pilotUpdated.elo)
        
    return

# Recalculate all rankings based on added races
# 1. Reset all
# 2. Recalculate all
def recalculate_rankings():
    # Resetting all Races weight
    db.update_all_races_weight(BASE_ELO)
    
    # Resetting all pilots elo
    pilots = db.get_all_pilots_by_rank(0)
    for pilot in pilots:
        log_message("Resetting Elo for Pilot : " + pilot.pseudo + " = " + str(BASE_ELO))
        db.update_pilot_elo(pilot.id, BASE_ELO)
        
    sorted_race_list = db.get_all_races_by_date()
    for race in sorted_race_list:
        avg_pilots_elo = db.get_avg_pilots_elo_per_race(race)
        race = db.update_race_weight(race, avg_pilots_elo)
        update_rankings_per_race(race)
    return

# Output the current pilot ranking with a minimum number of races
# MD format : 
#|#|ELO|LICENCE|PSEUDO|PRENOM|NOM DE FAMILLE|
#|:-|:-|:-:|:-:|:-:|:-:|
def output_pilot_ranking(numberOfRaces, format='md'):
    pilotsRanking = db.get_all_pilots_by_rank(numberOfRaces)
    log_message(f"CURRENT RANKING with {numberOfRaces} race(s):", True)
    if  format == 'md':
        log_message("|#|ELO|LICENCE|PSEUDO|PRENOM|NOM DE FAMILLE|", True)
        log_message("|:-|:-|:-:|:-:|:-:|:-:|", True)
    elif format == 'csv':
        log_message("#,ELO,LICENCE,PSEUDO,PRENOM,NOM DE FAMILLE")

    i=1
    for pilot in pilotsRanking:
        if  format == 'md':
            log_message("|"+f"{i:02d}"+"|"+str(int(pilot.elo))+"|"+pilot.licenseNumber+"|"+pilot.pseudo+"|"+pilot.firstName+"|"+pilot.lastName+"|", True)
        elif format == 'csv':
            log_message(f"{i:02d}"+","+str(int(pilot.elo))+","+pilot.licenseNumber+","+pilot.pseudo+","+pilot.firstName+","+pilot.lastName)
        i+=1
    return
    
# Check if race is already imported in the database based on the file name
def is_race_already_imported(fileName): 
    for race in db.get_all_races_by_date():
        if race.fileName == fileName:
            return True
    return False

########################################################################
# MENU FUNCTIONS
########################################################################
def print_menu():
    print ("----------------------")
    print ('ELO CALCULATOR !! v'+VERSION)
    print ("----------------------")
    print ("1. Get current rankings")
    print ("2. Calculate rankings")
    print ("3. Get race list")
    print ("4. Add a single race")
    print ("5. Add a list of races")
    print ("6. Set single race multiplier")
    print ("q. quit")

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def wait_for_user_input():
    input("Press any key to continue...")
    clear_console()
    return

########################################################################
# MAIN FUNCTION
########################################################################
def main():
    parser = argparse.ArgumentParser(description='Process input file to add data to the database')
    parser.add_argument('-q','--quiet', type=str, required=False, help='Quiet mode = No Menu | -i --input_folder option required', choices=['true','false'],default='false')
    parser.add_argument('-i','--input_folder',type=str, required=False, help='Path to the input file')
    parser.add_argument('-if','--input_format',type=str, required=False, help='File format | Default is csv', choices=['csv','json'],default='csv')
    parser.add_argument('-of','--output_format',type=str, required=False, help='File format | Default is csv', choices=['md','csv','json'],default='md')
    args = parser.parse_args()    

    logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)
    log_message('Welcome to the ELO CALCULATOR !! v'+VERSION)
    
    
    # Check quiet mode
    if (args.quiet == 'true'): # QUIET MODE
        if not args.input_folder:
            log_message("Input Folder required in quiet mode, please add option with -i or --input_folder", True)
            log_message("For more information please run with -h option", True)
            exit()
        if (os.path.exists(os.getcwd()+'\\'+DB_NAME)): 
            os.remove(os.getcwd()+'\\'+DB_NAME)
            log_message("Existing DB but in quiet mode -> Delete current DB")
            
        log_message("Creating new DB with name : " + DB_NAME)
        db.create(DB_NAME)
            
        # Proceed and work with provided files only
        # Loop Through path to get files
        fileNames = list_files_in_dir(args.input_folder, args.input_format)

        # For each file create race object
        for fileName in fileNames: 
            results = read_race_results(args.input_folder, fileName, args.input_format)
            update_db_with_race_results(results)    

        recalculate_rankings()
            
        output_pilot_ranking(MIN_NUM_RACES, args.output_format)
        db.close()
        log_message("Finished calculating rankings... Exiting !")
        exit()
        
    else : # NOT IN QUIET MODE
        log_message("Connecting to DB : " + DB_NAME)
        db.create(DB_NAME)
        
    clear_console()
    while True:
        print_menu()
        option = input("\n->  Enter your choice : ")
        clear_console()
        
        # Get current rankings
        if option == "1":
            num_races = input("\nPlease provide the minimum number of races for the ranking, {DEFAULT=" + str(MIN_NUM_RACES) + "} : ")
            if num_races.isdigit():
                output_pilot_ranking(num_races, args.output_format)
            else:
                output_pilot_ranking(MIN_NUM_RACES, args.output_format)
            
        # Calculate rankings
        elif option == "2":
            log_message("Calculating ranking with given races", True)
            recalculate_rankings()
            log_message("Done Calculating", True)
            
        # Get race list
        elif option == "3":
            list_races()
            
        # Add a single race
        elif option == "4":
            log_message("Adding a single race", True)
            fileFormat = "csv"
            fullPath = input ("Please provide race file path : ")
            folderPath, fileName = os.path.split(fullPath)
            if is_race_already_imported(fileName):
                log_message("Race already added", True)
            else:
                results = read_race_results(folderPath, fileName, fileFormat)
                update_db_with_race_results(results)   
        
        # Add a list of races
        elif option == "5":
            log_message("Adding list of files", True)
            fileFormat = "csv"
            folderPath = input ("Please provide folder path : ")
            # Loop Through path to get files
            fileNames = list_files_in_dir(folderPath, fileFormat)
            
            for fileName in fileNames: 
                if is_race_already_imported(fileName):
                    log_message("Race already added", True)
                else:
                    results = read_race_results(folderPath, fileName, fileFormat)
                    update_db_with_race_results(results)
            
            log_message("All files added", True)
            
        elif option == "6":
            list_races()
            race_id = input("\nSelect race id for update : ")
            multiplier = input("Please provide updated multiplier : ")
            if not multiplier.isdigit() or int(multiplier) < 1 or int(multiplier) > 3:
                log_message("Please set a multiplier between 1 and 3", True)
                continue
            
            races = db.get_all_races_by_date()
            for race in races:
                if race.id == int(race_id):
                    log_message(race.name + " with id " + str(race.id) + " selected.\nNew race multiplier : " + multiplier, True)
                    update_race_multiplier(race, int(multiplier))
                    log_message("Race weight updated for "+ race.name, True)
                    break
            list_races()

        elif option == "q":
            break
        else : 
            print("please provide a valid option")
        
        
        wait_for_user_input()
        ##END OF WHILE LOOP
        
    db.close()
    log_message("Finished calculating rankings... Exiting !", True)
    exit()

if __name__ == "__main__":
    main()
########################################################################