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


import re
import Class as cl
#from build_RC_tree import build_RC_tree
from build_path import build_path
from build_path import parse_net
import via_section_def_parser as def_via
from lefParser import compute_via_number_of_cuts
import global_var as glob


def def_parser(def_file, pins, nets, cell_coor_dict, load_cap_dict, cell_dimension, buildPath = True):
    print('# READING DEF')
    with open(def_file) as f:
        blocks = []
        mapping_number = 1
        
        # Parsing Components Section
        parsing_component = False
        comp_syn = False
        cur_comp =[]
        
        # NET BOOLEAN
        find_net = False
        find_data = False
        
        # PIN BOOLEAN
        find_pin = False
        pin_info = False
        
        # VIAS BOOLEAN
        find_vias = False
        via_info = False
        
        for line in f:
            """ HEADER SECTION"""
            # Finding the PER UNIT VALUE
            if re.search('UNITS DISTANCE MICRONS',line,flags=re.IGNORECASE):
                data = re.findall(r'\d+', line)
                glob.UNIT_DISTANCE = (int(data[0]))
            
            if re.match('^VERSION\s*(\d+\.?\d*)\s*[;]', line):
                def_version = re.match('^VERSION\s*(\d+\.?\d*)\s*[;]', line).group(1)
            
            if re.match('^DIVIDERCHAR\s*["](.+)["]\s*[;]', line):
                glob.DIVIDER = re.match('^DIVIDERCHAR\s*["](.+)["]\s*[;]', line).group(1)               
                
            if re.match('^BUSBITCHARS\s*["](.+)["]\s*[;]', line):
                glob.BUS_CHAR = re.match('^BUSBITCHARS\s*["](.+)["]\s*[;]', line).group(1)
            
            if re.match('^DESIGN\s*\w+\s*[;]', line):
                glob.DESIGN = re.match('^DESIGN\s*(\w+)\s*[;]', line).group(1)
                
            """" END HEADER SECTION """
            
            """FILLING THE FIRST PART OF THE RECT CLASS"""
            if re.match('^[\t ]*COMPONENTS \d+',line, flags=re.IGNORECASE):
                parsing_component = True
                continue
            
            if re.match('^[\t ]*END COMPONENTS',line, flags=re.IGNORECASE):
                parsing_component = False
                # Create dictionary that contains all the COMPONENTS info
                create_block_dict(blocks, load_cap_dict, cell_dimension, cell_coor_dict)
                continue

            if parsing_component:
                if re.match('^[\t ]*-[\t ]+\w+[\t ]+\w+',line):
                    comp_name = re.search(r'[\t ]*-[\t ]+(\w+)[\t ]+(\w+)', line)
                    cur_comp = cl.Component(name = comp_name.group(1), cell=comp_name.group(2), number = mapping_number)
                    comp_syn = True
                    mapping_number += 1 
                
                if re.search('PLACED|FIXED|COVER',line,flags=re.IGNORECASE) and comp_syn:
                    comp_loc = re.search(r'[+] (PLACED|FIXED|COVER)\s+[(] ([-+]?\d+\.?\d*)\s+([-+]?\d+\.?\d*) [)] (\w+)', line)
                    cur_comp.set_location(comp_loc.group(2), comp_loc.group(3))
                    cur_comp.set_orientation(comp_loc.group(4))
                    
                if re.search('PLACED|FIXED|COVER',line,flags=re.IGNORECASE) and comp_syn:
                    Property = re.search(r'[+] (PROPERTY)\s+(\w+)\s+([-+]?\d+\.?\d*|\w+)', line)
                    if Property != None:
                        cur_comp.set_property([Property.group(2), Property.group(3)])
                        
                if re.search(';',line) and comp_syn: #semicolon at the begining of the line
                    comp_syn = False
                    blocks.append(cur_comp)
         
            """ FIRST PART ENDS HERE """

            """ PINS START """
            if re.match('^[\t ]*PINS \d+',line, flags=re.IGNORECASE):
                find_pin = True
                continue
             
            if re.match('^[\t ]*END PINS*',line, flags=re.IGNORECASE):
                find_pin = False
                continue
            
            if find_pin:
                if re.match('^\s*-\s+(\w+)',line):
                    pin_info = True
                    pin_class = cl.Pin(number = mapping_number)
                    pin_class.set_name(re.match('^\s*-\s+(\S+)\s*',line).group(1))
                    mapping_number += 1
                    
                if pin_info:
                    if re.match('. .+',line):
                        data = re.findall(r'(?![(|)|+|;])\S+', line)
                        processPinData(pin_class, data)
                    
                if re.search(';',line):
                    pin_info = False
                    add_pin_info_toDict(pin_class, pins)
                    continue

            """ END PINS """
        
            """ VIAS SECTION """
            if find_vias:
                if re.search(r';', line):
                    via_info = False
                    # Set the cut layer of the via
                    num_cuts = compute_via_number_of_cuts(cur_via, glob.TECH_LEF_DICT)
                    cur_via.set_viaCuts(num_cuts)
                    def_via.append_via_data_to_dict(cur_via, glob.TECH_LEF_DICT)
                
                if via_info:
                    def_via.parse_def_via_section(line, cur_via, glob.TECH_LEF_DICT)
                    
                if re.match(r'^\s*[-]\s+(\w+)', line):
                    via_name = re.findall(r'\S+', line)
                    via_name = (via_name[1])
                    cur_via = cl.LEF_VIA_Info(via_name = via_name)
                    via_info = True
                    
            if re.match('^VIAS\s+\d+\s+[;]', line):
                find_vias = True
                
            if re.match('^END VIAS*', line):
                find_vias = False
            
            """ END VIA SECTION """
            
            """ NETS PART """
            if re.match('^[\t ]*NETS \d+',line, flags=re.IGNORECASE):
                find_net = True
                print('# Process Nets information...')
                net_count = 0
                continue
             
            if re.match('^[\t ]*END NETS*',line, flags=re.IGNORECASE):
                find_net = False
                print('# Finsihed processing Nets information')
                print('# Total Net Count: {}'.format(net_count))
                continue
                
            if find_net == True:
                if re.match('^[\t ]*-[\t ]+\w+',line):
                    mapped = False
                    data = re.findall(r'\S+', line)
                    # Create an Instance of a net
                    cur_net = cl.NET(data[1]) 
                    cur_net.add_cell = blocks
                    # ADDING THE MAPPING NUMBER OF THE NET TO THE PIN INFO
                    if data[1] in pins:
                        cur_net.number = pins[data[1]]['number']
                        mapped = True
                        
                    if not mapped:
                        cur_net.number = mapping_number
                        mapping_number += 1
                        
                    find_data = True
            
                # End of the particular NET, process the wire data
                if re.search('^\s*;',line): #semicolon at the begining of the line
                    find_data = False
                    net_count += 1
                    if cur_net.wire_list == []:
                        nets.append(cur_net)
                        print('# Warning: Net {} does not contain any interconnect information!'.format(cur_net.name))
                        continue
                    
                    # Use for SPEF writer, creating PATH from DEF
                    if buildPath:
                        build_path(cur_net, cell_coor_dict, pins)
                        
                    nets.append(cur_net)
                    continue
                
                if find_data:
                   parse_net(line, cur_net, cell_coor_dict)
                           
            """ END NETS """
            
