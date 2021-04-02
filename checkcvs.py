# import os # used to get environment variables
# import sys # used for sys.exit
import argparse # used to parse command line arguments
import json # parses responses from CVS
import urllib.request # requests appointment information from CVS
import time # prints the time
from playsound import playsound # plays the alarm

def alarm():
    playsound("alarm.mp3", False)
    return

def check_for_appointments(json_in, state):
    found_appointment = False
    for location in json_in["responsePayloadData"]["data"][state]:
        if location["status"] != "Fully Booked":
            print ("Appointment available at " + location["city"] + "!")
            found_appointment = True
    if found_appointment:
        alarm()
    return found_appointment

def main(delay: int, soundcheck: bool, state: str):
    appointment = False
    timestamp = ""
    headers = {
        "Referer": "https://www.cvs.com/immunizations/covid-19-vaccine?icid=cvs-home-hero1-link2-coronavirus-vaccine",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    req = urllib.request.Request("https://www.cvs.com/immunizations/covid-19-vaccine.vaccine-status."
                                 + state + ".json?vaccineinfo", headers = headers)

    if soundcheck:
        alarm()

    else:
        print("Checking for appointments in " + state
              + " every " + str(delay) + " seconds.")
        while not appointment:
            localtime = time.strftime("%I:%M:%S %p", time.localtime())
            print("Making request at " + localtime)

            response = urllib.request.urlopen(req).read()
            data = json.loads(response)

            if data["responsePayloadData"]["currentTime"] != timestamp:
                timestamp = data["responsePayloadData"]["currentTime"]
                print("CVS updated data at " + timestamp)
                if check_for_appointments(data, state):
                    break

            time.sleep(delay)

    input("Press enter to end the program")
    print("Hope you got your appointment!")
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--delay", required = False, type = int, default = 60, 
                        help = "Seconds to wait between each request. Defaults to 60.")
    parser.add_argument("--soundcheck", required = False, 
                        action = "store_true", default = False,
                        help = "Optional. If present, plays the alarm sound.")
    parser.add_argument("--state", required = False, type = str, default = "CT", 
                        help = "Two-letter state code, capitalized. Defaults to 'CT'.")
    args = parser.parse_args()

    main(args.delay, args.soundcheck, args.state)
    exit