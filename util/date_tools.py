from datetime import datetime
import pytz


def get_today_string():
    berlin_tz = pytz.timezone("Europe/Berlin")
    now = datetime.now(berlin_tz)
    return now.strftime("%Y-%m-%d")


def is_date_today(date: str):
    berlin_tz = pytz.timezone("Europe/Berlin")

    date = datetime.strptime(date, "%Y-%m-%d")
    date = berlin_tz.localize(date)

    return date.date() == datetime.now(berlin_tz).date()


def current_time():
    date = datetime.now(pytz.timezone("Europe/Berlin"))
    return date.strftime("%H:%M:%S.%f")[:-4]
