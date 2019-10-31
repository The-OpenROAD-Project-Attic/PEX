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
import sys

def compute_overlap(inst):
    multp = int(int(inst)/TOTAL_WIRES_PER_LAYER)
    return int((int(int(inst)%50)/2)+2)*DX*2, float(int((int(inst)-TOTAL_WIRES_PER_LAYER*multp)/50)+1)*0.1 - 0.03

def determine_metal_layer(num):
    return int(int(num)/TOTAL_WIRES_PER_LAYER + 1)

def read_file(file,corner_type):
    """ Parse SPEF generated from Innovus
    
    Parse SPEF to get the total RC for a spesific net with known wire length. 
    Dump the training data to .txt file.
    
    Args:
        file: path to the input file, SPEF
        corner_type: contain the information of the RC corner
        
    Returns:
        cap_storage -> the list is filled with the trained data
            - The data is in form of [capacitance = a*X + b], X is length of wire
            - Trained data are {a} and {b}
    """
    
    mapping_name = []
    LUT = {}
    net_num = 0
    
    with open(file) as f, open('./work/Resistance_TrainingSet_' + CORNER_TYPE + '.txt','w') as out, \
    open('./work/Cap_TrainingSet_' + CORNER_TYPE + '.txt','w') as out1, \
    open('./work/CC_Cap_TrainingSet_' + CORNER_TYPE + '.txt','w') as out2:
        name_map = False
        d_net = False
        find_res = False
        find_cap = False

        res = 0.0
        cap = 0.0
        cc_cap = 0.0
        wire_length = 0.0
        prev_length = 0
        metal_layer = 0
        ref_cap = 0.0
        ref_res = 0.0
        
        # Print the corner Type
        out.write('Corner Type: ' + CORNER_TYPE + '\n')
        out1.write('Corner Type: ' + CORNER_TYPE + '\n')
          
        # Print header
        out.write('Len Resistance\n')
        out1.write('Len Cap\n')
        out2.write('Len Spacing CC\n')
        
        # Parsing file
        for line in f:
            if re.search('[*]NAME_MAP',line,flags=re.IGNORECASE):
                name_map = True

            if re.search('[*]PORTS',line,flags=re.IGNORECASE):
                name_map = False

            if name_map:
                if re.match('^[*]\d+ \w+',line, flags=re.IGNORECASE):
                    data = re.findall(r'\w+', line)
                    if re.search('OUT',line,flags=re.IGNORECASE):
                        mapping_name.append(data)

            if re.search('[*]D_Net',line,flags=re.IGNORECASE):
                d_net = True
                data = re.findall(r'\d+', line)
                for mapping in mapping_name:
                    if mapping[0] == data[0]:
                        num = re.findall(r'\d+', mapping[1])
                        net_num = num[0]
#                        wire_length = compute_wire_length(num[0])
                        topology = compute_overlap(num[0])
                        metal_layer = determine_metal_layer(num[0])

            if d_net:
                if re.search('[*]END',line,flags=re.IGNORECASE):
                    d_net =False
                    find_res = False
                    
                    LUT[net_num] = {'Resistance' : str(round(res,7)),\
                       'ML' : metal_layer, 'Cap' : str(round(cap,7))}
                    
                    prev_length = topology[0]
                    res, cc_cap, cap = 0.0, 0.0, 0.0

                if re.search('[*]RES',line,flags=re.IGNORECASE):
                    find_cap = False
                    find_res = True
                    
                if re.search('[*]CAP',line,flags=re.IGNORECASE):
                    find_cap = True
                    find_res = False

                if find_res:
                    if re.match('^\d+ [*].+ \d+',line, flags=re.IGNORECASE):
                        data = re.findall(r'\d+\.?\d*', line)
                        
                        ## Caclulate all resistance 
                        res += float(data[len(data)-1])
                        
                if find_cap:
                    if re.match('^\d* [*].* .*',line, flags=re.IGNORECASE):
                        data = re.findall(r"\d+\.?\d*", line)
                        if re.search('e[-]',line,flags=re.IGNORECASE):
                            cap += float(data[len(data)-2]) * pow(10, -int(data[len(data)-1]))
                            
                        else:
                            cap += float(data[len(data) - 1])
                        
                    
                    if re.match('^\d* [*].* .* .*',line, flags=re.IGNORECASE):
                        data = re.findall(r"\d+\.?\d*", line)
                        if re.search('e[-]',line,flags=re.IGNORECASE):
                            cc_cap += float(data[len(data)-2]) * pow(10, -float(data[len(data)-1]))
                            
                        else:
                            cc_cap += float(data[len(data) - 1])
        
        # Printing out parasitic data
        for i in range (0,len(LUT)):
            # Get the reference RC
            if i%TOTAL_WIRES_PER_LAYER == 0:
                ref_res = float(LUT[str(i)]['Resistance'])
                ref_cap = float(LUT[str(i)]['Cap'])
                continue
            
            # Calculate the RC respective to its length
            total_res = float(LUT[str(i)]['Resistance'])
            total_cap = float(LUT[str(i)]['Cap'])
            
            res = total_res - ref_res
            cap = total_cap - ref_cap
            wire_length = i%TOTAL_WIRES_PER_LAYER * DX
            
            # Print the training data 
            out.write(str(round(wire_length,4)) + ' ' + str(round(res,7)) + '\n')
            out1.write(str(round(wire_length,4)) + ' ' + str(round(cap,10)) + '\n')
            
def main():
    read_file(SPEF_FILE, CORNER_TYPE)

##########################################
########### Start of the Code ############
##########################################
assert len(sys.argv) == 7, 'ERROR - Expected arguments are 6, but ' + str(len(sys.argv)-1) + ' provided'

### Global Variable - Input for calibration script ###
DX = float(sys.argv[1])
START_LEN = float(sys.argv[2])
TOTAL_WIRES_PER_LAYER = float(sys.argv[3])
DY = float(sys.argv[4])
CORNER_TYPE = sys.argv[5]
SPEF_FILE = sys.argv[6]

main()
##########################################