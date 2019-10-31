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

import re, json
import global_var as glob
import regression_model as rm
import Class as cl
from def_parser import def_parser 
import datetime
from lefParser import get_lef_and_lib_data
import time

# =============================================================================
#             
# =============================================================================
def printToSPEF(blocks_dict, nets, pins):
    print('# Writing SPEF')
    with open('./output/{}.spef'.format(glob.DESIGN), "w") as outfile:
        printHeader(outfile)
        
        #Step1: Print the NAME MAP section
        printNameMap(outfile, blocks_dict, nets)
        
        #Step2: Print the PORTS section
        printPorts(outfile, pins)
        
        #Step3: Print the DNET section (PARASITIC)
        print('# Calculating Parasitic...')
        printParasitics(outfile, blocks_dict, nets, pins)
        print('# Finish Writing Parasitic')
# =============================================================================
# 
# =============================================================================
def printHeader(out):
    now = datetime.datetime.now()
    
    out.write('*SPEF "' + glob.SPEF_VER + '"\n')
    out.write('*DESIGN "' + glob.DESIGN + '"\n')
    out.write('*DATE "' + now.strftime("%a %b %d %H:%M:%S %Y") + '"\n')
    out.write('*VENDOR "' + glob.VENDOR + '"\n')
    out.write('*PROGRAM "' + glob.PROGRAM + '"\n')
    out.write('*VERSION "' + glob.VERSION +'"\n')
    out.write('*DESIGN_FLOW "PIN_CAP NONE" "NAME_SCOPE LOCAL"\n')
    out.write('*DIVIDER {}\n'.format(glob.DIVIDER))
    out.write('*DELIMITER :\n'.format(glob.DELIMITER))
    out.write('*BUS_DELIMITER {}\n'.format(glob.BUS_CHAR))
    out.write('*T_UNIT 1 {}\n'.format(glob.TIME_UNIT))
    out.write('*C_UNIT 1 {}\n'.format(glob.CAP_UNIT))
    out.write('*R_UNIT 1 {}\n'.format(glob.RES_UNIT))
    out.write('*L_UNIT 1 {}\n\n'.format(glob.INDUCTANCE_UNIT))
    
# =============================================================================
# Desc: Print the number with its associated cell to SPEF
# =============================================================================
def printNameMap(out, blocks, nets):
    out.write('*NAME_MAP\n')
    for b in blocks:
        name = b
        number = blocks[b]['number']
        out.write('\n*{} {}'.format(number, name))
            
    for n in nets:
        out.write('\n*{} {}'.format(n.number, n.name))

      
# =============================================================================
# Desc: Writes the parasitic section to the SPEF
# =============================================================================
def printParasitics(out, cell_coor_dict, nets, pins):
    for net in nets:
        # Exception
        if net.rc_tree == None:
#            print('# Warning - No interconnect parasitic can be processed for net: {}'.format(net.name))
            continue
        
        # CALCULATE PARASITIC VALUE
        getResCap_fromRM(net)
        
        """TEMPORARY FUNCTION TO CALCULATE TOTAL CAPCITANCE"""
        total_cap = 0.0
        for i in net.regression_data:
            if len(i) == 4:
                total_cap += i[3]
        """"""
        
        # Print DNET section
        out.write('\n*D_NET *' + str(net.number) + ' '  + str(round(total_cap,10)))
        
        # Print CONN section
        out.write('\n\n*CONN\n')
        
        # PIN or PORT
        for pin in net.pin:
            if pins[pin[1]]['DIRECTION'].lower() == 'input':
                pin_dir = 'I'
            elif pins[pin[1]]['DIRECTION'].lower() == 'output':
                pin_dir = 'O'
            
            # For a Pin, the load is zero
            out.write('*P *{} {} *C {} {} *L 0\n'.format(pins[pin[1]]['number'], pin_dir, 
                      float(pins[pin[1]]['X'])/float(glob.UNIT_DISTANCE), float(pins[pin[1]]['Y'])/float(glob.UNIT_DISTANCE)))
        
        # INPUT
        iteration = int(len(net.input))
        for i in range (0, iteration):
            out.write('*I *{}:{} I *C {} {} *L {} *D {}\n'.format(cell_coor_dict[net.input[i][0]]['number'], \
                      net.input[i][1], float(cell_coor_dict[net.input[i][0]]['x'])/float(glob.UNIT_DISTANCE), \
                      float(cell_coor_dict[net.input[i][0]]['y'])/float(glob.UNIT_DISTANCE), \
                      cell_coor_dict[net.input[i][0]]['pin'][net.input[i][1]]['cap'], \
                      cell_coor_dict[net.input[i][0]]['cell_name']))
            
        # OUTPUT
        iteration = int(len(net.output))
        for i in range (0, iteration):
            out.write('*I *' + str(cell_coor_dict[net.output[i][0]]['number']) + ':' + net.output[i][1] + ' O *C' + ' ' 
                  + str(float(cell_coor_dict[net.output[i][0]]['x'])/float(glob.UNIT_DISTANCE)) + ' ' 
                  + str(float(cell_coor_dict[net.output[i][0]]['y'])/float(glob.UNIT_DISTANCE)) + ' *L 0'
                  + ' *D ' + cell_coor_dict[net.output[i][0]]['cell_name'] + '\n')
            
        printResCap(net, out)
            
