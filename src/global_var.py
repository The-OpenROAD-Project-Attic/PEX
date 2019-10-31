"""
Author: Geraldo Pradipta

BSD 3-Clause License

Copyright (c) 2019, The Regents of the University of Minnesota

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
© 2019 GitHub, Inc.
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

# There is an option makefile = True --> for testing purposes, where DEF, etc information are 
# given ( do not need to parse and process the data because the input data has been process in form
# of a text file) in order to reduce the run time
def initialize(makefile = True):
    global DIVIDER, BUS_DELIMITER, UNIT_DISTANCE, DESIGN, VENDOR, VERSION, PROGRAM, SPEF_VER,\
        DELIMITER, TIME_UNIT, CAP_UNIT, RES_UNIT, INDUCTANCE_UNIT, TECH_LEF_DICT, DEF_DIR, \
        TECH_LEF_DIR, MARCRO_LEF_DIR, CONFIG_FILE_DIR, BC_LIB_DIR, WC_LIB_DIR, LIB_DIR
        
    DIVIDER = '/'
    BUS_DELIMITER = '[]'
    DELIMITER = ':'
    UNIT_DISTANCE = 0
    DESIGN = ""
    VENDOR = "OpenROAD"
    VERSION = "0.1"
    PROGRAM = "OpenROAD-PEX"
    SPEF_VER = "IEEE 1481-1998"
    TIME_UNIT = 'NS'
    CAP_UNIT = 'PF'
    RES_UNIT = 'OHM'
    INDUCTANCE_UNIT = 'HENRY'
    TECH_LEF_DICT = {}
    
    if makefile:
        assert 'DEF_DIR' in os.environ, 'Error - Please provide the DEF_DIR in the Makefile'
        assert 'TECH_LEF_DIR' in os.environ, 'Error - Please provide the TECH_LEF_DIR in the Makefile'
        assert 'MARCRO_LEF_DIR' in os.environ, 'Error - Please provide the MARCRO_LEF_DIR in the Makefile'
        assert 'CONFIG_FILE_DIR' in os.environ, 'Error - Please provide the CONFIG_FILE_DIR in the Makefile'
        # Environment Variable
        DEF_DIR = os.environ['DEF_DIR']
        TECH_LEF_DIR = os.environ['TECH_LEF_DIR']
        MARCRO_LEF_DIR = os.environ['MARCRO_LEF_DIR'].split()
        CONFIG_FILE_DIR = os.environ['CONFIG_FILE_DIR']
        LIB_DIR = os.environ['LIB_DIR'].split()