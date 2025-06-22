from evennia.contrib.base_systems.custom_gametime import custom_gametime
from commands.command import Command
from evennia import Command
from evennia.utils import gametime
import time

def get_custom_time():
    """
    Calculate in-game time using Evennia's accelerated gametime system.
    Assumes:
        - TIME_FACTOR = 25.0
        - 8-day weeks
        - 30-day months
        - 360-day years
    """
   

    # Calculate the number of in-game seconds
    rseconds = int(gametime.gametime(absolute=True)) ### Doesnt work, sets the year as year 3, some issue with epoch and time factor in server/conf/settings.py

    # For now, we will use the real time epoch
    seconds = int(time.time())
    gseconds = int(rseconds * 25)


    # DEBUG: Time calculation comparison
    print(f"[DEBUG] Evennia rseconds: {rseconds}")
    print(f"[DEBUG] Real epoch seconds: {seconds}")
    print(f"[DEBUG] Custom gseconds (epoch * 25): {gseconds}")

    # Time units
    mincount = gseconds // 60
    hourcount = mincount // 60
    daycount = hourcount // 24
    monthcount = daycount // 30
    yearcount = monthcount // 12

    # Time components
    hour = hourcount % 24
    minute = mincount % 60
    weekday_index = daycount % 8
    date = daycount % 30
    month_index = monthcount % 12

    # Weekdays and months
    weekdays = [
        "|rFiresday|n",       # Red
        "|gEarthsday|n",      # Green
        "|bWatersday|n",      # Blue
        "|cWindsday|n",       # Cyan
        "|W|hIceday|n",       # Bright White + Bold
        "|yLightningday|n",   # Yellow
        "|mLightsday|n",      # Magenta
        "|D|hDarksday|n",     # Dark Grey (Bright Black) + Bold
    ]
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    day = weekdays[weekday_index]
    month = months[month_index]

    # Season
    if month in ("November", "December", "January"):
        season = "Winter"
    elif month in ("February", "March", "April"):
        season = "Spring"
    elif month in ("May", "June", "July"):
        season = "Summer"
    else:
        season = "Autumn"

    # Sunrise/Sunset
    sunrise_sunset = {
        "Winter": (10, 16),
        "Spring": (8, 18),
        "Summer": (6, 22),
        "Autumn": (9, 17)
    }
    sunrise, sunset = sunrise_sunset[season]

    # Determine the day within the current 90-day lunar cycle
    moon_day = daycount % 90
    moon = "|wNew Moon|n"  # Default fallback moon phase (white)

    # Assign moon phase based on moon_day range
    if 1 <= moon_day <= 7:
        moon = "|wNew Moon|n"  # White
    elif 8 <= moon_day < 47:
        moon = "|C|hCrescent Moon|n"  # Bright Cyan & Bold
    elif 47 <= moon_day < 65:
        moon = "|bHalf Moon|n"  # Blue
    elif 65 <= moon_day < 83:
        moon = "|mGibbous Moon|n"  # Magenta
    elif 83 <= moon_day <= 90:
        moon = "|W|hFull Moon|n"  # Bright White & Bold

        # 🌑 Blood Moon logic: occurs on prime-numbered full moons only
        full_moons_passed = daycount // 90

        # Check if number of full moons passed is a prime number
        if full_moons_passed > 1 and all(
            full_moons_passed % i != 0 for i in range(2, int(full_moons_passed ** 0.5) + 1)
        ):
            moon = "|R|hBlood Moon|n"  # Bright Red & Bold for dramatic effect

    # 🎊 Define special in-game calendar events tied to (day, month)
    special_days = {
        (1, "January"): "|wNew Year's Day|n",         # White
        (25, "March"): "|gSpring Equinox|n",          # Green
        (21, "June"): "|Y|hSummer Solstice|n",        # Bright Yellow + Bold
        (22, "September"): "|C|hAutumn Equinox|n",    # Bright Cyan + Bold
        (30, "October"): "|r|hHalloween|n",           # Bright Red + Bold
        (21, "December"): "|b|hWinter Solstice|n",    # Blue + Bold
        (25, "December"): "|W|hXmas|n"                # Bright White + Bold
    }

    # 🎯 Look up if today matches a special day
    special_day = special_days.get((date, month), None)

    return yearcount, month, date, day, hour, minute, gseconds, season, moon, special_day, sunrise, sunset


class CmdTime(Command):
    """
    Display the current in-game date and time.

    Usage:
        timenow
    """
    key = "timenow"
    aliases = ["clock", "time"]
    locks = "cmd:all()"

    def func(self):
        year, month, date, day, hour, minute, seconds, season, moon, special_day, sunrise, sunset = get_custom_time()

        time_string = (
            f"{date}, {month} {day}, Year {year}\n"
            f"The time is {hour:02}:{minute:02}:{seconds % 60:02}.\n"
            f"Season: {season}, Moon Phase: {moon}\n"
            f"|Y|hSunrise|n was at {sunrise:02}:00 and |R|hSunset|n will be at {sunset:02}:00.\n"
        )
        if special_day:
            time_string += f"\nToday is {special_day}!"

        # Debug info
        time_string += (
            f"\n[DEBUG] year={year}, month={month}, day_of_month={date}, "
            f"hour={hour}, minute={minute}, second={seconds % 60}, "
            f"weekday={day}, season={season}, moon={moon}, special_day={special_day}"
        )

        self.msg(time_string)