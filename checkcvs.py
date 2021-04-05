import argparse # used to parse command line arguments
import json # parses responses from CVS
import time # prints the time
import urllib.request # requests appointment information from CVS
from playsound import playsound # plays the alarm

def alarm():
    playsound("alarm.mp3", False)

    return True

def find_city(json_in: dict, state: str, city: str):
    foundCity = False
    for location in json_in["responsePayloadData"]["data"][state]:
        if location["city"] == city:
            foundCity = True

    return foundCity

def find_cities(json_in: dict, state: str, cities: list):
    allGood = True
    for city in cities:
        if not find_city(json_in, state, city):
            print ("Couldn't find " + city
                   + ", check your spelling, or they may not have a CVS.")
            allGood = False

    return allGood

def check_cities(json_in: dict, state: str, cities: list):
    found_appointment = False

    if not find_cities(json_in, state, cities):
        input("Press enter to end the program")
        exit()

    for location in json_in["responsePayloadData"]["data"][state]:
        #print(location["city"])
        for city in cities:
            if location["city"] == city:
                if location["status"] != "Fully Booked":
                    print ("Appointment available at " + location["city"] + "!")
                    found_appointment = True
    if found_appointment:
        alarm()

    return found_appointment

def check_state(json_in: dict, state: str):
    found_appointment = False
    for location in json_in["responsePayloadData"]["data"][state]:
        if location["status"] != "Fully Booked":
            print ("Appointment available at " + location["city"] + "!")
            found_appointment = True
    if found_appointment:
        alarm()

    return found_appointment

def make_request(state: str):
    headers = {
        "Referer": "https://www.cvs.com/immunizations/covid-19-vaccine?icid=cvs-home-hero1-link2-coronavirus-vaccine",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    req = urllib.request.Request("https://www.cvs.com/immunizations/covid-19-vaccine.vaccine-status."
                                 + state + ".json?vaccineinfo", headers = headers)
    localtime = time.strftime("%I:%M:%S %p", time.localtime())
    print("Making request at " + localtime)

    return urllib.request.urlopen(req).read()

def main(delay: int, soundcheck: bool, state: str, cities: list):
    foundAppointment = False
    timestamp = ""

    if soundcheck:
        alarm()
        input("Press enter to end the program")
        exit()

    else:
        if cities:
            print("Checking for appointments in " + state
                  + " every " + str(delay) + " seconds:")
            for city in cities:
                print(city)
        else:
            print("Checking for appointments in " + state
                  + " every " + str(delay) + " seconds.")

        while not foundAppointment:
            data = json.loads(make_request(state))
            if data["responsePayloadData"]["currentTime"] != timestamp:
                timestamp = data["responsePayloadData"]["currentTime"]
                print("CVS updated data at " + timestamp)
                if cities:
                    foundAppointment = check_cities(data, state, cities)
                else:
                    foundAppointment = check_state(data, state)

                if foundAppointment:
                    print("Go to https://www.cvs.com/immunizations/covid-19-vaccine")
                    input("Press enter to end the program")
                    print("Hope you got your appointment!")
                    exit()

            time.sleep(delay)



    return foundAppointment

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--delay", required = False, type = int, default = 60, 
                        help = "Seconds to wait between each request. Defaults to 60.")
    parser.add_argument("--soundcheck", required = False, 
                        action = "store_true", default = False,
                        help = "Optional. If present, plays the alarm sound.")
    parser.add_argument("--state", required = False, type = str, default = "CT", 
                        help = "Two-letter state code, capitalized. Defaults to 'CT'.")
    parser.add_argument("--cities", "--city", required = False, type = str, default = "", nargs = '+',
                        help = "Optional: specify cities to check for appointments."
                        + " Surround each city with quotes.")

    args = parser.parse_args()

    cities = []

    if args.cities:
        for city in args.cities:
            cities.append(city.upper())

    #print(cities)

    main(args.delay, args.soundcheck, args.state, cities)