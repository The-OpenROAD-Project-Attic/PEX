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
import matplotlib.path as Path
import numpy as np
import global_var as glob

class Component(object):
    def __init__(self, name = '', cell = '', orient=None, x=0, y=0, number = 0):
        self.compName = name
        self.type   = cell
        self.orient = orient
        self.x      = x
        self.y      = y
        self.number = number
        self.property = []

    def set_location(self, x, y):
        self.x  = x
        self.y  = y

    def set_orientation(self, orient):
        self.orient = orient
    
    def set_property(self, data):
        self.property.append(data)
        
    def set_direction(self, dir):
        if dir == 'INPUT':
            dir = 'I'
        elif dir == 'OUTPUT':
            dir = 'O'
            
        self.direction = dir
    
    def __repr__(self):
        return self.name
            

class NET(object):
    def __init__(self, name, number = 0):
        self.name = name
        self.regression_data = []
        self.cell = []
        self.input = []
        self.output = []
        self.pin = []
        self.number = number
        self.wire_list = []
        self.rc_tree = None
        self.coupling_capacitance = []
        self.property = []
        self._virtual = None
        self.__duplicate_cell = []
    
    def add_cell(self, cell):
        self.cell = cell
    
    def add_pin(self, l):
        self.pin.append(l)
        
    def set_virtual(self,l):
        self._virtual = l
        
    @property
    def get_duplicateCell(self):
        return self.__duplicate_cell
    
    @property
    def get_virtual(self):
        return self._virtual
    
    @property
    def isVirtual(self):
        if self._virtual:
            return True
        return False
    
    @property
    def hasPin(self):
        if self.pin:
            return True
        return False
    
    @property
    def hasDuplicate(self):
        if self.__duplicate_cell:
            return True
        return False
    
    def add_regression_data(self, val):
        self.regression_data.append(val)
        
    def add_input(self, l):
        self.input.append(l)
        
    def add_output(self, l):
        self.output.append(l)
        
    def set_wire_list(self, l):
        self.wire_list.append(l)
    
    def get_wire_list(self):
        return self.wire_list
    
    def add_cc(self, l):
#        self.coupling_capacitance.append(l)
        self.coupling_capacitance = l
        
    def set_rc_tree(self, l):
        self.rc_tree = l
   
    def set_property(self, data):
        self.property.append(data)
    
    def set_duplicate_cell(self):
        x = self.input
        _size = len(x) 
        repeated = [] 
        for i in range(_size): 
            k = i + 1
            for j in range(k, _size): 
                if x[i][0] == x[j][0] and x[i][0] not in repeated: 
                    repeated.append(x[i][0]) 
        
        if repeated:
            self.__duplicate_cell = repeated

class routingPoints(object):
    def __init__(self, x, y, metal_layer = None, ext = None, via_name = None):
        self.x = x
        self.y = y
        self.extPoint = ext
        self.metal_layer = metal_layer
        self.number = None
        self.NEXT = []
        self.via_name = via_name
        self.connected_to_pin = False
    
    @property
    def is_connected_to_pin(self):
        return self.connected_to_pin
    
    @property
    def set_connected_to_pin(self):
        self.connected_to_pin = True
    
    def set_next(self, data):
        self.NEXT.append(data)
    
    def set_number(self, num):
        self.number = num
    
    def set_metal_layer(self, l):
        self.metal_layer = l
        
    @property
    def hasExt(self):
        if self.extPoint != None:
            return True
        return False
    
    @property
    def isVia(self):
        if self.via_name != None:
            return True
        return False
    
    @property
    def get_extPoint(self):
        return self.extPoint
    
    def __repr__(self):
        if self.hasExt:
            return '( {} {} {} )'.format(self.x, self.y, self.extPoint)
        return '( {} {} )'.format(self.x, self.y)
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def isBetween(self, other, next_other):
        if (int(self.y) == int(other.y) and int(self.y) == int(next_other.y)) \
        and ((int(self.x) < int(other.x) and int(self.x) > int(next_other.x)) \
        or (int(self.x) > int(other.x) and int(self.x) < int(next_other.x))):
            return True
        
        if (int(self.x) == int(other.x) and int(self.x) == int(next_other.x)) \
        and ((int(self.y) < int(other.y) and int(self.y) > int(next_other.y)) \
        or (int(self.y) > int(other.y) and int(self.y) < int(next_other.y))):
            return True
        
        return False
    
