# dicebot.py
# !/usr/bin/env python3
"""Available functions:
- parse_text: Determine if a String value is a valid dice roll command
- roll_dice: Simulate the rolling of one or more dice with an arbitrary number of sides
- format_slack_response: Turn the result of a roll_dice into a slack compatible output dict
"""
# imports
from random import randint

# globals
DEFAULT_NUM_DICE = 1  # rolls 1 dice when not specified
DEFAULT_DICE_SIDES = 20  # max number of sides that can be specified
DEFAULT_DIVIDER_STR = "d"  # string to divide num_dice and dice_sides


def parse_text(text):
    """Take a roll definition string, checks if it's valid, and then returns
        a dict to be used as kwargs for the roll_dice function.

        Args:
            text: a String value defining a roll according to SRD standard (ie "2d10")

        Returns: a dict with the output required for roll_dice function
            num_dice: integer value for how many dice will be rolled
            dice_sides: integer value for sides on each dice. represents maximum roll value.
        ex: {"num_dice":1, "dice_sides":20}
    """
    num_dice = DEFAULT_NUM_DICE
    num_sides = DEFAULT_DICE_SIDES
    divider = DEFAULT_DIVIDER_STR.lower()

    if text:
        lower_text = str(text).lower()  # ex: convert "D" to "d"
        # if a divider is present, attempt to parse the values before and after it
        if divider in lower_text:
            # returns partitiioned tuple: (num_dice,"d",num_sides)
            parted_text = lower_text.partition(divider)
            # if num_dice is defined, convert to int and use it
            if parted_text[0]:
                num_dice = int(parted_text[0])  # throws ValueError
            # if num_sides is defined, convert to int and use it
            if parted_text[2]:
                num_sides = int(parted_text[2])  # throws ValueError
        else:
            # if no divider is present, as single int is accepted as num_dice
            num_dice = int(text)  # throws ValueError

    output = {"num_dice": num_dice, "dice_sides": num_sides}
    return output


def roll_dice(num_dice=DEFAULT_NUM_DICE, dice_sides=DEFAULT_DICE_SIDES):
    """Creates a dict with random roll values

    Args:
        num_dice: integer value for how many dice will be rolled
        dice_sides: integer value for sides on each dice. represents maximum roll value.

    Returns: dict with that contains the roll definition and results
        keys and values in the output inlcude:
        dice_roll: a string defining the dice roll (ie, "1d20")
        results: a list of ints representing rolled values (ie, [20])
        ex: {"dice_roll": "1d20", "results":[20]}
    """
    dice_results = [randint(1, dice_sides) for i in range(num_dice)]
    dice_result_dict = {"dice_roll": "{}d{}".format(num_dice, dice_sides), "results": dice_results}
    return dice_result_dict


def format_slack_response(dice_result):
    """Takes the output from the roll_dice function and creates a slack-formatted dict with output

    Args:
        dice_result: a dict with the output from roll_dice.
           expects keys and values for:
               dice_roll: a string defining the dice roll (ie, "1d20")
               results: a list of ints representing rolled values (ie, [20])
            ex: {"dice_roll": "1d20", "results":[20]}

    Returns: A dict with containing a result message as expected by the slack API
        ex:
    {
    "response_type": "in_channel",
    "text": "20",
    "attachments": [{
            "text":"rolled 1d20"
        }]
    }
    """
    sum_results = sum(dice_result["results"])
    output_dict = {"response_type": "in_channel"}
    output_dict["text"] = "{} = {}".format(dice_result["results"], str(sum_results))
    output_dict["attachments"] = [{"text": "rolled {}".format(dice_result["dice_roll"])}]
    return output_dict