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

"""
Goals:   1. Parse the LEF to obtain the dimension of all cells
         2. Parse PVT libraries to obtain the load capcitance of the cell  
"""

import re
import json 
from argparse import ArgumentParser
import sys
import glob
import os
import Class as cl

def parse_lef(filename, tech_lef = None, look_for_cell = None, find_desired_cell_info = False):
    lef = {}
    with open (filename, 'r') as lef_file:
        search = False
        find_pin_info = False
        find_layer_info = False 
        find_poly_coordinate = False
        find_rect_coordinate = False
        find_poly_info = False
        
        macro = None
        desired_macro = None
        
        macros = []
        pin_name = ''
        
        for line in lef_file:
            if re.search(r'^\s*MACRO', line, flags=re.IGNORECASE):
                macro = None
                cell_name = re.search(r'MACRO (\w+)', line, flags=re.IGNORECASE)
                cell_name = cell_name.group(1)
                if cell_name != None or cell_name != '':
                    search = True
                    
                if look_for_cell != None:
                    if cell_name == look_for_cell:
                        find_desired_cell_info = True
                        macro = cl.MACRO(cell_name)
                        
                    else:
                        find_desired_cell_info = False
                    
                if find_desired_cell_info:
                    macro = cl.MACRO(cell_name)

            if search and re.match('^\s*END\s+' + re.escape(cell_name), line):
                if cell_name == look_for_cell:
                    find_desired_cell_info = False
                    desired_macro = macro
                if find_desired_cell_info:
                    macros.append(macro)
                search = False
                
            if search:  
                if re.search(r'SIZE\s*\d+\.?\d*\sBY', line):
                    ## Search for the dimension of the cell
                    size = re.search(r'SIZE (\d+\.?\d*) BY (\d+\.?\d*)', line)
                    ## Input the dimension to the dictionary
                    lef[cell_name] = { 'x' : size.group(1), 'y' : size.group(2)}
                    ## Insert the info to the class
                    if look_for_cell != None:
                        if cell_name == look_for_cell:
                            macro.set_width(float(size.group(1)))
                            macro.set_height(float(size.group(2)))

                if re.match(r'^\s*PIN\s+(\w+)', line) and find_desired_cell_info:
                    pin_name = re.match(r'^\s*PIN\s+(\w+)', line).group(1)
                    find_pin_info = True
                    cl_pin = cl.MACRO_PIN(pin_name)

                if find_desired_cell_info and re.match(r'^\s*END\s+' + re.escape(pin_name), line) and find_pin_info:
                    find_pin_info = False
                    
                if find_pin_info:
                    if re.match(r'^\s*DIRECTION\s+(\w+)\s+;', line):
                        direction = re.match(r'\s*DIRECTION\s+(\w+)\s+;', line).group(1)
                        if direction == 'INPUT' or direction == 'OUTPUT':
                            find_layer_info = True
                            cl_pin.set_direction(direction)
                            lef[cell_name][pin_name] = []
             
                        else:
                            find_layer_info = False
                            
                    if find_layer_info:
                        if re.match(r'^\s*LAYER\s+(\w+)\s+;', line):
                            metal = re.match(r'^\s*LAYER\s+(\w+)',line).group(1)
                            if (tech_lef != None and tech_lef['Layer'][metal]['type'] != 'CUT') or metal == 'M1':
                                find_poly_info = True
                                coordinate = []
                        
                        if re.match(r'^\s*END', line):
                            find_poly_info = False
                            
                        if find_poly_info:
                            if re.search('POLY', line):
                                cl_pin._isRect = False  
                                find_poly_coordinate = True
                                
                            if re.search('RECT', line):
                                cl_pin._isRect = True
                                find_rect_coordinate = True
                                
                            if find_poly_coordinate:
                                coordinate.extend(re.findall('([-+]?\d*\.?\d+)+', line))
                                if look_for_cell == cell_name:
                                    cl_pin.set_coordinate(coordinate)
                                
                            if find_rect_coordinate:
                                rect_pattern = r'^\s*(RECT)\s+(\s*MASK\s*\d+\s*)?(\d*\.?\d+\s*)(\d*\.?\d+\s*)(\d*\.?\d+\s*)(\d*\.?\d+\s*)\s*;'
                                coordinate = re.search(rect_pattern, line)
                                coordinate = [coordinate.group(1),metal,coordinate.group(3),\
                                              coordinate.group(4),coordinate.group(5),coordinate.group(6)]
                                
                                lef[cell_name][pin_name].append(coordinate)
                                if len(coordinate) > 4:
                                    coordinate = coordinate[-4:]
                                
                                cl_pin.set_coordinate(coordinate)
                            
                            if re.search(';', line) and (find_rect_coordinate or find_poly_coordinate):
                                if find_poly_coordinate:
                                    # Only store the PIN class that has coordinate data
                                    if len(coordinate) > 0:
                                        if look_for_cell == cell_name:
                                            cl_pin.convert_coordinate_to_Point()
                                        coordinate.insert(0, metal)
                                        coordinate.insert(0, 'POLY')
                                        lef[cell_name][pin_name].append(coordinate)
                                        
                                if look_for_cell == cell_name:
                                    macro.set_pin(cl_pin)
                                find_poly_coordinate = False
                                find_rect_coordinate = False
    
    if desired_macro != None:
        # Process the data
        POX, POY, start_length = desired_macro.get_starting_point
        print(str(POX) + ' ' + str(POY) + ' ' + str(start_length))
        
    return lef

