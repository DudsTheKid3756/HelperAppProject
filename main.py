import ctypes
import getpass
import os
import random
import sys
import time
from datetime import datetime

import easygui
import keyboard
import mouse
import pyautogui
import pywinauto
import screeninfo
from pywinauto.findwindows import find_windows

pyautogui.FAILSAFE = False
num_min = 3 if (len(sys.argv) < 2) or sys.argv[1].isalpha() or int(sys.argv[1]) < 1 else int(sys.argv[1])

user = getpass.getuser()  # gets current user of this Windows machine
base_path = f"C:/Users/{user}/Desktop/"
is_live = False  # bool to set for live app or testing
state: list[int] = []  # used to determine which set of instructions to execute

file_keys = ['messages', 'logs', 'move_configs']  # file/dir names to use as keys for dict
file_paths = {file: f'{base_path}{file}' for file in file_keys}  # dict of files/dirs needed from user desktop

os.mkdir(file_paths.get("logs")) if not os.path.isdir(file_paths.get("logs")) else None  # creates new log directory
log_file_name = f"{file_paths.get('logs')}/log_{datetime.now().strftime('%B %d, %Y')}"  # sets name of new log file
log_file = open(log_file_name, 'a') \
    if os.path.isfile(log_file_name) \
    else open(log_file_name, 'x')  # opens log file for current day or creates new one if it doesn't exist

default_config = "[pyautogui.moveTo(0, i * 10) for i in range(100)]"


def get_dir_size(dir_path: str) -> int:
    """gets size of a directory; i.e. how many files are present within a directory"""
    return len([name for name in os.listdir(dir_path)])


move_config_dir_len = get_dir_size(file_paths.get('move_configs'))  # length of move config dir
move_configs = [
    f"{file_paths.get('move_configs')}/move_config_{i + 1}" for i in range(move_config_dir_len)
]  # adds all move config file names to a list

default_message = "Catch you guys later, bye!"
custom_message: str  # custom exit message
set_hour: int = 18  # default value for time to close chat


def get_file_length(file: str) -> int:
    """gets the length of a file"""
    with open(file, 'r') as f:
        lines = sum(1 for _ in f)
        return lines


def get_config(rand_num: int) -> list[str]:
    """gets contents of config file based on list index"""
    rand_config = move_configs[rand_num]
    config_length = get_file_length(rand_config)
    with open(rand_config) as rc:
        c_lines = rc.readlines()
    return [c_lines[i].strip() for i in range(config_length)]


def read_file(file_path: str, range_1: tuple[int, int], range_2=None) -> tuple[list[str], list[str]]:
    """returns tuple of lists comprised of text from txt files"""
    with open(file_path) as f:
        lines: list[str] = f.readlines()
    text_1: list[str] = [lines[i].strip() for i in range(range_1[0], range_1[1])]
    text_2: list[str] = None if range_2 is None else [lines[i].strip() for i in range(range_2[0], range_2[1])]
    return text_1, text_2


# sets messages variable to list of messages from 'messages' text file
# range_1 passed in for read_file is set to length of file so messages file can be updated
messages: list[str] or None = read_file(
    file_paths.get("messages"),
    (1, get_file_length(file_paths.get("messages")))
)[0]

# sets monitor variable to tuple of lists from 'exit_scripts' text file
# first is for single monitor setup, second is for dual monitor setup
monitors: list[str] or None = read_file(
    "../HelperAppProject/exit_scripts",
    (1, 8),
    (10, 17)
)
one_monitor: list[str] = monitors[0]
two_monitors: list[str] = monitors[1]


def exec_list_items(_list: list[str]) -> None:
    """executes command strings from list from txt file"""
    for item in _list:
        exec(item)


e = exec_list_items


def click_spot(x: int, y: int) -> None:
    """moves to spot on screen and clicks"""
    mouse.move(x, y)
    mouse.click()


def press_key(key: str) -> None:
    """presses keyboard key/key sequence"""
    keyboard.press_and_release(key)


def type_message(message=default_message) -> None:
    """types out message"""
    time.sleep(2)
    print(message)
    for ch in message:
        if ch == '!':
            press_key("shift+1")
        else:
            press_key(ch)
        time.sleep(0.1)
    time.sleep(1)
    press_key('enter')


