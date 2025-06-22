# Import the base Command class from Evennia's command system
from evennia import Command

# Import Evennia's menu system for interactive multi-step menus
from evennia import EvMenu


class CmdChargen(Command):
    """
    This command launches the character generation menu using EvMenu.

    Usage:
        chargen

    This would typically be used by new players to create and customize their characters.
    """

    # The keyword the player types to invoke this command
    key = "chargen"

    # Lock string to determine who can use the command
    # "cmd:all()" means all users can run this (you might change to perm(Player) in future)
    locks = "cmd:all()"

    def func(self):
        """
        The function called when the player uses the `chargen` command.
        It starts an EvMenu for character creation.
        """
        # Launch the EvMenu system for this caller (the player)
        # "world.chargen_menu" is the path to the chargen module (e.g., mygame/world/chargen_menu.py)
        # "startnode" is the entry function name within that module
        EvMenu(self.caller, "world.chargen_menu", startnode="start")
