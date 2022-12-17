"""
    Main Hierchical Controller Agent
    Includes:
        - a VirtualBody communicating with the Body
            through the message broker
        - a Controller comunicatin internally with VirtualBody
"""

from VirtualBody import VirtualBody
from Controller import Controller
import time

MY_PERC_CH = "PERCEPTIONS"  # from the physical body to the virtual body and controller
MY_COMM_CH = "COMMANDS"     # from virtual body to physical


if __name__ == "__main__":
    my_virt_body = VirtualBody(MY_PERC_CH, MY_COMM_CH)
    my_controller = Controller()
    while True:
        percepts = my_virt_body.get_perceptions()
        print("percepts", percepts)
        command = my_controller.plan(percepts)
        print(command)
        my_virt_body.send_command(command)
        time.sleep(0.1)