def parse_lib(filename):
    cell = ''
    pin = ''
    direction = ''
    data = [] # FOR LOAD CAP
    parasitic_data = {}
    find_capacitance_unit = False
    unit_cap = 1
    
    with open(filename) as json_file:
        for line in json_file:
            if re.search('capacitive_load_unit', line):
                find_capacitance_unit = True
                
            if find_capacitance_unit:
                if re.search('ff', line):
                    unit_cap = 0.001
                    
                if re.search(';', line):
                    find_capacitance_unit = False
                    
            if re.search('cell\s*[(]\w+[])]',line,flags=re.IGNORECASE):
                cell = line[line.find("(")+1:line.find(")")]
                
            if re.search('^[\t ]+pin\s*\(\w+\)\s*\{',line,flags=re.IGNORECASE):
                pin = line[line.find("(")+1:line.find(")")]

            if re.search('^[\t ]+direction\s*:\s*\w+',line,flags=re.IGNORECASE):
                direction = re.search('^[\t ]+direction\s*:\s*(\w+)',line)
                direction = direction.group(1)
                if direction == 'output':
                    data = [0]
                
            if re.match('^[\t ]+capacitance\s*:\s*([-+]?\d*\.\d+|\d+)\s*;',line,flags=re.IGNORECASE):
                data = re.findall('\d*\.\d+|\d+', line)
                
            ## Input the data into the dictionary
            if pin != '' and direction != '' and len(data) != 0:
                # if the cap unit is fF -> convert to pF
                if cell in parasitic_data:
                    parasitic_data[cell].update({pin : {'cap' : str(round(float(data[0])*unit_cap,5)), 'dir' : direction}})
                else:
                    parasitic_data[cell] = {pin : {'cap' : str(round(float(data[0])*unit_cap,5)), 'dir' : direction}}
                
    return parasitic_data

