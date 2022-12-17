"""
    Implementation of the third layer controller
    according to the hierchical agent architecture
"""

from typing import Any


class Controller:
    _state: Any
    _history: []
    _reverse_count: 0

    def __init__(self):
        self._history = []
        self._reverse_count = 0
        pass

    def plan(self, perceptions):
        """
        Planning algorithm for the robot to navigate
            1. read perceptions
            2. decide a new direction
            3. output the action
        :return:
        """

        # ratio = perceptions[1] / perceptions[0]
        # self._history.append(round(ratio, 2))
        #
        # if len(self._history) > 5: #and all(x == self._history[0] for x in self._history):
        #     # last 5 ratios were equal
        #     print(self._history)
        #     for index, value in self._history:
        #         if index > 0 and self._history[index-1] == self._history[index] and self._history[index] == self._history[index+1]:
        #             print("EQUAL\n\n\n\n\n\n\n\n\n")
        #             return 'reverse'

        # print("ratio:", ratio)
        # if ratio > 1.4:
        #     return 'right'
        # elif ratio < 0.6:
        #     return 'left'
        # return 'forward'

