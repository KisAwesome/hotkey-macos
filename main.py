import pyautogui
import clipboard
import ctypes
import time
import webbrowser
import os
import sys
import pynput.keyboard as keyboard
import pynput.mouse as mouse
import threading
import compiler
import zono.colorlogger as colorlogger
import signal
import re

chars = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y',
 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~']


kbd = keyboard.Controller()

CURRENTLY_PRESSED = None
def parse_hotkey(hotkey):
    hotkey = hotkey.lower().strip()
    _parsed = re.split(r',\s?', hotkey)
    keys = re.split(r'\s?\+\s?',_parsed[0])
    parsed_hotkey = []
    for key in keys:
        if key in chars:
            parsed_hotkey.append(key)
            continue
        parsed_hotkey.append(f'<{key}>')

    return keyboard.HotKey.parse('+'.join(parsed_hotkey))


def create_hotkey(hotkey,action,args):
    return keyboard.HotKey(parse_hotkey(hotkey),action,args=args)

def is_pressed(hotkey):
    parsed = parse_hotkey(hotkey)
    state = True
    for i in parsed:
        if not i in CURRENTLY_PRESSED:
            state = False
            break

    return state


signal.signal(signal.SIGINT, lambda x, y: os._exit(0))


pyautogui.FAILSAFE = False

mouse_control = mouse.Controller()


def open_website(url):
    webbrowser.open(url)


def clear_clipboard():
    if ctypes.windll.user32.OpenClipboard(None):
        ctypes.windll.user32.EmptyClipboard()
        ctypes.windll.user32.CloseClipboard()


def run_command(cmd):
    os.system(cmd)


def open_app(app_path):
    os.startfile(app_path)


def deley(deley):
    time.sleep(deley)


def press_key(key):
    for key in parse_hotkey(key):
        kbd.press(key)
        kbd.release(key)


def clipboardwrite(text):
    clipboard.copy(text)


def click_mouse(button):
    if button == 'left':
        mouse_control.click(mouse.Button.left)
    else:
        mouse_control.click(mouse.Button.right)


def move_mouse(coords):
    x = coords[0]
    y = coords[1]
    pyautogui.moveTo(x, y)


def typewrite(text):
    pyautogui.typewrite(text)


def loop(x):
    macro = x['func']
    iterations = x['iterations']
    for i in range(iterations):
        for action in macro:
            ARG = actions[action['cmd']]['arg']
            function = actions[action['cmd']]['function']

            function(action[ARG])


actions = {
    'OPEN_WEBSITE': {'arg': 'url', 'function': open_website},
    'DELAY': {'arg': 'duration', 'function': deley},
    'RUN_COMMAND': {'arg': 'command', 'function': run_command},
    'PRESS_KEY': {'arg': 'key', 'function': press_key},
    'TYPEWRITE': {'arg': 'text', 'function': typewrite},
    'CLICK_MOUSE': {'arg': 'button', 'function': click_mouse},
    'MOVE_MOUSE': {'arg': 'pos', 'function': move_mouse},
    'LAUNCH_APP': {'arg': 'path', 'function': open_app},
    'LOOP': {'arg': 'x', 'function': loop},
    'CLIPBOARD': {'arg': 'text', 'function': clipboardwrite},
    'DEBUG':{'arg':'message','function':print}


}

toggle_macros = {}


class held_macro:
    def __init__(self, macro_name, key):

        self.macro_name = macro_name
        self.running = False
        self._thread = None
        self.key = key

        self.MACRO = compiler.compile_source(f'macros/{macro_name}.ms')['src']

    def runner(self):
        while True:
            if not is_pressed(self.key):
                self.kill()
            for action in self.MACRO:
                if not is_pressed(self.key):
                    self.kill()
                ARG = actions[action['cmd']]['arg']
                function = actions[action['cmd']]['function']

                function(action[ARG])
                if not is_pressed(self.key):
                    self.kill()

    def kill(self):
        self.running = False
        sys.exit()

    def toggle(self):
        if self.running:
            self.running = False
            self._thread.join()

        else:
            self.running = True
            self._thread = threading.Thread(target=self.runner, daemon=True)
            self._thread.start()


class toggle_macro:
    def __init__(self, macro_name):
        self.macro_name = macro_name
        self.running = False
        self._thread = None

        self.MACRO = MACRO = compiler.compile_source(
            f'macros/{macro_name}.ms')['src']

    def runner(self):
        while True:
            if not self.running:
                sys.exit()
            for action in self.MACRO:
                if not self.running:
                    sys.exit()
                ARG = actions[action['cmd']]['arg']
                function = actions[action['cmd']]['function']

                function(action[ARG])
                if not self.running:
                    sys.exit()

    def toggle(self):
        if self.running:
            self.running = False
            self._thread.join()

        else:
            self.running = True
            self._thread = threading.Thread(target=self.runner, daemon=True)
            self._thread.start()


def run_macro(macro):
    print(CURRENTLY_PRESSED)

    MACRO = compiler.compile_source(f'macros/{macro}.ms')['src']

    for action in MACRO:
        ARG = actions[action['cmd']]['arg']
        function = actions[action['cmd']]['function']
        function(action[ARG])


def load_macros():
    FILE_LIST = os.listdir('macros')
    macro_names = []
    for i in FILE_LIST:
        split = os.path.splitext(f'macros/{i}')
        if split[1] == '.ms':
            macro_names.append(os.path.basename(
                f'macros/{i}').replace('.ms', ''))

    compiled = []
    HOTKEYS = []

    loaded = 0

    for macro in macro_names:
        MACRO_NAME = macro

        try:
            macro_ = compiler.compile_source(f'macros/{MACRO_NAME}.ms')

        except Exception as e:
            print(f'Compiler error in macro {MACRO_NAME}.ms')
            print(e)
            print(f'Type of error {type(e)}')
            continue

        KEY = macro_['key']
        MODE = macro_['run_mode']
        if MODE == 'single':
            HOTKEYS.append(create_hotkey(KEY,run_macro,args=(MACRO_NAME,)))
            # keyboard.add_hotkey(KEY, run_macro, args=(
            #     MACRO_NAME,), suppress=False)

        elif MODE == 'toggle':
            toggle_macros[MACRO_NAME] = toggle_macro(MACRO_NAME)
            HOTKEYS.append(create_hotkey(KEY,lambda x: toggle_macros[x].toggle(), args=(
                MACRO_NAME,)))

        elif MODE == 'while_held':
            toggle_macros[MACRO_NAME] = held_macro(MACRO_NAME, KEY)
            HOTKEYS.append(create_hotkey(KEY, lambda x: toggle_macros[x].toggle(), args=(
                MACRO_NAME,)))

        loaded += 1



    return loaded, len(macro_names),HOTKEYS


def main():
    global CURRENTLY_PRESSED
    num, number_of_macros,HOTKEYS = load_macros()
    if number_of_macros == 0:
        colorlogger.error('No macros found')
    elif num == 0:
        colorlogger.error('No macros were loaded successfully')
    else:
        colorlogger.log(f'Sucsessfully loaded {num} macros')
        with keyboard.GlobalHotKeys(HOTKEYS,force_hotkeys=True) as f:
            CURRENTLY_PRESSED = f.state
            f.join()



if __name__ == "__main__":
    main()