def parse_tech_lef(filename, find_via = False):
    techLEF_dict = {}
    metal_layer = 1
    
    with open(filename) as f:
        start_parsing_layer_info = False
        start_parsing_via_info = False
        find_cutclass = False
        find_open_quote_cutclass = False
        find_layer_cut_info = False
        find_layer_routing_info = False
        find_via_dimesion = False
        
        storage = []
        
        for line in f:
            if re.match(r'^LAYER\s+(\w+)', line):
                layer_name = re.match(r'^LAYER\s+(\w+)', line).group(1)
                start_parsing_layer_info = True
            
            # PART I: Parsing the information of the metal layer
            if start_parsing_layer_info:
                if re.match(r'^\s+TYPE\s+\w+\s*;', line):
                    type_of_layer = re.match(r'^\s+TYPE\s+(\w+)\s*;', line).group(1)
                    if type_of_layer == 'CUT':
                        find_layer_cut_info = True  # Set the Flag
                        
                        # initialize the dictionary
                        if not 'Layer' in techLEF_dict:
                            techLEF_dict['Layer'] = {}
                        techLEF_dict['Layer'][layer_name] = {'type' : type_of_layer}
                        continue
                        
                    if type_of_layer == 'ROUTING':
                        find_layer_routing_info = True
                        cur_ml = cl.LEF_Metal_Routing(layer= layer_name, layer_type=type_of_layer, layer_number = metal_layer)
                        metal_layer += 1
                        continue
                
                # PART IA: Get the information of CUT layers 
                if find_layer_cut_info:
                    if re.match(r'^\s*PROPERTY\s+LEF58_CUTCLASS', line):
                        find_cutclass = True
                    
                    if find_cutclass:
                        if re.search(r'"', line) and not find_open_quote_cutclass:
                            find_open_quote_cutclass = True
                            
                        elif re.search(r'"', line) and find_open_quote_cutclass:
                            find_open_quote_cutclass = False
                        
                        if re.search(r';', line) and not find_open_quote_cutclass:
                            find_cutclass = False
                            
                        if find_open_quote_cutclass:
                            if re.match('^\s+CUTCLASS\s+\w+', line):
                                cutclass = re.match(r'^\s+CUTCLASS\s+(\w+)', line)
                                # Initialize the class to store the info
                                cur_ml = cl.LEF_Metal_Cut(layer= layer_name, layer_type=type_of_layer)
                                cur_ml.set_layerClassName(cutclass.group(1))
                                cur_ml.set_cutClass(True)
                                
                            if re.search(r'\s+WIDTH\s+([-+]?\d*\.\d+)', line):
                                width = re.search(r'\s+WIDTH\s+([-+]?\d*\.\d+)', line)
                                cur_ml.set_viaWidth(width.group(1))
                                
                            if re.search(r'\s+LENGTH\s+([-+]?\d*\.\d+|\w+)', line):
                                length = re.search(r'\s+LENGTH\s+([-+]?\d*\.\d+)', line)
                                cur_ml.set_viaLength(length.group(1))
                                
                            if re.search(r'\s+CUTS\s+([-+]?\d*\.\d+|\w+)', line):
                                cuts = re.search(r'\s+CUTS\s*(\d+)', line)
                                cur_ml.set_viaCuts(cuts.group(1))
                                
                            if re.search(r';', line):
                                storage.append(cur_ml)
                                
                    if re.match(r'^\s*WIDTH\s+([-+]?\d*\.\d+)', line):
                        wid = re.search(r'^\s*WIDTH\s+([-+]?\d*\.\d+)\s*;', line)
                        cur_ml = cl.LEF_Metal_Cut(layer= layer_name, layer_type=type_of_layer)
                        cur_ml.set_viaWidth(wid.group(1))
                        storage.append(cur_ml)
                        
                    if start_parsing_layer_info and re.match(r'^\s*END\s+' + re.escape(layer_name), line):
                        start_parsing_layer_info  = False
                        find_layer_cut_info = False
                
                # PART IB: Get the information of ROUTING layers 
                if find_layer_routing_info:
                    if re.match('^\s+DIRECTION\s+\w+', line):
                        direction = re.match(r'^\s+DIRECTION\s+(\w+)\s+;', line)
                        cur_ml.set_layerDirection(direction.group(1))
                        
                    if re.match('^\s+WIDTH\s+([-+]?\d*\.\d+)\s+;', line):
                        width = re.match(r'^\s+WIDTH\s+([-+]?\d*\.\d+)', line)
                        cur_ml.set_layerWidth(width.group(1))
                        
                    if re.match('^\s+PITCH\s+([-+]?\d*\.\d+)\s+;', line):
                        pitch = re.match(r'^\s+PITCH\s+([-+]?\d*\.\d+|\w+)', line)
                        cur_ml.set_layerPitch(pitch.group(1))
                        
                    if re.match('^\s+SPACING\s+([-+]?\d*\.\d+)\s+;', line):
                        spacing = re.match(r'^\s+SPACING\s+([-+]?\d*\.\d+|\w+)', line)
                        cur_ml.set_layerSpacing(spacing.group(1))
                    
                    if re.match('^\s+TYPE\s+\w+\s*;', line):
                        check = re.match('^\s+TYPE\s+(\w+)\s*;', line).group(1)
                        if check == 'MIMCAP' or check == 'PASSIVATION' or check == 'HIGHR' or check == 'TSV':
                            start_parsing_layer_info  = False
                            find_layer_routing_info = False
                    
                    if start_parsing_layer_info and re.match(r'^\s*END\s+' + re.escape(layer_name), line):
                        start_parsing_layer_info  = False
                        find_layer_routing_info = False
                        storage.append(cur_ml)
            