#    if buildPath:
#        import multiprocessing as mp
#        print('# Building Path ...')
#        processes = []
#        end = 0
#
#        cpu_count = mp.cpu_count() + 10
#        for i in range (cpu_count):
#            start = end
#            
#            if i == cpu_count-1:
#                end = len(nets)
#            else:
#                end = (i+1) * int(len(nets)/cpu_count)
#                
#            p = mp.Process(target=fork_build_path, args=(start, end, nets, cell_coor_dict, pins,))
#            processes.append(p)
#            p.start()
#
#        for process in processes:
#            process.join()
            
    print('# Finish Rading DEF')
# =============================================================================
# Desc: Determine whether the cell is an input or output
#   Input: The NET class object and the data itself
# =============================================================================
def create_block_dict(blocks, load_cap_dict, cell_dimension, cell_coor_dict):
    for block in blocks:
        cell_coor_dict[block.compName] = {'x' : block.x, 'y' : block.y, 'number' : block.number, 'cell_name' : block.type,
                      'pin' : load_cap_dict[block.type], 'orient' : block.orient, 'dimension' : cell_dimension[block.type]}

    ### EMPTY THE DICTIONARY
    del cell_dimension
    del load_cap_dict

# =============================================================================
#                 
# =============================================================================
def processPinData(pin_class, data):
    for i in range (0, len(data)):
        if re.search('NET', data[i]):
            pin_class.set_net(data[i+1])
            i += 1
            continue
        
        if re.search('DIRECTION', data[i]):
            pin_class.set_direction(data[i+1])
            i += 1    
            continue
        
        if re.search('LAYER', data[i]):
            add = 1
            if data[i+2] == 'MASK' or data[i+2] == 'SPACING' or data[i+2] == 'DESIGNRULEWIDTH':
                add = 3
                
            pin_class.set_layer(data[i+1])
            pin_class.set_dimension([data[i+add+1], data[i+add+2], data[i+add+3], data[i+add+4]])
            i += (add + 4)
            continue
            
        if re.search('COVER|FIXED|PLACED', data[i]):
            pin_class.set_x(data[i+1])
            pin_class.set_y(data[i+2])
            pin_class.set_orientation(data[i+3])
            i += 3
            continue
            
def add_pin_info_toDict(pin_class, pin_dict):
    pin_dict[pin_class.name] = {'NET' : pin_class.net, 'DIRECTION' : pin_class.direction, 'LAYER' : pin_class.layer, 
            'X' : pin_class.x, 'Y' : pin_class.y, 'dimension' : pin_class.dimension,
            'orientation' : pin_class.orientation, 'number' : pin_class.number }

def processPropertyInfo(cur_net, data):
    for i in range (1, len(data)-1, 2):
        cur_net.set_property([data[i], data[i+1]])
        
def fork_build_path(start, end, nets, cell_coor_dict, pins,):
    for i in range (start,end):
        if nets[i].wire_list == []:
            continue
        build_path(nets[i], cell_coor_dict, pins)