# =============================================================================
# 
# =============================================================================
def printPorts(out, pins):
    unit_distance = glob.UNIT_DISTANCE
    out.write('\n\n*PORTS\n\n')
    
    for key in pins:
        x_coor = str(round(float(pins[key]['X'])/unit_distance, 4))
        y_coor = str(round(float(pins[key]['Y'])/unit_distance, 4))
        
        out.write('*{} {} *C {} {}\n'.format(pins[key]['number'], pins[key]['DIRECTION'][0], x_coor, y_coor))
        
# =============================================================================
#         
# =============================================================================
def printResCap(net, out):
    line_num = 1
    
    # Cap Section
    out.write('\n*CAP\n')
    for cap_data in net.regression_data:
        if len(cap_data) == 4:
            string = ''
            string = str(line_num) + ' *' + str(cap_data[1][0])
            if cap_data[1][1]:
                string += ':' + str(cap_data[1][1])
            
            string += ' ' +  str(cap_data[3]) + '\n'
            out.write(string)
            line_num += 1
        
    line_num = 1
    
    # Res Section
    out.write('\n*RES\n')
    for data in net.regression_data: 
        string = ''
        string = str(line_num) + ' *' + str(data[0][0])
        if str(data[0][1]):
            string += ':' + str(data[0][1])
            
        string += ' *' + str(data[1][0])
        if str(data[1][1]) :
            string += ':' + str(data[1][1])
        
        string += ' ' +str(data[2]) + '\n'
        out.write(string)
        
        line_num += 1       #Increment the line numbers

# =============================================================================
# Need to be modified because now we are using the coordianate not the NODE.
# We need to use the NODE, so that on the SPEF we will use the spesific node that
# indicates that points where coupling capacitance exists.
        
# In this case, we are just hardcoding the nodes 
# =============================================================================
def get_CC_from_RM(net, nets):
    CC_list = []
    tot_CC = 0
    metal_width = 72            #0.018 um if converted to actual value
    unit_distance = glob.UNIT_DISTANCE
    MIN_SPACING = 1874          #The min spacing for CC is 0.4685 um -- NEED TO BE MODIFIED FOR DIFFERENT PDK
    
    for n in nets:
        tot_CC = 0
        if net.name == n.name:
            continue
        