#             PART II: Parsing the information of VIA section --> # of cuts
            if re.match(r'^\s*VIA\s+(\w+)', line):
                start_parsing_via_info = True
                via_name = re.match(r'^\s*VIA\s+(\w+)', line).group(1)
                cur_via = cl.LEF_VIA_Info(via_name=via_name)
                
            if start_parsing_via_info and re.match(r'^\s*END\s+' + re.escape(via_name) + '', line):
                start_parsing_via_info = False
                cur_via.set_viaCuts(compute_via_number_of_cuts(cur_via, techLEF_dict))
                storage.append(cur_via)
                
            if start_parsing_via_info:
                if re.match(r'^\s+LAYER\s+(\w+)\s+;', line):
                    layer = re.match(r'\s+LAYER\s+(\w+)\s+;', line).group(1)
                    if techLEF_dict['Layer'][layer]['type'] == 'CUT':
                        find_via_dimesion = True
                        cur_via.set_viaCutLayer(layer)
                    else:
                        cur_via.set_viaLayerAssignemnt(layer, techLEF_dict)
                        find_via_dimesion = False
                
                # If the CUT layer is detected 
                if find_via_dimesion:
                    if re.match(r'^\s+RECT\s+.+;$', line):
                        pin_dimension = re.findall('([-+]?\d*\.\d+)+', line)
                        cur_via.set_viaDimension(pin_dimension)
            
            if len(storage) != 0:
                convert_techLEF_dictionary(storage, techLEF_dict)
                storage.clear()
        
        # Function to get the list of via used in the calibration script
        if find_via:
            find_via_for_each_layer(techLEF_dict)
        
        else:
            return techLEF_dict
        
        
