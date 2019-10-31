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
import global_var as glob

def parse_def_via_section(line, cur_via, tech_lef):
    if re.match(r'^\s*[+]\s+RECT\s+(\w+)', line):
        metal_layer = re.match(r'^\s*[+]\s+RECT\s+(\w+)', line).group(1)
        metal_layer = (metal_layer)
        
        if tech_lef['Layer'][metal_layer]['type'] == 'CUT':
            cur_via.set_viaCutLayer(metal_layer)
            pp = '\s*[(]\s*([-+]?\d+)\s*([-+]?\d+)\s*[)]\s*'    # Pattern of the rect points
            pin_dimension = re.search(r'{}{}'.format(pp, pp), line)
            pin_dimension = [float(pin_dimension.group(1))/glob.UNIT_DISTANCE, float(pin_dimension.group(2))/glob.UNIT_DISTANCE, \
                             float(pin_dimension.group(3))/glob.UNIT_DISTANCE, float(pin_dimension.group(4))/glob.UNIT_DISTANCE]
            cur_via.set_viaDimension(pin_dimension)
            
        else:
            cur_via.set_viaLayerAssignemnt(metal_layer, tech_lef)
            
    if re.match(r'^\s*[+]\s+CUTSIZE', line):
        cut_size = re.match(r'\s*[+]\s+CUTSIZE\s+(\d+)\s+(\d+)', line)
        x_size = float(cut_size.group(1))/glob.UNIT_DISTANCE
        y_size = float(cut_size.group(2))/glob.UNIT_DISTANCE
        
        cur_via.set_viaDimension([x_size, y_size])
        
    if re.match(r'^\s*[+]\s+LAYERS\s+', line):
        layers = re.match(r'^\s*[+]\s+LAYERS\s+(\w+)\s+(\w+)\s+(\w+)', line)
        bl = layers.group(1)
        cl = layers.group(2)
        tl = layers.group(3)
        
        cur_via.set_viaCutLayer(cl)
        cur_via.set_viaLayerAssignemnt(bl, tech_lef)
        cur_via.set_viaLayerAssignemnt(tl, tech_lef)
        
            
def append_via_data_to_dict(cur_via, tech_lef):
    tech_lef['Via'][cur_via.get_viaName] = {}     # Initialize the key to the dictionary
    tech_lef['Via'][cur_via.get_viaName]['cuts'] = cur_via.get_viaTotalCuts
    tech_lef['Via'][cur_via.get_viaName]['top_layer'] = cur_via._top_layer
    tech_lef['Via'][cur_via.get_viaName]['bottom_layer'] = cur_via._bottom_layer
    tech_lef['Via'][cur_via.get_viaName]['bottom_layer_number'] = tech_lef['Layer'][cur_via._bottom_layer]['metal_layer']