def change_tabs(x: int, y: int) -> None:
    """changes to google meet tab (tab 2)"""
    meet_tab = "ctrl+2"
    click_spot(x, y)
    time.sleep(2)
    press_key(meet_tab)


def set_close_schedule() -> None:
    """callback func to change hour that chat ends"""
    global set_hour
    hour: int = easygui.integerbox(
        "Input a time to end Google Meet (in hours):",
        "Helper App", set_hour, 0, 24
    )
    if hour is not None:
        set_hour = hour


def end_chat(hour=set_hour) -> int:
    """
    - checks if current time is 6 or is equal to time arg
    - if equal checks current Chrome tab id and sets win_num to id if current tab is 24/7 meet
    - checks monitor config and executes exit script based on config
    """
    global custom_message
    if datetime.now().hour >= hour:
        win_num = 0
        try:
            win_num = find_windows(best_match="Meet - New Hire 24/7 Meet")
        except pywinauto.findbestmatch.MatchError:
            pass

        custom_message_response = easygui.buttonbox(
            "Would you like to use a custom message?",
            "Helper App", ["Custom Message", "Default Messages"])
        time.sleep(1)

        if custom_message_response == "Custom Message":
            custom_message = easygui.enterbox(
                "Enter your custom message here:",
                "Custom Message")
        time.sleep(2)

        if len(screeninfo.get_monitors()) == 1:
            if win_num == 0:
                change_tabs(1656, 9)
                time.sleep(5)
            e(one_monitor)
        else:
            if win_num == 0:
                change_tabs(1337, 1093)
                time.sleep(5)
            e(two_monitors)
        return 0
    return 1


def stay_awake() -> int:
    """main script to move mouse if inactive for more than 3 minutes"""
    x = 0
    first_pos: tuple[int, int] = mouse.get_position()
    while x < num_min:
        for _ in range(60):
            end: int = end_chat()
            keyboard.on_press_key('end', lambda _: state.append(0))
            keyboard.on_press_key('home', lambda _: state.append(1))
            if end == 0:
                return 0
            if state.count(0) > 0:
                return 1
            if state.count(1) > 0:
                return 2
            time.sleep(1)
        x += 1
    sec_pos: tuple[int, int] = mouse.get_position()
    if abs(sec_pos[0] - first_pos[0]) < 50 and abs(sec_pos[1] - first_pos[1] < 50):
        log_file.write(f"Movement made at: {datetime.now().strftime('%B %d, %Y - %H:%M:%S')}\n")
        if not os.path.isdir(file_paths.get("move_configs")) or get_dir_size(file_paths.get("move_configs")) == 0:
            exec(default_config)
        else:
            exec_list_items(get_config(random.randint(0, move_config_dir_len - 1)))
        pyautogui.moveTo(1, 1)
        for i in range(4):
            pyautogui.press("capslock")


def _schedule():
    set_close_schedule()
    state.clear()


def _end():
    end_response = easygui.buttonbox(
        "Do you want to end the program or end the call?",
        "HelperApp", ["End Program", "End Call", "Cancel"])
    if end_response == "End Call":
        end_chat(datetime.now().hour)
    elif end_response == "End Program":
        pass
    else:
        state.clear()


def _close():
    state.append(0)


def stay_awake_response_switch(s_a_response: int):
    switcher = {
        0: _close,
        1: _end,
        2: _schedule
    }

    func = switcher.get(s_a_response)
    func() if callable(func) else None


# prompts user to set live or testing environment and executes stay_awake function if live
while True:
    try:
        response = input("Is this live?> ")
    except TypeError:
        response = 'no'

    is_live = True if response.lower().startswith('y') else False
    time.sleep(3)
    if is_live:
        while state.count(0) == 0:
            stay_awake_response: int = stay_awake()
            stay_awake_response_switch(stay_awake_response)
        state.clear()
        print("Exiting program")
        time.sleep(2)
        if datetime.now().hour > 17:
            ctypes.windll.user32.LockWorkStation()
        log_file.close()
    exit(0)