class Wire(object):
    def __init__(self, rp = [], virtual = False, metal_layer = None):
        self.routing_points = rp
        self.virtual = virtual
        self.metal_layer = metal_layer
        self.adj = []
        self.depth = None
        self.branch_rp = []

    def add_adj(self, new):
        self.adj.append(new)
        
    def add_rp(self, rp):
        self.routing_points.append(rp)
    
    def set_branchRP(self, rp):
        self.branch_rp.append(rp)
        
    def set_depth(self, depth):
        self.depth = depth
        
    def set_prev(self, prev):
        self.prev = prev
        
    @property
    def isWire(self):
        if self.isVia:
            return False
        return True
    
    # Eliminating star and link the two routing points 
    def init(self, prev_x, prev_y):
        self.eliminate_star(prev_x, prev_y)
        if not self.isVia:
            self.routing_points[0].next = self.routing_points[1]
    
    @property
    def isVirtual(self):
        return self.virtual
    
    @property
    def isVia(self):
        return False
    
    def eliminate_star(self, prev_x, prev_y):
        if not self.isVia:
            if self.routing_points[1].x == '*':
                self.routing_points[1].x = self.routing_points[0].x
            
            if self.routing_points[1].y == '*':
                self.routing_points[1].y = self.routing_points[0].y
                
        if self.isVia:
            if self.routing_points[0].x == '*':
                self.routing_points[0].x = prev_x
            
            if self.routing_points[0].y == '*':
                self.routing_points[0].y = prev_y
    
    def __repr__(self):
        if self.isVirtual:
            return 'Virtual --- {}, {}, {} {} {}'.format(self.prev,self.depth, self.metal_layer, self.routing_points[0], self.routing_points[1])
        
        return '{}, {}, {} {} {}'.format(self.prev,self.depth, self.metal_layer, self.routing_points[0], self.routing_points[1])
    
    # Check if the point is between two nodes
    def isPartOf(self, other):
        if self.isVia and not other.isVia:
            if ((int(self.routing_points[0].y) < int(other.routing_points[0].y) and int(self.routing_points[0].y) > int(other.routing_points[1].y)) \
            or (int(self.routing_points[0].y) > int(other.routing_points[0].y) and int(self.routing_points[0].y) < int(other.routing_points[1].y))) \
            and (int(self.routing_points[0].x) == int(other.routing_points[0].x) and int(self.routing_points[0].x) == int(other.routing_points[1].x)):
#                print('via x ------ {} - {}'.format(self.routing_points[0], other))
                return True, None
            
            if ((int(self.routing_points[0].x) < int(other.routing_points[0].x) and int(self.routing_points[0].x) > int(other.routing_points[1].x)) \
            or (int(self.routing_points[0].x) > int(other.routing_points[0].x) and int(self.routing_points[0].x) < int(other.routing_points[1].x))) \
            and (int(self.routing_points[0].y) == int(other.routing_points[0].y) and int(self.routing_points[0].y) == int(other.routing_points[1].y)):
#                print('via y ------ {} - {}'.format(self.routing_points[0], other))
                return True, None
        
        elif not self.isVia and not other.isVia:
            for i in range(2):
                if (((int(self.routing_points[i].y) < int(other.routing_points[0].y) and int(self.routing_points[i].y) > int(other.routing_points[1].y)) \
                or (int(self.routing_points[i].y) > int(other.routing_points[0].y) and int(self.routing_points[i].y) < int(other.routing_points[1].y))) \
                and (int(self.routing_points[i].x) == int(other.routing_points[0].x) and int(self.routing_points[i].x) == int(other.routing_points[1].x))):
#                    print('y ------ {} - {}'.format(self.routing_points[i], other))
                    return True, i
                
                if (int(self.routing_points[i].y) == int(other.routing_points[0].y) and int(self.routing_points[i].y) == int(other.routing_points[1].y)) \
                and ((int(self.routing_points[i].x) < int(other.routing_points[0].x) and int(self.routing_points[i].x) > int(other.routing_points[1].x)) \
                or (int(self.routing_points[i].x) > int(other.routing_points[0].x) and int(self.routing_points[i].x) < int(other.routing_points[1].x))):
