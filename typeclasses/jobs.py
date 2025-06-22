# typeclasses/jobs.py

class Job:
    def __init__(self, name, description, hp, mp, spell_list, ability_list):
        self.name = name
        self.description = description
        self.hp = hp
        self.mp = mp
        self.spell_list = spell_list
        self.ability_list = ability_list

# Define example jobs
whm = Job("White Mage", "A healer who uses divine magic.", 7, 8, ["Cure", "Dia"], ["Dual Wield", "Run"])
blm = Job("Black Mage", "An offensive spellcaster of elemental destruction.", 6, 9, ["Fire", "Thunder"], ["Focus", "Meditate"])
war = Job("Warrior", "A powerful front-line melee fighter.", 10, 3, [], ["Berserk", "Taunt"])
thf = Job("Thief", "A quick and cunning rogue.", 8, 5, [], ["Steal", "Hide"])
mnk = Job("Monk", "A disciplined hand-to-hand combatant.", 9, 4, [], ["Kick", "Chakra"])

# List of jobs for chargen
job_list = [whm, blm, war, thf, mnk]