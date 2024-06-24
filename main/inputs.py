import time
import ctypes

PUL = ctypes.POINTER(ctypes.c_ulong)
KEYCODE_MAPPINGS = {
    "Esc": 0x01,
    "Backspace": 0x0e,
    "Tab": 0x0f,
    "Ctrl": 0x1d,
    "Shift": 0x2a,
    "Space": 0x39,
    "LmbDown":0x0002,
    "RmbDown":0x0008,
    "LmbUp":0x0004,
    "RmbUp":0x0010,
    "1": 0x02,
    "2": 0x03,
    "3": 0x04,
    "4": 0x05,
    "5": 0x06,
    "6": 0x07,
    "7": 0x08,
    "8": 0x09,
    "9": 0x0a,
    "0": 0x0b,
    "Q": 0x10,
    "W": 0x11,
    "E": 0x12,
    "R": 0x13,
    "T": 0x14,
    "Y": 0x15,
    "U": 0x16,
    "I": 0x17,
    "O": 0x18,
    "P": 0x19,
    "A": 0x1e,
    "S": 0x1f,
    "D": 0x20,
    "F": 0x21,
    "G": 0x22,
    "H": 0x23,
    "J": 0x24,
    "K": 0x25,
    "L": 0x26,
    "Z": 0x2c,
    "X": 0x2d,
    "C": 0x2e,
    "V": 0x2f,
    "B": 0x30,
    "N": 0x31,
    "M": 0x32,
}

class KBI(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class MI(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class II(ctypes.Union):
    _fields_ = [("ki", KBI),
                ("mi", MI)]


class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", II)]

class input_manager():

    def __init__(self):
        pass

    def move_mouse(self, x, y):
        extra = ctypes.c_ulong(0)
        ii_ = II()
        ii_.mi = MI(x, y, 0, 0x0001, 0, ctypes.pointer(extra))
        command = Input(ctypes.c_ulong(0), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(command), ctypes.sizeof(command))

    def press_key(self, key):
        key = KEYCODE_MAPPINGS[key]
        extra = ctypes.c_ulong(0)
        ii_ = II()
        ii_.ki = KBI(0, key, 0x0008, 0, ctypes.pointer(extra))
        command = Input(ctypes.c_ulong(1), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(command), ctypes.sizeof(command))

    def release_key(self, key):
        key = KEYCODE_MAPPINGS[key]
        extra = ctypes.c_ulong(0)
        ii_ = II()
        ii_.ki = KBI(0, key, (0x0008 | 0x0002), 0, ctypes.pointer(extra))
        command = Input(ctypes.c_ulong(1), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(command), ctypes.sizeof(command))

    def tap_key(self, key, duration = 0):
        self.press_key(key)
        if duration > 0:
            time.sleep(duration)
        self.release_key(key)

    def mouse_down(self, left):
        extra = ctypes.c_ulong(0)
        ii_ = II()
        ii_.mi = MI(0, 0, 0, KEYCODE_MAPPINGS["LmbDown"] if left else KEYCODE_MAPPINGS["RmbDown"], 0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(0), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    def mouse_up(self, left):
        extra = ctypes.c_ulong(0)
        ii_ = II()
        ii_.mi = MI(0, 0, 0, KEYCODE_MAPPINGS["LmbUp"] if left else KEYCODE_MAPPINGS["RmbUp"], 0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(0), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    def click(self, left, duration=0):
        self.mouse_down(left)
        if duration > 0:
            time.sleep(duration)
        self.mouse_up(left)