#                        print('x ------ {} - {}'.format(self.routing_points[i], other))
                        return True, i
            
        return False, None    
        
class Via(Wire):
    def __init__(self, name, rp = [], metal_layer = None, bottom_layer = None):
        Wire.__init__(self, rp, metal_layer = metal_layer)
        self.viaName = name
        self.bottom_layer = bottom_layer
        if self.bottom_layer == None:
            if glob.TECH_LEF_DICT and self.viaName in glob.TECH_LEF_DICT['Via']:
                self.set_bottom_layer(glob.TECH_LEF_DICT['Via'][self.viaName]['bottom_layer_number'])
            
    
    @property
    def get_viaName(self):
        return self.viaName
    
    def set_bottom_layer(self, bl):
        self.bottom_layer = bl
        
    @property
    def isVia(self):
        return True
    
    def __repr__(self):
        return '{}, {}, {}  {}  {}'.format(self.prev,self.depth, self.metal_layer, self.routing_points[0], self.viaName)
   

class Pin(object):
    def __init__(self, number = None):
        self.name = ''
        self.net = ''
        self.direction = ''
        self.layer = ''
        self.x = '0'
        self.y = '0'
        self.orientation = ''
        self.dimension = {}
        self.number = number
    
    def set_name(self, data):
        self.name = data
        
    def set_net(self, data):
        self.net = data
        
    def set_orientation(self, data):
        self.orientation = data
    
    def set_direction(self, data):
        self.direction = data
        
    def set_layer(self, data):
        self.layer = data
        
    def set_x(self, data):
        self.x = data
        
    def set_y(self, data):
        self.y = data    
    
    def set_dimension(self, data):
        self.dimension = {'xl' : data[0] , 'xr' : data[2], 'yb' : data[1], 'yt' : data[3]}
        
    def __repr__(self):
        return self.net + ' ' + self.direction + ' ' + self.layer  + ' ' + self.x + ' ' + self.y
        
class Node(Wire):
    def __init__(self, rp = None):
        Wire.__init__(self, rp)
        self.adj = []
        self.prev = None
        self.depth = None
        
    def add_adj(self, new):
        self.adj.append(new)
        
    def set_depth(self, depth):
        self.depth = depth
        
    def set_prev(self, prev):
        self.prev = prev
    
""" BELOW CLASSES ARE USED FOR LEF PARSER """
class LEF_Metal_Info(object):
    def __init__(self, layer='', layer_type=''):
        self._layer_name = layer
        self._type = layer_type
        
    def set_layerName(self, l):
        self._layer_name = l
        
    def set_layerType(self, l):
        self._type = l
    
    @property
    def get_layerName(self):
        return self._layer_name
        
    @property
    def get_layerType(self):
        return self._type

class LEF_Metal_Cut(LEF_Metal_Info):
    def __init__(self, layer='', layer_type=''):
        super().__init__(layer, layer_type)
        self._className = ''
        self._viaWidth = ''
        self._viaLength = ''
        self._cuts = '1'
        self._hasCutClass = False
        
    def set_layerClassName(self, l):
        self._className = l
        
    def set_viaWidth(self, l):
        self._viaWidth = l
        
    def set_viaLength(self, l):
        self._viaLength = l
        
    def set_viaCuts(self, l):
        self._cuts = l
    
    def set_cutClass(self, l):
        self._hasCutClass = l
        
    # Getters
    @property
    def get_layerClassName(self):
        return self._className
    
    @property
    def get_viaWidth(self):
        return self._viaWidth
    
    @property
    def get_viaLength(self):
        return self._viaLength
    
    @property
    def get_viaCuts(self):
        return self._cuts
    
    @property
    def isCutClass(self):
        return self._hasCutClass
        
class LEF_Metal_Routing(LEF_Metal_Info):
    def __init__(self, layer='', layer_type='', layer_number = 0):
        super().__init__(layer, layer_type)
        self._width = ''
        self._spacing = ''
        self._pitch = ''
        self._direction = ''
        self._layer_number = layer_number
    
    # Setters
    def set_layerWidth(self, l):
        self._width = l
    
    def set_layerSpacing(self, l):
        self._spacing = l
    
    def set_layerPitch(self, l):
        self._pitch = l
        
    def set_layerDirection(self, l):
        self._direction = l
    
    # Getters
    @property
    def get_layerWidth(self):
        return self._width
    
    @property
    def get_layerSpacing(self):
        return self._spacing
    
    @property
    def get_layerPitch(self):
        return self._pitch
    
    @property
    def get_layerDirection(self):
        return self._direction
    
