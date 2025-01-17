from datetime import date, datetime, timezone
from garminconnect import Garmin
from notion_client import Client
import os

page_id_dict = {
    "17c571d4386c80b3aa28fa51cc8c2405": False,
    "17c571d4386c80689233d64b878268be": False,
    "17c571d4386c800db319ef7382f95f4a": False,
    "17c571d4386c80188db1ce7c78ff7c25": False,
    "17c571d4386c803988a5d384f44aae51": False
}

weekday_dict = {
    0: "Mon",
    1: "Tue",
    2: "Wed",
    3: "Thu",
    4: "Fri",
    5: "Sat",
    6: "Sun"
}

def write_row(client, weekday):
    for key, value in page_id_dict.items():
        client.pages.update(
            **{
                "page_id": key,
                "properties": {
                    weekday_dict[weekday]: {
                        "checkbox": value
                    }
                }
            }
        )

def resetWeeklyGoals(client):
    for key, value in page_id_dict.items():
        content = client.pages.retrieve(page_id=key)
        progress = content['properties']['Progress']['formula']['number'] > 0.99
        streak = content['properties']['Streak']['number']
        streak = streak + 1 if progress else 0
        
        client.pages.update(
            **{
                "page_id": key,
                "properties": {
                    "Mon": {"checkbox": False},
                    "Tue": {"checkbox": False},
                    "Wed": {"checkbox": False},
                    "Thu": {"checkbox": False},
                    "Fri": {"checkbox": False},
                    "Sat": {"checkbox": False},
                    "Sun": {"checkbox": False},
                    "Streak": {"number": streak}
                }
            }
        )

def main():
    garmin_email = os.getenv("GARMIN_EMAIL")
    garmin_password = os.getenv("GARMIN_PASSWORD")
    notion_token = os.getenv("NOTION_TOKEN")

    garmin = Garmin(garmin_email, garmin_password)
    garmin.login()

    client = Client(auth=notion_token)

    today = date.today()
    weekday = today.weekday()
    today = today.isoformat()
    if weekday == 0: resetWeeklyGoals(client)

    steps = garmin.get_stats_and_body(today)['totalSteps']
    pilates = False
    run = False
    vovinam = False
    sleep = garmin.get_stats_and_body(today)['sleepingSeconds']

    sleep = sleep >= 28800

    activity = garmin.get_activities_by_date(today)
    for i in range(len(activity)):
        #print(activity[i]['activityType']['typeKey'], "\n")
        if activity[i]['activityType']['typeKey']=="pilates": pilates=True
        if activity[i]['activityType']['typeKey']=="running": run=True
        if activity[i]['activityType']['typeKey']=="mixed_martial_arts": vovinam=True
        
    steps = steps >= 9000

    page_id_dict["17c571d4386c80b3aa28fa51cc8c2405"] = sleep
    page_id_dict["17c571d4386c80689233d64b878268be"] = run
    page_id_dict["17c571d4386c800db319ef7382f95f4a"] = pilates
    page_id_dict["17c571d4386c80188db1ce7c78ff7c25"] = vovinam
    page_id_dict["17c571d4386c803988a5d384f44aae51"] = steps
    
    write_row(client, weekday)

if __name__ == '__main__':
     main()
