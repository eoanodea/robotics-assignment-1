"""
    Implementation of the VirtualBody class of the Agent
"""

import logging
from typing import Any, List
import time
import redis
import json

from Body import Body

MY_PERC_CH = "PERCEPTIONS"  # from the physical body to the virtual body and controller
MY_COMM_CH = "COMMANDS"     # from virtual body to physical


class VirtualBody(Body):

    def __init__(self, perception_channel, commands_channel):
        self._my_perc_ch = perception_channel
        self._my_comm_ch = commands_channel
        self._my_msg_broker = redis.Redis(decode_responses=True)
        self._my_perceptions = None
        try:
            print(self._my_msg_broker.info())
            self._pub_sub = self._my_msg_broker.pubsub()
            self._pub_sub.subscribe(self._my_perc_ch)
            msg = None
            while not msg:
                msg = self._pub_sub.get_message()
                time.sleep(0.1)
                print("Still waiting..")
            print("subscribed: ", msg, "to", self._my_perc_ch)
        except Exception as e:
            logging.exception(e)
            print(e)
            raise e

    def get_perceptions(self):
        while True:
            msg = self._pub_sub.get_message()
            if msg:
                self._my_perceptions = json.loads(msg['data'])
                return self._my_perceptions
            time.sleep(0.1)

    def plan(self, perceptions):
        """
        Planning algorithm for the robot to navigate
            1. read perceptions
            2. decide a new direction
            3. output the action
        :return:
        """

        print(round(perceptions[0], 3), round(perceptions[1], 3), round(perceptions[2], 3),round(perceptions[3], 3),round(perceptions[4], 3),round(perceptions[5], 3))
        if perceptions[2] < 0.04 and perceptions[3] < 0.04:
            print('forward')
            return 'forward'
        if (perceptions[0] == 0 and perceptions[1] < 0.07) or perceptions[1] == 0:
            print('left')
            return 'left'
        if (perceptions[5] == 0 and perceptions[4] < 0.07) or perceptions[4] == 0:
            print('right')
            return 'right'
        print('forward')
        return 'forward'

        # This worked before but maybe before the walls were made dynamic
        # if perceptions[2] < 0.02 and perceptions[3] < 0.02:
        #     return 'forward'
        # if perceptions[1] == 0 and perceptions[2] < 0.5 and perceptions[3] < 0.5:
        #     return 'left'
        # if perceptions[6] == 0 and perceptions[5] < 0.5 and perceptions[4] < 0.5:
        #     return 'right'
        # return 'forward'

        # ratio = perceptions[1] / perceptions[0]
        # print("ratio:", ratio)
        # if ratio > 1.4:
        #     return 'right'
        # elif ratio < 0.6:
        #     return 'left'
        # return 'forward'

    def send_command(self, command):
        try:
            self._my_msg_broker.publish(self._my_comm_ch, command)
        except Exception as e:
            print(e)
            raise e


if __name__ == "__main__":
    my_virt_body = VirtualBody(MY_PERC_CH, MY_COMM_CH)
    while True:
        percepts = my_virt_body.get_perceptions()
        # print(percepts)
        command = my_virt_body.plan(percepts)
        # print(command)
        my_virt_body.send_command(command)
        time.sleep(0.1)