class LEF_VIA_Info(object):
    def __init__(self, via_name='', number_of_cuts=0):
        self._via_name = via_name
        self._cuts = number_of_cuts
        self._via_dimension = []
        self._cut_layer = ''
        self._top_layer =''
        self._bottom_layer = ''
        
    def set_viaName(self, l):
        self._via_name = l
        
    def set_viaCuts(self, l):
        self._cuts = l
        
    def set_viaCutLayer(self, l):
        self._cut_layer = l
        
    def set_viaLayerAssignemnt(self, l, techLEF_dict):
        if self._top_layer == '':
            self._top_layer = l
            
        else:
            if techLEF_dict['Layer'][self._top_layer]['metal_layer'] > techLEF_dict['Layer'][l]['metal_layer']:
                self._bottom_layer = l
            
            else:
                self._bottom_layer = self._top_layer
                self._top_layer = l
            
    def set_viaDimension(self, l):
        self._via_dimension.append(l)
        
    @property
    def get_viaName(self):
        return self._via_name
    
    @property
    def get_viaTotalCuts(self):
        return self._cuts
    
    @property
    def get_viaDimension(self):
        return self._via_dimension
    
    @property
    def get_viaCutLayer(self):
        return self._cut_layer
    
class MACRO(object):
    def __init__(self, name):
        self._name = name
        self._height = 0
        self._width = 0
        self._pin = []
    
    def set_height(self, he):
        self._height = he
    
    def set_width(self, he):
        self._width = he
        
    def set_pin(self, pin):
        self._pin.append(pin)
        
    @property
    def get_macroName(self):
        return self._name
    
    @property
    def get_pin(self):
        return self._pin
    
    @property
    def get_starting_point(self):
        for pin in self.get_pin:
            if pin.get_direction == 'OUTPUT':
                out_pin = pin
            
            if pin.get_direction == 'INPUT':
                in_pin = pin
        
        # Algorithm for Poly Shape 
        if not in_pin._isRect:
            in_point, in_next_point = self.find_edge_point(in_pin, False) 
            in_top, in_bottom = self.find_top_bottom_point(in_point)
                
            out_point, out_next_point = self.find_edge_point(out_pin, True)
            out_top, out_bottom = self.find_top_bottom_point(out_point)
            
            # Setting up the variable
            POY = self.find_overlapping_pointY(float(in_top), float(in_bottom), float(out_top), float(out_bottom))
            POX = self.find_starting_pointX(float(out_point.x), float(out_next_point.x), True)
            POX_IN = self.find_starting_pointX(float(in_point.x), float(in_next_point.x), False)
            start_length = self._width - POX + POX_IN
            
            assert out_pin._enclosure.contains_point((POX,POY)), 'POX and POY point is not inside the PIN'
            assert in_pin._enclosure.contains_point((POX_IN,POY)), 'POX_IN and POY point is not inside the PIN'
            return POX, POY, round(start_length,5)
            
    def find_overlapping_pointY(self, in_top, in_bottom, out_top, out_bottom):
        def mirror_value(top, bottom, height):
            mirrored_top = height - bottom
            mirrored_bottom = height - top 
            return mirrored_top, mirrored_bottom
        
        predicted_point = self._height / 2
