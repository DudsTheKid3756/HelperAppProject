import random
import getpass
import sys
import time
import mouse
import keyboard
import screeninfo
import pyautogui
import pywinauto
import ctypes
import easygui
from pywinauto.findwindows import find_windows
from datetime import datetime

user = getpass.getuser()  # gets current user of this Windows machine
is_live = False  # bool to set for live app or testing
state = []  # contains 0 if 'end' key is pressed
file_paths = {
    "messages": f"C:/Users/{user}/Desktop/messages",
    "scripts": f"C:/Users/{user}/Desktop/exit_scripts"
}

pyautogui.FAILSAFE = False
num_min = 0
if (len(sys.argv) < 2) or sys.argv[1].isalpha() or int(sys.argv[1]) < 1:
    num_min = 3
else:
    num_min = int(sys.argv[1])


def get_file_length(file: str) -> int:
    """gets the length of a file"""
    with open(file, 'r') as f:
        lines = sum(1 for _ in f)
        return lines


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
    file_paths.get("scripts"),
    (1, 8),
    (10, 17)
)
one_monitor: list[str] = monitors[0]
two_monitors: list[str] = monitors[1]


def exec_list_items(_list: list[str]):
    """executes command strings from list from txt file"""
    for item in _list:
        exec(item)


def click_spot(x: int, y: int) -> None:
    """moves to spot on screen and clicks"""
    mouse.move(x, y)
    mouse.click()


def press_key(key: str) -> None:
    """presses keyboard key/key sequence"""
    keyboard.press_and_release(key)


def type_message(message: str) -> None:
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


def get_end_response() -> str:
    return easygui.buttonbox(
        "Do you want to end the program or end the call?",
        "HelperApp", ["End Program", "End Call"])


def end_chat(hour=18) -> int:
    """
    - checks if current time is 6 or is equal to time arg
    - if equal checks current Chrome tab id and sets win_num to id if current tab is 24/7 meet
    - checks monitor config and executes exit script based on config
    """
    if datetime.now().hour >= hour:
        e = exec_list_items
        win_num = 0
        try:
            win_num = find_windows(best_match="Meet - New Hire 24/7 Meet")
        except pywinauto.findbestmatch.MatchError:
            pass

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


def stay_awake() -> int or None:
    """main script to move mouse if inactive for more than 3 minutes"""
    x = 0
    first_pos: tuple[int, int] = mouse.get_position()
    while x < num_min:
        for _ in range(60):
            end: int = end_chat()
            keyboard.on_press_key('end', lambda _: state.append(0))
            if end == 0:
                return 0
            if state.count(0) > 0:
                return
            time.sleep(1)
        x += 1
    sec_pos: tuple[int, int] = mouse.get_position()
    if abs(sec_pos[0] - first_pos[0]) < 50 and abs(sec_pos[1] - first_pos[1] < 50):
        print("Movement made at: {}".format(datetime.now().strftime("%B %d, %Y - %H:%M:%S")))
        for i in range(0, 100):
            pyautogui.moveTo(0, i * 10)
        pyautogui.moveTo(1, 1)
        for i in range(0, 4):
            pyautogui.press("capslock")


# prompts user to set live or testing environment and executes stay_awake function if live
while True:
    try:
        response = input("Is this live?> ")
    except TypeError:
        response = 'no'

    is_live = True if response.lower().startswith('y') else False
    z: int or None = None
    time.sleep(3)
    if is_live:
        while state.count(0) == 0:
            z = stay_awake()
        if z is None:
            end_response = get_end_response()
            if end_response == "End Call":
                end_chat(datetime.now().hour)
        print("Exiting program")
        time.sleep(2)
        if datetime.now().hour > 17:
            ctypes.windll.user32.LockWorkStation()
    exit(0)
