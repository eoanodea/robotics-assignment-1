"""
    Implementation of the Body class of the Agent
"""

import logging
from zmqRemoteApi import RemoteAPIClient
from typing import Any, List
import time
import redis
import json
import random


MY_PERC_CH = "PERCEPTIONS"  # from the physical body to the virtual body and controller
MY_COMM_CH = "COMMANDS"     # from virtual body to physical
FREE_SPACE = 1
ROTATION_DELAY = 0.05


class Body:
    _my_sensors: set
    _my_actuators: List
    _my_name: str
    _my_perceptions: set

    def __init__(self, name, robot_sens_array, robot_act_array):
        logging.info(f"Agent name: {name} initialized.")
        self._my_name = name
        self._my_sensors = robot_sens_array
        self._my_actuators = robot_act_array

    def __repr__(self):
        out = f"{self._my_name}: I have {len(self._my_sensors)} sensors and {len(self._my_actuators)} list of actuators"
        return out

    def perceive(self, stimuli):
        # transform stimuli from sensors into perceptions
        for s in stimuli:
            self._my_perceptions.add(...)
        pass

    def step(self, t: int):
        # called by the simulator at each simulation step
        logging.info(f"{self._my_name}: agent body step at time {t}")
        stimuli = [s.get_value() for s in self._my_sensors]
        logging.info(f"{self._my_name}: stimuli at time {t} -> {stimuli}")
        self.perceive(stimuli)
        logging.info(f"{self._my_name}: perceptions at time {t} -> {self._my_perceptions}")
        # how about command?

    def get_perceptions(self):
        return self._my_perceptions


"""
    Simulated body class to pilot the simulated robot inside
    the simulator (CoppeliaSim)
"""


MY_ABILITIES = ['left', 'forward', 'right', 'stop']


class SimulatedPioneerBody(Body):
    _sim: Any
    _cSim_client: Any
    _my_sensors: List
    _my_actuators: List
    _my_perceptions: List

    def __init__(self, name: str, perceptions_channel, commands_channel):
        self._my_name = name
        self._my_perc_ch = perceptions_channel
        self._my_comm_ch = commands_channel
        # zmqRemoteApi connection
        self._cSim_client = RemoteAPIClient()
        self._sim = self._cSim_client.getObject('sim')
        self._my_actuators = []

        # Get handles
        motors = [self._sim.getObject("./leftJoint"),
                  self._sim.getObject("./rightJoint")]

        self._my_actuators.append(motors)
        self._my_sensors = []
        front_sensors = [
            self._sim.getObject("./proxSensor[0]"),
            self._sim.getObject("./proxSensor[1]"),
            self._sim.getObject("./proxSensor[2]"),
            self._sim.getObject("./proxSensor[3]"),
            self._sim.getObject("./proxSensor[4]"),
            self._sim.getObject("./proxSensor[5]"),
            # self._sim.getObject("./proxSensor[6]"),
            # self._sim.getObject("./proxSensor[7]"),
        ]

        self._my_sensors.append(front_sensors)
        back_sensors = [

        ]
        self._my_sensors.append(back_sensors)
        self._my_msg_broker = redis.Redis(decode_responses=True)
        self._my_perceptions = []
        try:
            print(self._my_msg_broker.info())
            self._pub_sub = self._my_msg_broker.pubsub()
            self._pub_sub.subscribe(self._my_comm_ch)
            msg = None
            while not msg:
                msg = self._pub_sub.get_message()
                time.sleep(0.1)
                print("Still waiting..")
            print("subscribed: ", msg, "to", self._my_comm_ch)
        except Exception as e:
            logging.exception(e)
            print(e)
            raise e

    def act(self, motor_speeds: List[float]):
        """
        Set the current speed to all motors of the (simulated) robot
        :param motor_speeds: list of values for motors
        :return: True if everything is ok
        """
        try:
            assert len(motor_speeds) == len(self._my_actuators[0])
            for i, speed in enumerate(motor_speeds):
                self._sim.setJointTargetVelocity(self._my_actuators[0][i], motor_speeds[i])
            return True
        except Exception as e:
            print(e)
            logging.exception(e)
            return False

    def _percept(self, sens_f_values: List) -> List[Any]:
        """
        Heuristic function
        For the Pioneer robot, let's find the most FREE-SPACE around
        1 arrays of 8 floating numbers, for front
        weights of sensor positions:
        -4 -3 -2 -1 0 1  2  3  4 weights
        0   1  2  3 | 4  5  6  7 sensor index
        return:
        (f_l, f_r) were f_l is the free space force to the left
                   f_r is the free space force to the right
        """

        return sens_f_values

        l_force, r_force = 0, 0
        n = len(sens_f_values)
        # left segment of the sensor array
        for xi in range(n // 2):
            if sens_f_values[xi] == 0.0:
                l_force += FREE_SPACE * (4 - xi)
            else:
                l_force += sens_f_values[xi]
        # right segment
        for xi in range(n // 2):
            if sens_f_values[xi + 4] == 0.0:
                r_force += FREE_SPACE * (xi + 1)
            else:
                r_force += sens_f_values[xi]
        print("forces: ", l_force, r_force)
        return l_force, r_force

    def _read_sensors(self, i: int):
        # i = 0 : front sensors
        # i = 1 : back sensors
        assert 0 <= i <= 1, "incorrect sensor array"
        values = []
        for sens in self._my_sensors[i]:
            _, dis, _, _, _ = self._sim.readProximitySensor(sens)
            values.append(dis)
        return values

    def sense(self):
        """
        Read from (simulated-)hardware sensor devices and store into the internal array
        :return: True if all right, else hardware problem

        readProximitySensor:
        int result,float distance,list detectedPoint,int detectedObjectHandle,list detectedSurfaceNormalVector=sim.readProximitySensor(int sensorHandle)
        """
        try:
            front_values = self._read_sensors(0)  # only fron sensors
            print("front: ", front_values)
            self._my_perceptions = self._percept(front_values)
            return True
        except Exception as e:
            print(e)
            logging.exception(e)
            return False

    def send_perceptions(self):
        # send the calculated perceptions to the virtual body
        # print(self._my_perceptions)
        data_msg = json.dumps(self._my_perceptions)
        self._my_msg_broker.publish(MY_PERC_CH, data_msg)

    def receive_command(self):
        """
        receive the command string from the message broker
        :return:
        """
        msg = self._pub_sub.get_message()
        if msg:
            command = msg['data']
            return command

    def execute(self, command):
        assert command in MY_ABILITIES, f"cannot execute {command}"
        delay = random.uniform(ROTATION_DELAY * 0.9, ROTATION_DELAY * 1.1)
        if command == 'left':
            self.act([-1, 1])
            time.sleep(delay)
            self.act([0, 0])
        elif command == 'right':
            self.act([1, -1])
            time.sleep(delay)
            self.act([0, 0])
        elif command == 'forward':
            self.act([1, 1])
        elif command == 'stop':
            self.act([0, 0])
        print(f"command {command} executed")

    def start(self):
        self._sim.startSimulation()

    def stop(self):
        self._sim.stopSimulation()


if __name__ == "__main__":
    my_body = SimulatedPioneerBody("pilot", MY_PERC_CH, MY_COMM_CH)
    print(my_body)
    my_body.start()
    my_body.execute('stop')  # robot shall not move before doing any sensing
    while True:
        my_body.sense()
        my_body.send_perceptions()  # sending through the message broker to the virtual body
        command = my_body.receive_command()  # from the virtual body
        if command:
            my_body.execute(command)
    my_body.stop()
    print("Done.")