#        mw = techLEF_dict['Layer']['M1']['width']
#        top_predicted_point = (self._height / 2) + mw/2
#        bottom_predicted_point = (self._height / 2) - mw/2
        
        # FIND THE MIRRORED POINT
        mirrored_in_top, mirrored_in_bottom = mirror_value(in_top, in_bottom, self._height)
        mirrored_out_top, mirrored_out_bottom = mirror_value(out_top, out_bottom, self._height)
        
        
        if predicted_point <= in_top and predicted_point >= in_bottom \
        and predicted_point <= out_top and predicted_point >= out_bottom \
        and predicted_point <= mirrored_in_top and predicted_point >= mirrored_in_bottom \
        and predicted_point <= mirrored_out_top and predicted_point >= mirrored_out_bottom:
            return predicted_point
    
        
    def find_top_bottom_point(self, point):
        if point.y > point.next.y:
            top = point.y
            bottom = point.next.y
            
        else:
            top = point.next.y
            bottom = point.y
            
        return top, bottom
        
    def find_edge_point(self, point, left):
        storage = []
        # Find Left most point
        edge_point = point.get_coordinate
        edge_point = sorted(edge_point, key=lambda x:x.x, reverse=left)
        for point in edge_point:
            if point.direction == 'V':
                storage.append(point)
        
        return storage[0], storage[1]
    
    def find_starting_pointX(self,a,b,isOutPin):
        if isOutPin:
            if a > b:
                return (round(b+(a-b)/2,4))
            else:
                return (round(a+(b-a)/2,4))
                
        else:
            if a < b:
                return (round(b+(a-b)/2,4))
            else:
                return (round(a+(b-a)/2,4))
    
class MACRO_PIN(object):
    def __init__(self, pin_name):
        self._pin_name = pin_name
        self._direction = None
        self._coordinate = None
        self._isRect = False
        self._enclosure = None
        
    def set_direction(self, dire):
        self._direction = dire
        
    def set_coordinate(self, points):
        if not self._isRect:
            if self._coordinate == None:
                self._coordinate = points
            else:
                for i in points:
                    self._coordinate.append(i)
                
        else:
            if self._coordinate == None:
                self._coordinate = []
                self._coordinate.append(self.build_rectangle(points))
            else:
                for i in points:
                    self._coordinate.append(self.build_rectangle(points))
        
    @property
    def get_coordinate(self):
        return self._coordinate
    
    @property
    def get_direction(self):
        return self._direction
    
    def build_rectangle(self, coordinate):
        rect = RECTANGLE() 
        x1 = coordinate[0]
        x2 = coordinate[2]
        y1 = coordinate[1]
        y2 = coordinate[3]
        
        # Determine the x coor
        if x1 > x2:
            rect.x_left = x2
            rect.x_right = x1
        else:
            rect.x_left = x1
            rect.x_right = x2
        
        # Determine the y coor
        if y1 > y2:
            rect.y_bottom = y2
            rect.y_top = y1
        else:
            rect.y_bottom = y1
            rect.y_top = y2
            
        return rect
        
    def convert_coordinate_to_Point(self):
        point = []
        arr = []
        coordinate = self.get_coordinate
        for i in range (0,len(coordinate),2):
            cl_point = POINT(coordinate[i],coordinate[i+1])
            point.append(cl_point)
            arr.append([coordinate[i],coordinate[i+1]])
        arr = np.array(arr)
        bbPath = Path.Path(arr)
            
        for i in range (0,len(point)):
            if i == 0:
                if point[i].x == point[len(point)-1].x:
                    point[i].prev = point[len(point)-1]
                    
                elif point[i].y == point[len(point)-1].y:
                    point[i].prev = point[len(point)-1]
                    
            else:
                if point[i].x == point[i-1].x:
                    point[i].prev = point[len(point)-1]
                
                elif point[i].y == point[i-1].y:
                    point[i].prev = point[len(point)-1]
                    
            if i == len(point)-1:
                if point[i].x == point[0].x:
                    point[i].next = point[0]
                    point[i].direction = 'V' 
                    
                elif point[i].y == point[0].y:
                    point[i].next = point[0]
                    point[i].direction = 'H'
                    
            else:
                if point[i].x == point[i+1].x:
                    point[i].next = point[i+1]
                    point[i].direction = 'V' 
                    
                elif point[i].y == point[i+1].y:
                    point[i].next = point[i+1]
                    point[i].direction = 'H'
        
        # Set the coordinate and the bounding box of the polygon        
        self._coordinate = point
        self._enclosure = bbPath
            
class POINT(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.prev = None
        self.Next = None
        self.direction = None   # HORIZONTAL or Vertical
    
    def __repr__(self):
        return 'x = ' + self.x + ' , y = ' + self.y

class RECTANGLE(object):
    def __init__(self):
        self.x_left = 0
        self.x_right = 0
        self.y_top = 0
        self.y_bottom = 0
        self.width = 0
        self.length = 0
        
    def set_width(self, left, right):
        self.width = left - right
        
    def set_length(self, top, bottom):
        self.width = top - bottom
