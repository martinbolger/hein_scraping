#!/usr/bin/env python
"""create_directories.py

This module contains a function that creates the
data directories. The paths are
relative to the location of the modules folder,
so this should run on any computer.
"""

import pathlib
import os
from datetime import date


__author__ = "Martin Bolger"
__date__ = "December 28th, 2020"

def create_directories():
    # Get the current date
    today = date.today()
    cur_date = today.strftime("%Y%m%d")
    base_path = pathlib.Path(__file__).parents[2]
    data_path = base_path / "data"
    # Create directories
    os.mkdir(data_path / cur_date)
    os.mkdir(data_path / cur_date / "a_working")
    os.mkdir(data_path / cur_date / "b_intermediate")
    os.mkdir(data_path / cur_date / "c_output")

if __name__ == "__main__":
    create_directories()
