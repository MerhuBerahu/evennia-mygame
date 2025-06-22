from evennia import EvMenu, search_tag  # Import Evennia's menu system and tag search
from typeclasses.races import RACES     # Custom race definitions
from typeclasses.jobs import job_list   # Custom job/class definitions

EvMenu.DEBUG = True  # Enable menu debug logging (prints menu steps in server logs)

# -----------------------------------------------------
# STEP 1: RACE SELECTION
# -----------------------------------------------------
def start(caller):
    """
    Starting point of the character generation menu.
    Presents a list of races to choose from.
    """
    text = "|wWelcome to Character Generation!|n\nChoose your race:"
    options = []

    # Create a menu option for each race
    for key, data in RACES.items():
        options.append({
            "desc": f"{data['name']} - {data['description']}",
            "goto": ("select_race", {"race_key": key})
        })

    return text, options

def select_race(caller, raw_string, **kwargs):
    """
    Displays the details of the selected race, with option to confirm or choose again.
    """
    race_key = kwargs["race_key"]
    race = RACES[race_key]

    text = (
        f"You selected |g{race['name']}|n.\n\n"
        f"|cDescription:|n {race['description']}\n"
        f"|cStats:|n\n" +
        "\n".join([f"  {k.capitalize()}: {v}" for k, v in race["stats"].items()])
    )

    options = [
        {"desc": "Confirm", "goto": ("finish_race", {"race_key": race_key})},
        {"desc": "Pick another race", "goto": "start"}
    ]

    return text, options

def finish_race(caller, raw_string, **kwargs):
    """
    Stores the selected race and moves to sex selection.
    """
    race_key = kwargs["race_key"]
    caller.db.chargen_data = {"race": race_key}  # Start a dict to track choices

    text = f"You selected |g{RACES[race_key]['name']}|n.\nNow choose your sex/gender:"
    options = [{"desc": "Continue", "goto": "select_sex"}]

    return text, options

# -----------------------------------------------------
# STEP 2: SEX/GENDER SELECTION
# -----------------------------------------------------
def select_sex(caller):
    """
    Menu to choose sex or gender identity.
    """
    text = "|wChoose your sex/gender identity:|n"
    options = [
        {"desc": "Male", "goto": ("finish_sex", {"sex": "male"})},
        {"desc": "Female", "goto": ("finish_sex", {"sex": "female"})},
        {"desc": "Nonbinary", "goto": ("finish_sex", {"sex": "nonbinary"})},
        {"desc": "Custom/Other", "goto": ("finish_sex", {})},  # Raw string fallback
    ]

    return text, options

def finish_sex(caller, raw_string, **kwargs):
    """
    Stores selected sex or custom entry.
    """
    chosen = kwargs.get("sex", raw_string.strip())
    caller.db.chargen_data["sex"] = chosen

    text = f"You selected |g{chosen}|n.\nNow choose your job:"
    options = [{"desc": "Continue", "goto": "select_job"}]

    return text, options

# -----------------------------------------------------
# STEP 3: JOB SELECTION
# -----------------------------------------------------
def select_job(caller):
    """
    Displays job/class options from job_list.
    """
    text = "|wSelect your starting job:|n"
    options = []

    for idx, job in enumerate(job_list):
        options.append({
            "desc": f"{job.name} - {job.description}",
            "goto": ("finish_job", {"job_index": idx})
        })

    return text, options

def finish_job(caller, raw_string, **kwargs):
    """
    Stores selected job and moves to city selection.
    """
    job_index = kwargs["job_index"]
    job = job_list[job_index]

    # Save selected job info
    caller.db.chargen_data["job"] = {
        "name": job.name,
        "hp": job.hp,
        "mp": job.mp,
        "spells": job.spell_list,
        "abilities": job.ability_list
    }

    text = f"You selected the job |g{job.name}|n.\nNow choose your starting city:"

    # Hardcoded city options
    cities = {
        "Evannia": "A bustling capital of trade and politics.",
        "Darkhollow": "A mysterious mountain town with ancient secrets.",
        "Seawatch": "A coastal city known for storms and ships.",
        "Frostgarde": "A frozen fortress in the north.",
    }

    options = []
    for name, desc in cities.items():
        options.append({
            "desc": f"{name} - {desc}",
            "goto": ("store_city", {"city_name": name})
        })

    return text, options

# -----------------------------------------------------
# STEP 4: STARTING CITY & NAME
# -----------------------------------------------------
def store_city(caller, raw_string, **kwargs): ### This is where my troubles start
    """
    Stores the selected starting city, prompts for character name.
    """
    try:
        city = kwargs["city_name"]
        caller.db.chargen_data["starting_city"] = city
        caller.msg(f"[DEBUG] store_city() - city set to: {city}")

        text = "|wPlease enter your character's name:|n"
        options = [{"key": "_default", "exec": handle_name_input}]

        return text, options

    except Exception as e:
        caller.msg(f"|r[ERROR in store_city()] {e}")
        return "|rAn error occurred in store_city. Check the logs.|n", []

def handle_name_input(caller, raw_string, **kwargs):  #never gets called
    """
    Handles and validates name input. Confirms character summary.
    """
    name = raw_string.strip()
    caller.msg(f"[DEBUG] handle_name_input() - name received: {name}")

    if len(name) < 2:
        return "|rInvalid name.|n Name must be at least 2 characters long:", handle_name_input

    # Store chosen name
    caller.db.chargen_data["name"] = name
    data = caller.db.chargen_data
    job = data["job"]

    # Summary screen
    text = (
        f"|wConfirm your character details:|n\n"
        f" |cName:|n {data['name']}\n"
        f" |cRace:|n {data['race']}\n"
        f" |cSex:|n {data['sex']}\n"
        f" |cJob:|n {job['name']} (HP: {job['hp']}, MP: {job['mp']})\n"
        f" |cCity:|n {data['starting_city']}\n\n"
        f"|wIs this correct?|n"
    )

    options = [
        {"desc": "Yes, finish character", "goto": "finalize_character"},
        {"desc": "No, restart chargen", "goto": "start"}
    ]

    return text, options

# -----------------------------------------------------
# STEP 5: FINALIZATION
# -----------------------------------------------------
def finalize_character(caller):
    """
    Finalizes the character, assigns all chosen attributes,
    and moves the player to the starting city.
    """
    data = caller.db.chargen_data
    job = data["job"]

    # Assign character attributes
    caller.key = data["name"]
    caller.db.name = data["name"]
    caller.db.race = data["race"]
    caller.db.sex = data["sex"]
    caller.db.job = job["name"]
    caller.db.hp = job["hp"]
    caller.db.mp = job["mp"]
    caller.db.spells = job["spells"]
    caller.db.abilities = job["abilities"]
    caller.db.city = data["starting_city"]

    # Look up room by tag: e.g., tag "start_evannia"
    tagname = f"start_{data['starting_city'].lower()}"
    matches = search_tag(tagname, category="start_location")

    if matches:
        caller.location = matches[0]
        caller.msg(f"You awaken in |y{matches[0].key}|n.")
    else:
        caller.msg("|rError: Starting city not found. Contact an admin.|n")

    # Cleanup chargen data
    del caller.db.chargen_data

    return "|gCharacter creation complete!|n Type |wlook|n to begin your adventure.", None
