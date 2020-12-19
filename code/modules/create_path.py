#!/usr/bin/env python
"""create_path.py

This module contains a function that creates the
paths to the data directories. The paths are
relative to the location of the modules folder,
so this should run on any computer.
"""

import pathlib

__author__ = "Martin Bolger"
__date__ = "December 19th, 2020"

def create_path():
    base_path = pathlib.Path(__file__).parents[2]
    input_path = base_path / "_input"
    work_path = base_path / "a_working"
    intr_path = base_path / "b_intermediate"
    out_path = base_path / "c_output"
    return input_path, work_path, intr_path, out_path

if __name__ == "__main__":
    input_path, work_path, intr_path, out_path = create_path()
    print(input_path)
