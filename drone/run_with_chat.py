"""
run_with_chat.py
================
Launch the Drone2d simulation with the interactive chat panel enabled.

Usage
-----
    python run_with_chat.py

The window is 1100 × 800 px (800 simulation + 300 chat sidebar).

Type commands in the chat panel on the right:
  target <x> <y>   – move the red target dot
  pause            – freeze / resume the simulation
  force <l> <r>    – lock motor thrust values (0–1000)
  force off        – release the force lock
  gravity <g>      – change gravity strength (default 1000)
  reset            – restart the episode
  clear            – clear the console history
  help             – list all commands
"""

import sys
import os

# Allow running from the project root without installing the package
sys.path.insert(0, os.path.dirname(__file__))

import drone_2d_custom_gym_env          # registers the gym env
from drone_2d_custom_gym_env.drone_2d_env import Drone2dEnv
import numpy as np

def main():
    env = Drone2dEnv(
        render_sim=True,
        render_path=True,
        render_shade=True,
        n_steps=2000,
        initial_throw=True,
        chat=True,          # ← enables the chat panel
    )

    obs = env.reset()

    print("Drone simulation running.")
    print("Type commands in the right-hand chat panel.")
    print("Close the window or press Ctrl-C to exit.\n")

    while True:
        # Random agent — replace with your trained model if you have one
        action = env.action_space.sample()
        obs, reward, done, info = env.step(action)
        env.render()

        if done:
            obs = env.reset()


if __name__ == "__main__":
    main()
