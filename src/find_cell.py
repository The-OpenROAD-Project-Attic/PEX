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

import global_var as glob
import matplotlib.path as Path
import numpy as np

# =============================================================================
#   
# =============================================================================
def find_cell(rp, net, lookup_dict, pin_dict, pin_used, find_pin = True, find_cell = True, prevent_duplicate = False):
    ## Multiplier to scale the unit
    unit_distance = glob.UNIT_DISTANCE
    
    rp_x = int(rp.x)
    rp_y = int(rp.y)
    
    if len(net.pin) != 0 and find_pin:
        for cell in net.pin:
            if rp.isVia:
                if glob.TECH_LEF_DICT['Layer'][pin_dict[cell[1]]['LAYER']]['metal_layer'] != rp.metal_layer \
                and glob.TECH_LEF_DICT['Layer'][pin_dict[cell[1]]['LAYER']]['metal_layer'] != rp.metal_layer + 1:
                    
                    continue
            else:
                if rp.metal_layer != pin_dict[cell[1]]['LAYER']:
                    continue
                    
            # Determine the bounding area of the pin
            if pin_dict[cell[1]]['orientation'] == 'N':
                if int(rp_y) < int(pin_dict[cell[1]]['Y']) + int(pin_dict[cell[1]]['dimension']['yt']) \
                and int(rp_y) > int(pin_dict[cell[1]]['Y']) + int(pin_dict[cell[1]]['dimension']['yb']):
                    if int(rp_x) == int(pin_dict[cell[1]]['X']) \
                    or (int(rp_x) >= int(pin_dict[cell[1]]['X']) + int(pin_dict[cell[1]]['dimension']['xl']) \
                    and int(rp_x) <= int(pin_dict[cell[1]]['X']) + int(pin_dict[cell[1]]['dimension']['xr'])):
                        if not cell[1] in pin_used:
                            pin_used.append(cell[1])
#                        else:
#                            print('PIN {} is redundant'.format(cell[1]))
                        rp.set_connected_to_pin
                        return pin_dict[cell[1]]['number'], ''
            
            elif pin_dict[cell[1]]['orientation'] == 'S':
                if int(rp_y) >= int(pin_dict[cell[1]]['Y']) - int(pin_dict[cell[1]]['dimension']['yt']) \
                and int(rp_y) <= int(pin_dict[cell[1]]['Y']) - int(pin_dict[cell[1]]['dimension']['yb']):
                    if int(rp_x) == int(pin_dict[cell[1]]['X'])\
                    or (int(rp_x) <= int(pin_dict[cell[1]]['X']) - int(pin_dict[cell[1]]['dimension']['xl']) \
                    and int(rp_x) >= int(pin_dict[cell[1]]['X']) - int(pin_dict[cell[1]]['dimension']['xr'])):
                        if not cell[1] in pin_used:
                            pin_used.append(cell[1])
#                        else:
#                            print('PIN {} is redundant'.format(cell[1]))
                        rp.set_connected_to_pin
                        return pin_dict[cell[1]]['number'], ''
            
            elif pin_dict[cell[1]]['orientation'] == 'W':
                if int(rp_y) == int(pin_dict[cell[1]]['Y']) \
                or (int(rp_y) >= int(pin_dict[cell[1]]['Y']) + int(pin_dict[cell[1]]['dimension']['xl']) \
                and int(rp_y) <= int(pin_dict[cell[1]]['Y']) + int(pin_dict[cell[1]]['dimension']['xr'])):
                    if int(rp_x) >= int(pin_dict[cell[1]]['X']) - int(pin_dict[cell[1]]['dimension']['yt']) \
                    and int(rp_x) <= int(pin_dict[cell[1]]['X']) + int(pin_dict[cell[1]]['dimension']['yb']):
                        if not cell[1] in pin_used:
                            pin_used.append(cell[1])
#                        else:
#                            print('PIN {} is redundant'.format(cell[1]))
                        rp.set_connected_to_pin
                        return pin_dict[cell[1]]['number'], ''
            
            elif pin_dict[cell[1]]['orientation'] == 'E':
                if int(rp_y) == int(pin_dict[cell[1]]['Y']) \
                or (int(rp_y) <= int(pin_dict[cell[1]]['Y']) - int(pin_dict[cell[1]]['dimension']['xl']) \
                and int(rp_y) >= int(pin_dict[cell[1]]['Y']) - int(pin_dict[cell[1]]['dimension']['xr'])):
                    if int(rp_x) <= int(pin_dict[cell[1]]['X']) + int(pin_dict[cell[1]]['dimension']['yt']) \
                    and int(rp_x) >= int(pin_dict[cell[1]]['X']) - int(pin_dict[cell[1]]['dimension']['yb']):
                        if not cell[1] in pin_used:
                            pin_used.append(cell[1])
