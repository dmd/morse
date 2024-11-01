from machine import Pin, Timer
import network
import urequests
import time

TIMEOUT = 10000

morse_code = {
    ".-": "A",
    "-...": "B",
    "-.-.": "C",
    "-..": "D",
    ".": "E",
    "..-.": "F",
    "--.": "G",
    "....": "H",
    "..": "I",
    ".---": "J",
    "-.-": "K",
    ".-..": "L",
    "--": "M",
    "-.": "N",
    "---": "O",
    ".--.": "P",
    "--.-": "Q",
    ".-.": "R",
    "...": "S",
    "-": "T",
    "..-": "U",
    "...-": "V",
    ".--": "W",
    "-..-": "X",
    "-.--": "Y",
    "--..": "Z",
}


class MorseCodeTranslator:
    def __init__(self):
        self.button = Pin(4, Pin.IN, Pin.PULL_UP)
        self.button.irq(
            trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self.button_callback
        )

        self.start_time = 0
        self.current_sequence = ""
        self.current_letter = ""
        self.is_pressing = False
        self.last_activity_time = time.ticks_ms()

        self.timer = Timer(-1)
        self.space_timer = Timer(-1)
        self.timeout_timer = Timer(-1)

        self.start_timeout_timer()

    def button_callback(self, pin):
        self.timer.init(mode=Timer.ONE_SHOT, period=5, callback=self.debounced_callback)

    def debounced_callback(self, timer):
        self.last_activity_time = time.ticks_ms()
        self.restart_timeout_timer()

        if self.button.value() == 0:  # Button pressed
            if not self.is_pressing:
                self.start_time = time.ticks_ms()
                self.is_pressing = True
                self.space_timer.deinit()  # Cancel any pending space insertion
        else:  # Button released
            if self.is_pressing:
                duration = time.ticks_diff(time.ticks_ms(), self.start_time)
                self.current_letter += "-" if duration > 150 else "."
                self.is_pressing = False
                self.timer.init(
                    mode=Timer.ONE_SHOT, period=500, callback=self.process_input
                )
                self.space_timer.init(
                    mode=Timer.ONE_SHOT, period=1500, callback=self.insert_space
                )

    def process_input(self, timer):
        if self.current_letter:
            if self.current_letter in morse_code:
                decoded_letter = morse_code[self.current_letter]
                self.current_sequence += decoded_letter
                print(decoded_letter, end="")
            self.current_letter = ""

    def insert_space(self, timer):
        if self.current_sequence and self.current_sequence[-1] != " ":
            self.current_sequence += " "
            print(" ", end="")

    def start_timeout_timer(self):
        self.timeout_timer.init(
            mode=Timer.PERIODIC, period=1000, callback=self.check_timeout
        )

    def restart_timeout_timer(self):
        self.timeout_timer.deinit()
        self.start_timeout_timer()

    def check_timeout(self, timer):
        if time.ticks_diff(time.ticks_ms(), self.last_activity_time) > TIMEOUT:
            try:
                if self.current_sequence:
                    postit(self.current_sequence)
            except:
                print("uh oh, didn't post")
            self.current_sequence = ""
            self.last_activity_time = time.ticks_ms()


def postit(message):
    print(f"sending: {message}")
    urequests.post("https://yourdomain.com/morse/", data=message)


print("Connecting to wifi", end="")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("your wifi network", "your wifi password")
while not wlan.isconnected():
    print(".", end="")
    time.sleep(0.1)
print(" Connected!")

morse_translator = MorseCodeTranslator()
while True:
    time.sleep(1)