#        net_ct = net.coordinate_tree
#        n_ct = n.coordinate_tree
#        
#        q = []
#        q.append(net_ct)
#        while(len(q) > 0):

        """Needs to modify the algorithm because ASAP7 metal width is 18 nm (72 in DEF), so this code
        substract the metal width from the spacing. For different PDK, we have to change this value 
        because the default metal width will be different from PDK to PDK"""

        for c in net.coordinates:
            for n_coor in n.coordinates:
                if c[0] == 'M2' and c[0] == n_coor[0] and len(c) > 4 and len(n_coor) > 4 :
                    spacing, length, cc = 0.0, 0.0, 0.0
                    if (float(c[1]) <= float(n_coor[1]) and float(c[3]) >= float(n_coor[3]) and float(c[1]) <= float(n_coor[3]) and float(c[3]) >= float(n_coor[1])):
                        spacing = abs(float(c[2]) - float(n_coor[2])) - metal_width
                        if spacing <= MIN_SPACING:
                            length = abs(float(n_coor[1]) - float(n_coor[3]))/unit_distance
                            spacing /= unit_distance
                            cc = rm.CC_RM(c[0], length, spacing*10)
                            
                    elif (float(c[1]) >= float(n_coor[1]) and float(c[3]) >= float(n_coor[3]) and float(c[1]) <= float(n_coor[3]) and float(c[3]) >= float(n_coor[1])):
                        spacing = abs(float(c[2]) - float(n_coor[2])) - metal_width
                        if spacing <= MIN_SPACING:
                            length = abs(float(c[1]) - float(n_coor[3]))/unit_distance
                            spacing /= unit_distance
                            cc = rm.CC_RM(c[0], length, spacing*10)
                            
                    elif(float(c[1]) >= float(n_coor[1]) and float(c[3]) <= float(n_coor[3]) and float(c[1]) <= float(n_coor[3]) and float(c[3]) >= float(n_coor[1])):
                        spacing = abs(float(c[2]) - float(n_coor[2])) - metal_width
                        if spacing <= MIN_SPACING:
                            length = abs(float(c[1]) - float(c[3]))/unit_distance
                            spacing /= unit_distance
                            cc = rm.CC_RM(c[0], length, spacing*10)
                            
                    elif (float(c[1]) <= float(n_coor[1]) and float(c[3]) <= float(n_coor[3]) and float(c[1]) <= float(n_coor[3]) and float(c[3]) >= float(n_coor[1])):
                        spacing = abs(float(c[2]) - float(n_coor[2])) - metal_width
                        if spacing <= MIN_SPACING:
                            length = abs(float(n_coor[1]) - float(c[3]))/unit_distance
                            spacing /= unit_distance
                            cc = rm.CC_RM(c[0], length, spacing*10)
                            
                    tot_CC += cc
                    
                elif c[0] == 'M3' and c[0] == n_coor[0] and len(c) > 4 and len(n_coor) > 4:
                    spacing, length,cc = 0.0,0.0, 0.0
                    if (float(c[2]) <= float(n_coor[2]) and float(c[4]) >= float(n_coor[4]) and float(c[2]) <= float(n_coor[4]) and float(c[4]) >= float(n_coor[2])):
                        spacing = abs(float(c[1]) - float(n_coor[1])) - metal_width
                        if spacing <= MIN_SPACING:
                            length = abs(float(n_coor[2]) - float(n_coor[4]))/unit_distance
                            spacing /= unit_distance
                            cc = rm.CC_RM(c[0], length, spacing*10)
                            
                    elif (float(c[2]) >= float(n_coor[2]) and float(c[4]) >= float(n_coor[4]) and float(c[2]) <= float(n_coor[4]) and float(c[4]) >= float(n_coor[2])):
                        spacing = abs(float(c[1]) - float(n_coor[1])) - metal_width
                        if spacing <= MIN_SPACING:
                            length = abs(float(c[2]) - float(n_coor[4]))/unit_distance
                            spacing /= unit_distance
                            cc = rm.CC_RM(c[0], length, spacing*10)
                            
                    elif (float(c[2]) >= float(n_coor[2]) and float(c[4]) <= float(n_coor[4]) and float(c[2]) <= float(n_coor[4]) and float(c[4]) >= float(n_coor[2])):
                        spacing = abs(float(c[1]) - float(n_coor[1])) - metal_width
                        if spacing <= MIN_SPACING:
                            length = abs(float(c[2]) - float(c[4]))/unit_distance
                            spacing /= unit_distance
                            cc = rm.CC_RM(c[0], length, spacing*10)
                            
                    elif (float(c[2]) <= float(n_coor[2]) and float(c[4]) <= float(n_coor[4]) and float(c[2]) <= float(n_coor[4]) and float(c[4]) >= float(n_coor[2])):
                        spacing = abs(float(c[1]) - float(n_coor[1])) - metal_width
                        if spacing <= MIN_SPACING:
                            length = abs(float(n_coor[2]) - float(c[4]))/unit_distance
                            spacing /= unit_distance
                            cc = rm.CC_RM(c[0], length, spacing*10)
                            
                    tot_CC += cc
                    
        if tot_CC > 0:  
            CC_list.append([n.number, tot_CC])
    
    return CC_list
        