#                        else:
#                            print('PIN {} is redundant'.format(cell[1]))
                        rp.set_connected_to_pin
                        return pin_dict[cell[1]]['number'], ''
    if find_cell:
        for cell in net.input:
            # Special Case
            if (net.hasDuplicate and cell[0] in net.get_duplicateCell) or prevent_duplicate or cell[0] in pin_used:
#                print('\nDUPLICATE')
                # To reduce # of iterations
                x_track = float(lookup_dict[cell[0]]['dimension']['x'])*unit_distance
                y_track = float(lookup_dict[cell[0]]['dimension']['y'])*unit_distance
                if not (rp_y > float(lookup_dict[cell[0]]['y']) and rp_y < (float(lookup_dict[cell[0]]['y']) + y_track)) \
                or not ((rp_x > float(lookup_dict[cell[0]]['x'])) and rp_x < (float(lookup_dict[cell[0]]['x']) + x_track)):
                    continue
                
                if get_cell_connection(rp, cell, net, lookup_dict):
                    if not cell[0] in pin_used:
                        pin_used.append(cell[0])
#                    else:
#                        print('PIN {} is redundant'.format(cell[0]))
                    rp.set_connected_to_pin
                    return lookup_dict[cell[0]]['number'], cell[1]
            else:
                x_track = float(lookup_dict[cell[0]]['dimension']['x'])*unit_distance
                y_track = float(lookup_dict[cell[0]]['dimension']['y'])*unit_distance
                if rp_y > float(lookup_dict[cell[0]]['y']) and rp_y < (float(lookup_dict[cell[0]]['y']) + y_track):
                    if (rp_x > (float(lookup_dict[cell[0]]['x']))) and rp_x < (float(lookup_dict[cell[0]]['x']) + x_track):
                        if not cell[0] in pin_used:
                            pin_used.append(cell[0])
#                        else:
#                            print('PIN {} is redundant'.format(cell[0]))
                        rp.set_connected_to_pin
                        return lookup_dict[cell[0]]['number'], cell[1]
                
        for cell in net.output:
            if (net.hasDuplicate and cell[0] in net.get_duplicateCell) or prevent_duplicate or cell[0] in pin_used:
#                print('\nDUPLICATE')
                # To reduce # of iterations
                x_track = float(lookup_dict[cell[0]]['dimension']['x'])*unit_distance
                y_track = float(lookup_dict[cell[0]]['dimension']['y'])*unit_distance
                if not (rp_y > float(lookup_dict[cell[0]]['y']) and rp_y < (float(lookup_dict[cell[0]]['y']) + y_track)) \
                or not ((rp_x > float(lookup_dict[cell[0]]['x'])) and rp_x < (float(lookup_dict[cell[0]]['x']) + x_track)):
                    continue
                
                if get_cell_connection(rp, cell, net, lookup_dict):
                    if not cell[0] in pin_used:
                        pin_used.append(cell[0])
#                    else:
#                        print('PIN {} is redundant'.format(cell[0]))
                    rp.set_connected_to_pin
                    return lookup_dict[cell[0]]['number'], cell[1]
            else:
                x_track = float(lookup_dict[cell[0]]['dimension']['x'])*unit_distance
                y_track = float(lookup_dict[cell[0]]['dimension']['y'])*unit_distance
                if rp_y > float(lookup_dict[cell[0]]['y']) and rp_y < (float(lookup_dict[cell[0]]['y']) + y_track):
                    if (rp_x > (float(lookup_dict[cell[0]]['x']))) and (rp_x < (float(lookup_dict[cell[0]]['x']) + x_track)):
                        if not cell[0] in pin_used:
                            pin_used.append(cell[0])
    #                    else:
    #                        print('PIN {} is redundant'.format(cell[0]))
                        rp.set_connected_to_pin
                        return lookup_dict[cell[0]]['number'], cell[1]
        
    return None, None

def get_cell_connection(rp, cell, net, lookup_dict, metal_layer = None):
    for inst in lookup_dict[cell[0]]['dimension'][cell[1]]:
        if inst[0] == 'RECT':
            rp_x = int(rp.x)
            rp_y = int(rp.y)
            
            x_left, x_right, y_bottom, y_top = get_rect_shape(lookup_dict, inst, cell)
            
            if is_inside_rectangle(rp_x,rp_y, x_left,x_right,y_bottom,y_top):
                return True

        if inst[0] == 'POLY':
            arr = np.array(get_poly_shape(lookup_dict, inst, cell))
            bbPath = Path.Path(arr)
