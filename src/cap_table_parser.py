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
import os
import glob

my_env = os.environ.copy()

def parse_file(filename):
    """ Parse the file containing via RC 
    
    Args:
        filename: File that contains VIA RC
        
    Returns:
        A dict that contains all via RC information.
    """
    
    ct_dict = {}
    find_layer = False
    metal_layer = 0
    unit_fF = False
    
    with open(filename) as f:
        for line in f:    
            data = [] 

            if re.search('Unit parasitics for layer (\d+)',line, flags=re.IGNORECASE):
                find_layer = True
                # get the metal layer number
                metal_layer = re.search('Unit parasitics for layer (\d+)',line, flags=re.IGNORECASE).group(1)
                if re.search(r'ff', line, flags=re.IGNORECASE):
                    unit_fF = True
                
            if find_layer:
                if re.match(r'[\t ]Cap = \d+\.?\d*',line, flags=re.IGNORECASE): 
                    data = re.findall(r'\d+\.?\d*', line)
                    ct_dict[str(metal_layer)] = { 'CAP' : data[0] }
                    ct_dict[str(metal_layer)]['UNIT'] = unit_fF
                
                if re.match(r'[\t ]Res = \d+\.?\d*',line, flags=re.IGNORECASE):
                    data = re.findall(r'\d+\.?\d*', line)
                    ct_dict[str(metal_layer)]['RES'] = data[0]
                    
                if re.match(r'[\t ]Via Cap = \d+\.?\d*',line, flags=re.IGNORECASE):
                    data = re.findall(r'\d+\.?\d*', line)
                    ct_dict[str(metal_layer)]['VIA_1_CAP'] = data[0]
                    
                if re.match(r'[\t ]Via Res = \d+\.?\d*',line, flags=re.IGNORECASE):
                    data = re.findall(r'\d+\.?\d*', line)
                    ct_dict[str(metal_layer)]['VIA_1_RES'] = data[0]
    
    return ct_dict

def write_toFile(ct_dict, filename):
    """ Write the Via RC info to the config file
    
    Args:
        filename: confi file path
        ct_dict: dict contains via RC info
    """
    
    ## Step 1: Read the contents of the file
    f = open(filename,'r')
    text = f.readlines()
    f.close()
    
    ## Step 2: Open the file that will be written
    f = open(filename,'w')
    
    cap_exist = False
    res_exist = False
    
    unit = 1    # unit conversion variable
    
    if ct_dict[str(2)]['UNIT']:
        unit = 0.001
        
    for line in text:
        if re.match('CAPACITANCE', line):
            cap_exist = True
        
        # Search and Replace the pattern
        if cap_exist:
            if re.match(r'[\d+\.?\d*]+',line, flags=re.IGNORECASE):
                data = re.split(' ', line)
                # Divided by 1000 for unit coversion from fF to pF if the unit is indeed fF
                data[1] = str(round(float(ct_dict[data[0]]['CAP'])*unit, 10)) if data[0] in ct_dict else data[1]
                line = ' '.join(data)
            
            if re.search('END',line, flags=re.IGNORECASE):
                cap_exist = False
        
        if re.match('RESISTANCE', line):
            res_exist = True
        
        if res_exist:
            if re.match(r'[\d+\.?\d*]+',line, flags=re.IGNORECASE):
                data = re.split(' ', line)
                ct_res = round(float(ct_dict[data[0]]['RES'])*unit, 10)
                config_res = float(data[1])
                data[1] = str(ct_res) if not (config_res < ct_res+1 and config_res > ct_res-1) else data[1]
            if re.search('END',line, flags=re.IGNORECASE):
                res_exist = False
                
        f.write(line)
        
    ## Step 3: Write the Via information --> CAP
    f.write('\nVIA CAP\n')
    f.write('Layer 1_Cut\n')
  
    for i in range (1,len(ct_dict)+1):
        if not 'VIA_1_CAP' in ct_dict[str(i)]:
            continue
        f.write(str(i) + ' ' + str(round(float(ct_dict[str(i)]['VIA_1_CAP'])*unit,10)) + '\n')
    
    f.write('END\n')
    
    ## Step 4: Write the Via information -- RES
    f.write('\nVIA RES\n')
    f.write('Layer 1_Cut\n')

    for i in range (1,len(ct_dict)+1):
        if not 'VIA_1_RES' in ct_dict[str(i)]:
            continue
        
        f.write(str(i) + ' ' + str(ct_dict[str(i)]['VIA_1_RES']) + '\n')
    
    f.write('END\n')

def get_corner_type(file):
    with open(file) as f:
        first_line = f.readline()
        corner_type = re.match('Corner Type: (\w+)',first_line, flags=re.IGNORECASE).group(1)
        
    return corner_type

def main():
    ct_dict = {}
    ## File that contains the cap table information
    files = './work/unit_parasitic_*.txt'
    for filename in glob.glob(files):
        ct_dict = parse_file(filename)
        # Get corner type 
        corner_type = get_corner_type(filename)
        
        if corner_type == 'Typical':
            corner_type = 'Typ'
            
        ## Write the information to the config file
        file = './output/config_file_' + corner_type+ '.txt'
        write_toFile(ct_dict, file)
    
main()