# =============================================================================
# 
# =============================================================================
def getResCap_fromRM(net):
    # Read config_file
    config_file = rm.CONFIG_FILE(glob.CONFIG_FILE_DIR)
    
    # Calculation of parasitics
    starting_nodes = net.rc_tree
    
    for node in starting_nodes: 
        regression_model(node, net, config_file)
     
# =============================================================================
# Desc: A recursive function that will traverse through the tree of the wire 
#       topology to run the regression model. It will segment the node if the 
#       algorithm detects a branching on the wire
# =============================================================================
def regression_model(node, net, config_file):
    for next_rp in node.NEXT:
        r, c = run_RM(node, next_rp, config_file)
        val = [node.number, next_rp.number, r, c]
        net.add_regression_data(val)
        regression_model(next_rp, net, config_file)
            

# =============================================================================
# Desc: Read and extract information from the DEF file      
# =============================================================================
#def run_RM(node, config_file):
def run_RM(cur_rp, next_rp, config_file):
    unit_distance = glob.UNIT_DISTANCE
    
    # Via Parasitics
    if next_rp.isVia:
        via = next_rp.via_name
        total_cut = int(glob.TECH_LEF_DICT['Via'][via]['cuts'])
        bottom_layer = int(glob.TECH_LEF_DICT['Via'][via]['bottom_layer_number'])
        
        via_res, via_cap = config_file.get_via_parasitic(1, bottom_layer, via_res = True, via_cap = True)
        via_res = via_res/total_cut
        return via_res, via_cap
    
    # Wire Parasitics
    else:
        metal_layer = int(glob.TECH_LEF_DICT['Layer'][next_rp.metal_layer]['metal_layer'])    
        length = float(calculate_length(cur_rp, next_rp)) / float(unit_distance)
        r,c = config_file.get_wire_parasitic(metal_layer, length, r = True, c = True)
        
        return round(float(r),6), round(float(c),11)
            
# =============================================================================
# Desc: Since the wire will only either go horizontal or vertical, we can calculate
#       the length of the metal
# =============================================================================
#def calculate_length(node):
def calculate_length(cur_rp, next_rp):
    if cur_rp.x == next_rp.x:
        return abs(int(cur_rp.y) - int(next_rp.y))
    
    if cur_rp.y == next_rp.y:
        return abs(int(cur_rp.x) - int(next_rp.x))

# =============================================================================
# Desc: A function to read the PDK simplified library to obtain the load
#       capacitance value
# =============================================================================
def read_json(file):
    with open (file, 'r') as f:
        return json.load(f)

def validate_data(nets):
    from validation_output import check_output
    file = './asd.txt'
    tot_pin_dict = check_output(file)
    for net in nets:
        if not net.name in tot_pin_dict:
            continue
        
        num_pin = len(net.output) + len(net.input) + len(net.pin)
        if tot_pin_dict[net.name] != num_pin:
            print('\n Error - Net: ' +net.name)
            print('Total Pin - Expected: {} - {}'.format(tot_pin_dict[net.name], num_pin))
"""END HERE"""

def main():
    # Declares Variables
    nets = []
    cell_coor_dict = {}
    pins = {}
    
    start_time = time.time()
    
    print('# Start DEF to SPEF conversion')
          
    # Initialize global variables
    glob.initialize()
    
    def_file = glob.DEF_DIR
    glob.TECH_LEF_DICT, cell_lef, load_cap_dict = \
    get_lef_and_lib_data(glob.MARCRO_LEF_DIR, glob.TECH_LEF_DIR, glob.LIB_DIR)
    
    # 1st: Parse DEF
    def_parser(def_file, pins, nets, cell_coor_dict, load_cap_dict, cell_lef)
    
    # 2nd: Write SPEF
    printToSPEF(cell_coor_dict, nets, pins)
    
    print("# Total RunTime = %s seconds" % (time.time() - start_time))
    
main()