#            print('-- rp: {} - arr: {}'.format(rp, arr))
            if bbPath.contains_point((int(rp.x),int(rp.y)), radius = -1):
                return True
            if bbPath.contains_point((int(rp.x),int(rp.y)), radius = 1):
                return True
        
    return False
        
def is_inside_rectangle(x,y, l, r, b, t):
#    print('rp: {} - {}'.format(x,y))
#    print('-- rect_dim: {} {} - {} {}'.format(l, b, r, t))
    if x >= l and x<= r:
        if t >= b and y <= t:
            return True
    return False

def get_rect_shape(lookup_dict, rect, cell):
    unit_distance = glob.UNIT_DISTANCE
    cell_orientation = lookup_dict[cell[0]]['orient']
    
    l = float(rect[2])* unit_distance
    r = float(rect[4]) * unit_distance
    b = float(rect[3])* unit_distance
    t = float(rect[5])* unit_distance
    x_track = float(lookup_dict[cell[0]]['dimension']['x'])*unit_distance
    y_track = float(lookup_dict[cell[0]]['dimension']['y'])*unit_distance
    
    if cell_orientation == 'N':
        x_left = float(lookup_dict[cell[0]]['x']) + l
        x_right = float(lookup_dict[cell[0]]['x']) + r
        y_bottom = float(lookup_dict[cell[0]]['y']) + b
        y_top = float(lookup_dict[cell[0]]['y']) + t
        return round(x_left, 1), round(x_right, 1), round(y_bottom, 1), round(y_top, 1)
    
    if cell_orientation == 'FN':
        x_left = float(lookup_dict[cell[0]]['x']) + x_track - r
        x_right = float(lookup_dict[cell[0]]['x']) + x_track - l
        y_bottom = float(lookup_dict[cell[0]]['y']) + b
        y_top = float(lookup_dict[cell[0]]['y']) + t
        return round(x_left, 1), round(x_right, 1), round(y_bottom, 1), round(y_top, 1)
    
    if cell_orientation == 'S':
        x_left = float(lookup_dict[cell[0]]['x']) + x_track - r
        x_right = float(lookup_dict[cell[0]]['x']) + x_track - l
        y_bottom = float(lookup_dict[cell[0]]['y']) + y_track - t
        y_top = float(lookup_dict[cell[0]]['y']) + y_track - b
        return round(x_left, 1), round(x_right, 1), round(y_bottom, 1), round(y_top, 1)
    
    if cell_orientation == 'FS':
        x_left = float(lookup_dict[cell[0]]['x']) + l
        x_right = float(lookup_dict[cell[0]]['x']) + r
        y_bottom = float(lookup_dict[cell[0]]['y']) + y_track - t
        y_top = float(lookup_dict[cell[0]]['y']) + y_track - b
        return round(x_left, 1), round(x_right, 1), round(y_bottom, 1), round(y_top, 1)
    
def get_poly_shape(lookup_dict, poly, cell):
    arr = []
    unit_distance = glob.UNIT_DISTANCE
    cell_orientation = lookup_dict[cell[0]]['orient']
    
    x_track = float(lookup_dict[cell[0]]['dimension']['x'])*unit_distance
    y_track = float(lookup_dict[cell[0]]['dimension']['y'])*unit_distance
    loc_x = float(lookup_dict[cell[0]]['x'])
    loc_y = float(lookup_dict[cell[0]]['y'])
    
    if cell_orientation == 'N':
        for i in range (2,len(poly),2):
            px = round(loc_x + float(poly[i])*unit_distance, 0)
            py = round(loc_y + float(poly[i+1])*unit_distance, 0)
            
            arr.append([px, py])
        
        return arr
    
    if cell_orientation == 'FN':
        for i in range (2,len(poly),2):
            px = round(loc_x + x_track - float(poly[i])*unit_distance, 0)
            py = round(loc_y + float(poly[i+1])*unit_distance, 0)
            
            arr.append([px, py])
        
        return arr
    
    if cell_orientation == 'S':
        for i in range (2,len(poly),2):
            px = round(loc_x + x_track - float(poly[i])*unit_distance, 0)
            py = round(loc_y + y_track - float(poly[i+1])*unit_distance, 0)
            
            arr.append([px, py])
        
        return arr
    
    if cell_orientation == 'FS':
        for i in range (2,len(poly),2):
            px = round(loc_x + float(poly[i])*unit_distance, 0)
            py = round(loc_y + y_track - float(poly[i+1])*unit_distance, 0)
            
            arr.append([px, py])
        
        return arr