def convert_techLEF_dictionary(storage, techLEF_dict):
    for data in storage:
        is_viaInfo = hasattr(data, 'get_layerType')
        
        """ CONVERT METAL INFO TO DICTIONARY """
        if is_viaInfo:
            if not 'Layer' in techLEF_dict:
                techLEF_dict['Layer'] = {}
            # Translate the ROUTING metal layer information
            if data.get_layerType == 'ROUTING':
                # Initialize the dictionary key
                if not data.get_layerName in techLEF_dict['Layer']:
                    techLEF_dict['Layer'][data.get_layerName] = {}
                techLEF_dict['Layer'][data.get_layerName]['type'] = data.get_layerType
                
                if data.get_layerWidth != '':
                    techLEF_dict['Layer'][data.get_layerName]['width'] = data.get_layerWidth
                
                if data.get_layerSpacing != '':
                    techLEF_dict['Layer'][data.get_layerName]['spacing'] = data.get_layerSpacing
                
                if data.get_layerPitch != '':
                    techLEF_dict['Layer'][data.get_layerName]['pitch'] = data.get_layerPitch
                    
                if data.get_layerDirection != '':
                    techLEF_dict['Layer'][data.get_layerName]['direction'] = data.get_layerDirection
                    
                if data._layer_number != 0:
                    techLEF_dict['Layer'][data.get_layerName]['metal_layer'] = data._layer_number
            
            # Translate the CUT metal layer information
            elif data.get_layerType == 'CUT':
                # Initialize the dictionary key
                if not data.get_layerName in techLEF_dict['Layer']:
                    techLEF_dict['Layer'][data.get_layerName] = {}
                    
                techLEF_dict['Layer'][data.get_layerName]['type'] = data.get_layerType
                
                # Data contains a cutClass information
                if data.isCutClass:
                    techLEF_dict['Layer'][data.get_layerName][data.get_layerClassName] = {}
                    techLEF_dict['Layer'][data.get_layerName][data.get_layerClassName]['viaCuts'] = data.get_viaCuts
                    
                    if data.get_viaWidth != '':
                        techLEF_dict['Layer'][data.get_layerName][data.get_layerClassName]['viaWidth'] = data.get_viaWidth
                    
                    if data.get_viaLength != '':
                        techLEF_dict['Layer'][data.get_layerName][data.get_layerClassName]['viaLength'] = data.get_viaLength
                
                # Data do not contain cutClass information
                else:
                    if data.get_viaWidth != '':
                        techLEF_dict['Layer'][data.get_layerName]['viaWidth'] = data.get_viaWidth
                    
                    techLEF_dict['Layer'][data.get_layerName]['viaCuts'] = data.get_viaCuts
        
        ### CONVERT VIA INFO TO DICT ###
        elif not is_viaInfo:
            if not 'Via' in techLEF_dict:
                techLEF_dict['Via'] = {}
            techLEF_dict['Via'][data.get_viaName] = {}     # Initialize the key to the dictionary
            techLEF_dict['Via'][data.get_viaName]['cuts'] = data.get_viaTotalCuts
            techLEF_dict['Via'][data.get_viaName]['top_layer'] = data._top_layer
            techLEF_dict['Via'][data.get_viaName]['bottom_layer'] = data._bottom_layer
            techLEF_dict['Via'][data.get_viaName]['bottom_layer_number'] = techLEF_dict['Layer'][data._bottom_layer]['metal_layer']
            
                
def compute_via_number_of_cuts(via_class, techLEF_dict):
    num_of_cuts = 0
    # Determine the width of the CUT layer
    cut_layer = False
    for x in techLEF_dict['Layer'][via_class.get_viaCutLayer]:
        if x == 'type':
            continue
                
        if 'viaWidth' in techLEF_dict['Layer'][via_class.get_viaCutLayer][x]:
            if int(techLEF_dict['Layer'][via_class.get_viaCutLayer][x]['viaCuts']) == 1:
                viaWidth = float(techLEF_dict['Layer'][via_class.get_viaCutLayer][x]['viaWidth'])
                cut_layer = True
                break 
    
    if not cut_layer:
        viaWidth = float(techLEF_dict['Layer'][via_class._bottom_layer]['width'])
    
    assert viaWidth != None, 'Invalid value for viaWidth in compute_via_number_of_cuts'
    
    # Algorthm to compute the number of cuts
    for point in via_class.get_viaDimension:
        if len(point) == 4:
            length = float(point[2]) - float(point[0])
            width = float(point[3]) - float(point[1])
            num_of_cuts += int(round(length/viaWidth,0) * round(width/viaWidth,0))

        elif len(point) == 2:
            x_size = float(point[0])
            y_size = float(point[1])
            num_of_cuts += int(round(x_size/viaWidth,0) * round(y_size/viaWidth,0))
    
    return (num_of_cuts)

