import time
import sys
import yaml
from typing import Dict
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient

import robonomicsinterface as rbi
from utils import h256_to_string
from substrateinterface import KeypairType

ROBOT_INTERFACE = 'eth0'

class UnitreeRobonomics:
    def __init__(self, robonomics_params_path):

        # Initialize robot interface
        ChannelFactoryInitialize(0, ROBOT_INTERFACE)

        # Prepare high level control client
        self.loco_client = LocoClient()
        self.loco_client.SetTimeout(10.0)
        self.loco_client.Init()

        self.loco_client.Damp()

        with open(robonomics_params_path, 'r') as robonomics_config_file:
            pubsub_params_dict: Dict = yaml.load(robonomics_config_file, Loader=yaml.SafeLoader)

        # Load all params
        account_seed: str = pubsub_params_dict['account_seed']
        self._remote_node_url: str = pubsub_params_dict['remote_node_url']
        self._account_type: str = pubsub_params_dict['crypto_type']

        # Checking the type of account
        if self._account_type == 'ED25519':
            crypto_type: int = KeypairType.ED25519
        elif self._account_type == 'SR25519':
            crypto_type: int = KeypairType.SR25519
        else:
            crypto_type: int = -1

        # Creating account
        try:
            self.__account = rbi.Account(
                seed=account_seed,
                remote_ws=self._remote_node_url,
                crypto_type=crypto_type)
        except ValueError as e:
            print("Problem with account creation: %s" % str(e))
            sys.exit(-1)

        print("Connected to Robonomics via: %s" % self.__account.remote_ws)

        account_address: str = self.__account.get_address()
        print('My address is %s' % account_address)

        # Create subscription of launches for Robonomics node account itself
        robonomics_launch_subscriber = rbi.Subscriber(
            self.__account,
            rbi.SubEvent.NewLaunch,
            addr=account_address,
            subscription_handler=self.receive_launch_callback,
        )

    def receive_launch_callback(self, launch_raw_data: tuple[str, str, str]) -> None:
        """
        Event handler when launch appears
        :param launch_raw_data: tuple with addresses and launch parameter
        :return: None
        """
        launch_sender_address: str = launch_raw_data[0]
        launch_param: str = launch_raw_data[2]

        print("Getting launch from %s..." % launch_sender_address)

        try:
            received_param = h256_to_string(launch_param)
            print("Launch param content: %s" % received_param)

            if received_param == '0':
                # 0x3000000000000000000000000000000000000000000000000000000000000000
                self.loco_client.WaveHand()
                print('Robot is waving hand')
                time.sleep(1)
            elif received_param == '1':
                # 0x3100000000000000000000000000000000000000000000000000000000000000
                self.loco_client.WaveHand(True)
                print('Robot is waving hand with a turn')
                time.sleep(1)
            elif received_param == '2':
                # 0x3200000000000000000000000000000000000000000000000000000000000000
                self.loco_client.ShakeHand()
                time.sleep(3)
                self.loco_client.ShakeHand()
                print('Robot is shaking hand')
                time.sleep(1)
            else:
                print('Unknown command to robot')

        except Exception as e:
            print('Launch receiving failed with exception: %s' % str(e))

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Error: Please, provide Robonomics params file")
        sys.exit(-1)

    params_path = sys.argv[1]
    print("Starting the robot client")
    unitree_robonomics = UnitreeRobonomics(params_path)

    # Main loop
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Closing the program")