"""Simulation script for assignment 2.

The script uses the control defined in file `aer1216_fall2020_hw2_ctrl.py`.

Example
-------
To run the simulation, type in a terminal:

    $ python aer1216_fall2020_hw2_sim.py

"""
import time
import random
import numpy as np
import pybullet as p

#### Uncomment the following 2 lines if "module gym_pybullet_drones cannot be found"
# import sys
# sys.path.append('../')

from gym_pybullet_drones.envs.CtrlAviary import CtrlAviary
from gym_pybullet_drones.utils.Logger import Logger
from gym_pybullet_drones.utils.utils import sync
from gym_pybullet_drones.utils.enums import DroneModel
from aer1216_fall2020_hw2_ctrl import HW2Control

DURATION = 50
"""int: The duration of the simulation in seconds."""
GUI = True
"""bool: Whether to use PyBullet graphical interface."""
RECORD = False
"""bool: Whether to save a video under /files/videos. Requires ffmpeg"""

if __name__ == "__main__":

    # Create the ENVironment
    ENV = CtrlAviary(num_drones=1,
                     drone_model=DroneModel.CF2P,
                     initial_xyzs=np.array([ [.0, .0, .15]]), #, [-.3, .0, .15], [.3, .0, .15] 
                     gui=GUI,
                     record=RECORD
                     )
    PYB_CLIENT = ENV.getPyBulletClient()

    # Initialize the LOGGER
    LOGGER = Logger(logging_freq_hz=ENV.SIM_FREQ,
                    num_drones=1,
                    )

    # Initialize the CONTROLLERS
    CTRL = HW2Control(env=ENV,
                        control_type=0
                        )

    # Initialize the ACTION 
    ACTION = {}
    OBS = ENV.reset()
    STATE = OBS["0"]["state"]
    ACTION["0"] = CTRL.compute_control(current_position=STATE[0:3],
                                        current_velocity=STATE[10:13],
                                        current_rpy=STATE[7:10],
                                        target_position=STATE[0:3],
                                        target_velocity=np.zeros(3),
                                        target_acceleration=np.zeros(3)
                                        )

    # Initialize the target trajectory
    TARGET_POSITION = np.array([[0, 4.0*np.cos(0.006*i), 1.0] for i in range(DURATION*ENV.SIM_FREQ)])
    TARGET_VELOCITY = np.zeros([DURATION * ENV.SIM_FREQ, 3])
    TARGET_ACCELERATION = np.zeros([DURATION * ENV.SIM_FREQ, 3])

    # Derive the target trajectory to obtain target velocities and accelerations
    TARGET_VELOCITY[1:, :] = (TARGET_POSITION[1:, :] - TARGET_POSITION[0:-1, :]) / ENV.SIM_FREQ
    TARGET_ACCELERATION[1:, :] = (TARGET_VELOCITY[1:, :] - TARGET_VELOCITY[0:-1, :]) / ENV.SIM_FREQ

    # Run the simulation 
    START = time.time()
    for i in range(0, DURATION*ENV.SIM_FREQ):

        # Step the simulation
        OBS, _, _, _ = ENV.step(ACTION)

        # Compute control for drone 0
        STATE = OBS["0"]["state"]
        ACTION["0"] = CTRL.compute_control(current_position=STATE[0:3],
                                             current_velocity=STATE[10:13],
                                             current_rpy=STATE[7:10],
                                             target_position=TARGET_POSITION[i, :],
                                             target_velocity=TARGET_VELOCITY[i, :],
                                             target_acceleration=TARGET_ACCELERATION[i, :]
                                             )
        # Log drone 0
        LOGGER.log(drone=0, timestamp=i/ENV.SIM_FREQ, state=STATE)

        # Printout
        if i%ENV.SIM_FREQ == 0:
            ENV.render()

        # Sync the simulation
        if GUI:
            sync(i, START, ENV.TIMESTEP)

    # Close the ENVironment
    ENV.close()

    # Save the simulation results
    LOGGER.save()

    # Plot the simulation results
    LOGGER.plot()