def find_via_for_each_layer(techLEF_dict):
    metal_layer = 1
    via_list = []
    
    for x in techLEF_dict['Via']:
        via_TopLayer = techLEF_dict['Via'][x]['top_layer']
        via_BottomLayer = techLEF_dict['Via'][x]['bottom_layer']
        bl = techLEF_dict['Layer'][via_BottomLayer]['metal_layer']
        
        if bl == metal_layer:
            if techLEF_dict['Via'][x]['cuts'] > 1:
                continue 
            
            if re.search('(BAR|WEST|EAST|NORTH|SOUTH|LRG|MIN)', x):
                continue
              
            tl_dir = 'H' if techLEF_dict['Layer'][via_TopLayer]['direction'] == 'HORIZONTAL' else 'V'
            bl_dir = 'H' if techLEF_dict['Layer'][via_BottomLayer]['direction'] == 'HORIZONTAL' else 'V'
            via_dir = bl_dir + tl_dir 
            if re.search(via_dir, x):
                via_list.append(x)
                metal_layer += 1
                
            elif not re.search(tl_dir, x) and not re.search(bl_dir, x):
                via_list.append(x)
                metal_layer += 1
    
    for via in via_list:
        print(via)
    
def write_to_file(filename, json_data):
    with open(filename, 'w') as f:
    ## Convert Dictionary to JSON Format and write it to a file 
        json.dump(json_data, f, indent = 4)

def read_json(file):
    with open (file, 'r') as f:
        return json.load(f)
    
def get_lef_and_lib_data(cell_lef_files = None, tech_lef_files = None, lib_dir = None, bc_lib_dir = None, wc_lib_dir = None):
    """ PART III: PARSING TECH LEF """
    print('# Reading the TECH LEF ...')
          
    tech_lef = parse_tech_lef(tech_lef_files)
    assert tech_lef, 'ERROR - tech_lef is NoneType!'
    print('# Finish Reading the TECH LEF')
          
    """ PART I: PARSING CELL LEF """
    CELL_LEF = {}
    
    print('# Reading the Marco LEF...')
          
    # PARSING THE MACRO LEF 
    for file in cell_lef_files:
        CELL_LEF.update(parse_lef(file, tech_lef = tech_lef, find_desired_cell_info = True))

    print('# Finish Reading the Marco LEF')
    """ END PARSING LEF """
    
    """ PART II: PARSING PVT LIBRARIES """
    LIB = {}
    
    print('# Reading the Lib...')
    # PARSE ALL THE LIBS TO OBTAIN THE DESIRED INFORMATION
    for ld in lib_dir:
        for file in glob.glob(ld):
            LIB.update(parse_lib(file))
    
    print('# Finish Reading the Lib')
    """ END OF PART II """

    return tech_lef, CELL_LEF, LIB

def main_cell_name(look_for_cell, lefFiles, tech_lef = None):
    if tech_lef:
        tech_lef = parse_tech_lef(tech_lef)
    
    LEF = {}
    
    for file in lefFiles:
        LEF.update(parse_lef(file, tech_lef = tech_lef, look_for_cell = look_for_cell))

###########################
#### START OF THE CODE ####
###########################
# Step 1: Find user input
parser = ArgumentParser()
parser.add_argument("-cn", dest="cn",help="Take cell name as input to find the shape of its input and output port", metavar="cell_name")
parser.add_argument("-tech", dest="tech_lef",help="Input the TECH LEF directory", metavar="TECH")
parser.add_argument("-clef", dest="cell_lef",help="Input the CELL LEF directory", metavar="CELL")
parser.add_argument("-via", dest='via', action='store_true', help="Choose Via type used in the calibration script")
args = parser.parse_args()

# User input - Get Cell's pins Information
if args.cn != None:
    assert args.cell_lef != None, 'ERROR - Input cell LEF directory'
    lefFiles = re.split('\n| |, |; ', args.cell_lef)
    main_cell_name(args.cn, lefFiles, args.tech_lef if args.tech_lef else None)
    
# User input - Get List of via for calibration
elif args.via:
    assert args.tech_lef != None, 'ERROR - Input tech LEF directory'
    tech_lef_file = re.split('\n| |, |; ', args.tech_lef)
    for file in tech_lef_file:
        parse_tech_lef(file, args.via)