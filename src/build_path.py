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

import re
import Class as cl
import global_var as glob
from find_cell import find_cell
import sys

# =============================================================================
# Desc: Determine whether the cell is an input or output
#   Input: The NET class object and the data itself
# =============================================================================
def net_inputOutput(obj, data, cell_coor_dict):
    num = len(data)

    for i in range (0,num,2):
        if (data[i] == 'PIN'):
            obj.add_pin([data[i], data[i+1]])
            i += 1
            continue
        
        if data[i] in cell_coor_dict:
            if cell_coor_dict[data[i]]['pin'][data[i+1]]['dir'] == 'input':
                obj.add_input([data[i], data[i+1]])
                i += 1
                continue
            
            if cell_coor_dict[data[i]]['pin'][data[i+1]]['dir'] == 'output':
                obj.add_output([data[i], data[i+1]])
                i += 1
                continue
            
def parse_net(line, net, cell_coor_dict):
    # Find compName or PIN, and pinName 
    pin_name_pattern = '(\s*[(]\s+.+\s+.+\s+[)])'
    net_name_prior_to_pin_name_pattern = '(^\s*[-]\s+\S+\s+[(]\s+.+\s+.+\s+[)])'#.format(net.name)
    pin_name_pattern = r'{}|{}'.format(net_name_prior_to_pin_name_pattern, pin_name_pattern)
    if re.match(pin_name_pattern, line):      
        data = re.findall(r'(?![(|)|+|-])\S+', line)
        if re.match(r'{}'.format(net_name_prior_to_pin_name_pattern), line):
            del data[0] # First data is the net name
        
        # Process the pinName section data
        net_inputOutput(net, data, cell_coor_dict)   
        net.set_duplicate_cell() # Check whether the net has duplicate cell
#        print('\n'+net.name)
#        print(data)
    
    # Find the wire information - Length, Metal Layer
    if re.search(r'([+]\s*(ROUTED|FIXED|NOSHIELD|COVER))|NEW',line):
        rw_data = process_regularWiring(line)
        
        # Add the processed regular wiring data to the set of a wire list 
        if rw_data:     # Check if the value is none Type or not
            for rw in rw_data:
                net.set_wire_list(rw)
        
def process_regularWiring(line):
    """
    # regularWiring = 
    # {+ ROUTED | + FIXED | + COVER | + NOSHIELD} 
    # layerName [TAPER | TAPERRULE rulename] [STYLE styleNum ] 
    #    routingPoints
    # [NEW layerName [TAPER | TAPERRULE rulename] [STYLE styleNum ]
    #    routingPoints
    # ] ...
    #
    # routingPoints =
    # ( x y [value] ) 
    # {( x * [value]) | ( * y [value]) | ( * * [value] ) | viaName | + RECT ( delta1x 
    #              delta1y delta2x delta2y ) | + VIRTUAL ( x y ) ]...] 
    """
    
    # Get metal_layer
    if re.search(r'(ROUTED|FIXED|NOSHIELD|COVER)|NEW\s*(\w+)', line):
        metal_layer = re.search(r'(ROUTED|FIXED|NOSHIELD|COVER|NEW)\s*(\w+)', line).group(2)
    
    # Patterns for regular wiring section
    mask = '(\s*MASK\s*(\d+)\s*)?'
    via = '(\s*(\w+))'
    orient = '(\s*(\w+))?'
    rect = '(\s*RECT\s*[(]\s*([+-]?\d+)\s*([+-]?\d+)\s*([+-]?\d+)\s*([+-]?\d+)\s*[)])'
    virtual = '(\s*VIRTUAL\s*[(]\s*(\d+|[*])\s*(\d+|[*])\s*[)])'
    rp = '([(]\s*(\d+|[*])\s*(\d+|[*])\s*((\d+)\s*)?[)])'
    
    rp_pattern = r'(?=({}\s*({}{}|({}{})|({})|({}{}{}))))'.format(rp, mask, rp, mask, rect, virtual, mask, via, orient)
    rp_pattern = re.compile(rp_pattern)
    matches = rp_pattern.finditer(line)
    
    # Get all the matched pattern
    results = [match.group(1) for match in matches]
    
    # Initializing vars
    prev_x = None
    prev_y = None
    rp_storage = []
    
    for result in results:
        routing_points_obj = create_node(result, metal_layer)
        
        # If the object contains data, store the variable to
        if routing_points_obj:
            routing_points_obj.init(prev_x, prev_y)
            rp_storage.append(routing_points_obj)
            
            if routing_points_obj.isVia:
                prev_x, prev_y = routing_points_obj.routing_points[0].x, routing_points_obj.routing_points[0].y
            else:
                prev_x, prev_y = routing_points_obj.routing_points[1].x, routing_points_obj.routing_points[1].y
                
    return rp_storage

def create_node(info, metal_layer):
    # Patterns for regular wiring section
    mask = '(\s*MASK\s*(\d+)\s*)?'
    via = '\s*(\w+)'
    virtual = '\s*VIRTUAL\s*[(]\s*(\d+|[*])\s*(\d+|[*])\s*[)]'
    rp = '[(]\s*(\d+|[*])\s*(\d+|[*])\s*(\d+)?\s*?[)]'
    
    cur_rp = None
    rp_storage = []
    
    # Wire with/out mask info
    if re.match(r'{}{}\s+{}'.format(rp,mask,rp), info):
        matches = re.finditer(r'{}'.format(rp), info)
        for match in matches:
            cur_rp = cl.routingPoints(match.group(1), match.group(2), \
                                      ext = match.group(3) if match.group(3) != None else None)
            
            cur_rp.set_metal_layer(metal_layer)
            rp_storage.append(cur_rp)
        
        wire = cl.Wire(rp = rp_storage, metal_layer = metal_layer)
        cur_rp.set_metal_layer(metal_layer)
        
        return wire
    
    elif re.match(r'{}{}{}'.format(rp,mask,virtual), info):
        matches = re.finditer(r'{}'.format(rp), info)
        for match in matches:
            cur_rp = cl.routingPoints(match.group(1), match.group(2), \
                                      ext = match.group(3) if match.group(3) != None else None)
            
            cur_rp.set_metal_layer(metal_layer)
            rp_storage.append(cur_rp)
        
        wire = cl.Wire(rp = rp_storage, metal_layer = metal_layer, virtual = True)
        
        return wire
        
    # Wire with via info
    elif re.match(r'{}{}\s+{}'.format(rp,mask,via), info) and not re.search('RECT|VIRTUAL', info):
        match = re.match(r'{}{}\s+{}'.format(rp, mask, via), info)
        via_name = match.group(6)
        cur_rp = cl.routingPoints(match.group(1), match.group(2), \
                                  ext = match.group(3) if match.group(3) != None else None, via_name = via_name)
        rp_storage.append(cur_rp)
        assert via_name, 'Can\'t capture via name'
        
        via = cl.Via(via_name, rp = rp_storage, metal_layer = metal_layer)
        cur_rp.set_metal_layer(via.bottom_layer)
        
        return cl.Via(via_name, rp = rp_storage, metal_layer = metal_layer)

def build_path(net, cell_coor_dict, pins):
    assert net.wire_list, 'ERROR - all_rp varible does not contain data'
    queue = []
    parent = []
    node_number = 1
    pin_used = [] # for testing
    
    all_rp = net.wire_list.copy()
    
    # To avoid having virtual connection on the first node
    for i in range (0,len(all_rp)):
        if all_rp[i].isVirtual:
            continue
        
        queue.append(all_rp.pop(i))
        node_number, first_node = init_starting_node(queue[0], net, cell_coor_dict, pins, node_number, pin_used)
        parent.append(first_node)
        break

    while queue or all_rp:
        deletes = []
        if not queue:
            for i in range (0,len(all_rp)):
                if all_rp[i].isVirtual:
                    continue
                
                queue.append(all_rp.pop(i))
                if not queue[0].isVia:
                    node_number, first_node = init_starting_node(queue[0], net, cell_coor_dict, pins, node_number, pin_used)
                    parent.append(first_node)
                break
        
        cur_rp = queue.pop(0)
        
        assert cur_rp, 'ERROR - cur_rp cannot be a NoneType [build_path function]'
        
        for i in range (0,len(all_rp)):
            rp = all_rp[i]
        
            if not rp.isVia:
                # VIA - WIRE: rp is a Wire Class and cur_rp is Via
                if cur_rp.isVia:
                    if cur_rp.bottom_layer == glob.TECH_LEF_DICT['Layer'][rp.metal_layer]['metal_layer'] \
                    or cur_rp.bottom_layer == glob.TECH_LEF_DICT['Layer'][rp.metal_layer]['metal_layer']-1:
                        found_connection = False
                        for a in range(0,2):
                            if cur_rp.routing_points[0] == rp.routing_points[a]:
                                setup_prev(cur_rp.routing_points[0], rp.routing_points[a], rp)
                                node_number = setup_depth(rp, net, cell_coor_dict, pins, node_number, pin_used)
#                                cur_rp.routing_points[0].set_next(rp.routing_points[a])
                                # JUST EDIT
                                rp.routing_points[a] = cur_rp.routing_points[0]
                                if a:
                                    cur_rp.routing_points[0].set_next(rp.routing_points[0])
                                else:
                                    cur_rp.routing_points[0].set_next(rp.routing_points[1])
                                    
                                queue.append(rp)
                                cur_rp.add_adj(rp)
                                deletes.append(i)
                                found_connection = True
                                break
                        if found_connection:
                            continue
                        
                        """ JUST ADDED """
                        part, _ = cur_rp.isPartOf(rp)
                        if part:
#                            print('VIA - WIRE')
                            # Assign the node numbers on the Wire routingPoints
                            node_number, _ = init_starting_node(rp, net, cell_coor_dict, pins, node_number, pin_used)
                            mid_rp = cl.routingPoints(cur_rp.routing_points[0].x, cur_rp.routing_points[0].y, metal_layer = rp.metal_layer)
                            mid_rp.set_number([net.number, node_number])
                            node_number += 1
                            isWorking = False
                            for a in range(2):
                                if connect_rps(cur_rp.routing_points[0], rp.routing_points[a], via_wire = True, mid_RP = mid_rp):
                                    isWorking = True
                                    break
                            
                            #######################################
                            if not isWorking and cur_rp.branch_rp:
                                for branch in cur_rp.branch_rp:
                                    if connect_rps(cur_rp.routing_points[0], branch):
                                        isWorking = True
                                        break
                                        
                            rp.set_branchRP(mid_rp)
                            assert isWorking, 'ERROR - Can\'t find connection! Net name:' + net.name
                            cur_rp.add_adj(rp)
                            queue.append(rp)
                            deletes.append(i)
                        """ """
                    continue
                    
                    
                # WIRE - WIRE: rp is a Wire, cur_rp is a Wire
                if not cur_rp.isVia:
                    if cur_rp.isVirtual and rp.isVirtual:
                        if glob.TECH_LEF_DICT['Layer'][rp.metal_layer]['metal_layer'] == 1:
                            deletes.append(i)
                            continue
                        
                    if cur_rp.metal_layer == rp.metal_layer:
                        is_looping = True
                        found_connection = False
                        for a in range(0,2):
                            for j in range (0,2):
                                if cur_rp.routing_points[a] == rp.routing_points[j]:
                                    setup_prev(cur_rp.routing_points[a], rp.routing_points[j], rp)
                                    node_number = setup_depth(rp, net, cell_coor_dict, pins, node_number, pin_used)
#                                    cur_rp.routing_points[a].set_next(rp.routing_points[j])
                                    rp.routing_points[j] = cur_rp.routing_points[a]
                                    if j:
                                        cur_rp.routing_points[a].set_next(rp.routing_points[0])
                                    else:
                                        cur_rp.routing_points[a].set_next(rp.routing_points[1])
                                    queue.append(rp)
                                    cur_rp.add_adj(rp)
                                    deletes.append(i)
                                    is_looping = False
                                    found_connection = True
                                    break
                            
                            if not is_looping:
                                break
                        if found_connection:
                            continue
                        
                        """ JUST ADDED """
                        part, ind = rp.isPartOf(cur_rp)
                        if part:
#                            print('WIRE - WIRE')
                            # Initialize the new Wire connection
                            node_number, _ = init_starting_node(rp, net, cell_coor_dict, pins, node_number, pin_used, index = ind)
                            # Break Up connection of cur_rp and put rp point in the middle
                            isWorking = False
                            for a in range(2):
                                if connect_rps(rp.routing_points[ind], cur_rp.routing_points[a]):
                                    isWorking = True
                                    break
                                
                            #######################################
                            if not isWorking and cur_rp.branch_rp:
                                for branch in cur_rp.branch_rp:
                                    if connect_rps(rp.routing_points[ind], branch):
                                        isWorking = True
                                        break
                                    
                            assert isWorking, 'ERROR - Can\'t find connection! Net name:' + net.name
                            cur_rp.add_adj(rp)
                            queue.append(rp)
                            deletes.append(i)
                        """ """
                    continue
                                
            # WIRE - VIA: cur_rp is a WIRE and rp is a VIA
            if not cur_rp.isVia:
                if rp.isVia:
                    if rp.bottom_layer == glob.TECH_LEF_DICT['Layer'][cur_rp.metal_layer]['metal_layer'] \
                    or rp.bottom_layer == glob.TECH_LEF_DICT['Layer'][cur_rp.metal_layer]['metal_layer']-1:
                        for a in range(0,2):
                            found_connection = False
                            if cur_rp.routing_points[a] == rp.routing_points[0]:
                                setup_prev(cur_rp.routing_points[a], rp.routing_points[0], rp)
                                node_number = setup_depth(rp, net, cell_coor_dict, pins, node_number, pin_used,connected_to_pin_or_cell = cur_rp.routing_points[a].is_connected_to_pin)
                                cur_rp.routing_points[a].set_next(rp.routing_points[0])
                                queue.append(rp)
                                cur_rp.add_adj(rp)
                                deletes.append(i)
                                found_connection = True
                                break
                        if found_connection:
                            continue
                        
                        """ JUST ADDED """
                        part, _ = rp.isPartOf(cur_rp)
                        if part:
#                            print('WIRE - VIA')
                            # Assign node number
                            node_number = setup_depth(rp, net, cell_coor_dict, pins, node_number, pin_used)

                            mid_rp = cl.routingPoints(rp.routing_points[0].x, rp.routing_points[0].y, metal_layer = cur_rp.metal_layer)
                            mid_rp.set_number([net.number, node_number])
                            node_number += 1
                            
                            isWorking = False
                            for a in range(2):
                                if connect_rps(rp.routing_points[0], cur_rp.routing_points[a], wire_via = True, mid_RP = mid_rp):
                                    isWorking = True
                                    break
                            
                            if not isWorking and cur_rp.branch_rp:
                                for branch in cur_rp.branch_rp:
                                    if connect_rps(rp.routing_points[0], branch, wire_via = True, mid_RP = mid_rp):
                                        isWorking = True
                                        break
                                    
                            assert isWorking, 'ERROR - Can\'t find connection! Net name:' + net.name
                            cur_rp.add_adj(rp)
                            queue.append(rp)
                            deletes.append(i)
                        """ """
                        
                    continue
                            
            
            # VIA - VIA: cur_rp and rp instances contain VIA nodes
            if cur_rp.isVia:
                if rp.isVia:
                    if cur_rp.bottom_layer == rp.bottom_layer+1 \
                    or cur_rp.bottom_layer == rp.bottom_layer-1:
                        if cur_rp.routing_points[0] == rp.routing_points[0]:
                            setup_prev(cur_rp.routing_points[0], rp.routing_points[0], rp)
                            node_number = setup_depth(rp, net, cell_coor_dict, pins, node_number, pin_used)
                            cur_rp.routing_points[0].set_next(rp.routing_points[0])
                            queue.append(rp)
                            cur_rp.add_adj(rp)
                            deletes.append(i)
                            continue
                continue
        
        # Delete the matched regularWiring
        if len(deletes) > 0:
            j = 0
            for i in deletes:
                del all_rp[i-j]
                j += 1
        
        # If the regularWiring node does not have an adjacent node
        # check for connection to a pin or port
        if len(cur_rp.adj) == 0:
            if cur_rp.isVia and cur_rp.bottom_layer == 1:
                continue
            node_number = setup_depth(cur_rp, net, cell_coor_dict, pins, node_number, pin_used, no_adjecent = True)
    
#    print('\nNet: ' + net.name)
#    print('Total Parent Node: {}'.format(len(parent)))
#    for node in parent:
#        dfs(node)
#    print('END')
    
    if len(pin_used) != (len(net.pin) + len(net.input) + len(net.output) - len(net.get_duplicateCell)):
        print('ERROR - Total Pin Comparison {} - {}'.format(pin_used, (len(net.pin) + len(net.input) + len(net.output))))

    # Add the path to the NET class
    net.set_rc_tree(parent)
    net.wire_list.clear()
        
def dfs(parent):
#    print(parent)
    for c in parent.NEXT:
        if c.isVia and not parent.isVia:
            print('{}, {}, {} {} {}'.format(parent.number, c.number, c.metal_layer, c, c.via_name))
            
        elif parent.isVia and not c.isVia:
            print('{}, {}, {} {} {} {}'.format(parent.number, c.number, c.metal_layer, c, parent, parent.via_name))
        
        else:
            print('{}, {}, {} {} {}'.format(parent.number, c.number, c.metal_layer, parent, c))
        dfs(c)
    
# =============================================================================
# 
# =============================================================================
def init_starting_node(head_node, net, cell_coor_dict, pins, node_number, pin_used, index = 1):
#    assert not (head_node.isVia and len(net.wire_list) != 1), '{} - {}'.format(net.name, head_node)#'ERROR - The head of the node is a Via!' + str(net.name)
    if index:
        last_index = 0
    else:
        last_index = 1
        
    if not head_node.isVia:
        if head_node.routing_points[index].hasExt or glob.TECH_LEF_DICT['Layer'][head_node.metal_layer]['metal_layer'] == 1:
            comp_num, pin = find_cell(head_node.routing_points[index], net, cell_coor_dict, pins, pin_used, prevent_duplicate = True)
            if not comp_num:
                comp_num, pin = net.number, node_number
                node_number += 1
            head_node.set_prev([comp_num, pin])
            head_node.routing_points[index].set_number([comp_num, pin])
        
        elif not head_node.routing_points[index].hasExt:
            comp_num, pin = find_cell(head_node.routing_points[index], net, cell_coor_dict, pins, pin_used, find_cell = False)
            if not comp_num:
                comp_num, pin = net.number, node_number
                node_number += 1
            head_node.set_prev([comp_num, pin])
            head_node.routing_points[index].set_number([comp_num, pin])
            
        if head_node.routing_points[last_index].hasExt or glob.TECH_LEF_DICT['Layer'][head_node.metal_layer]['metal_layer'] == 1:
            comp_num, pin = find_cell(head_node.routing_points[last_index], net, cell_coor_dict, pins, pin_used, prevent_duplicate = True)
            if not comp_num:
                comp_num, pin = net.number, node_number
                node_number += 1
            head_node.set_depth([comp_num, pin])
            head_node.routing_points[last_index].set_number([comp_num, pin])
            
        elif not head_node.routing_points[last_index].hasExt:
            comp_num, pin = find_cell(head_node.routing_points[last_index], net, cell_coor_dict, pins, pin_used, find_cell = False)
            if not comp_num:
                comp_num, pin = net.number, node_number
                node_number += 1
            head_node.set_prev([comp_num, pin])
            head_node.routing_points[last_index].set_number([comp_num, pin])
            
        head_node.routing_points[index].set_next(head_node.routing_points[last_index])
                    
    if head_node.isVia and len(net.wire_list) == 1:
        print('SPECIAL CASE - A node starts with a Via')
        # Set the depth
        comp_num, pin = find_cell(head_node.routing_points[0], net, cell_coor_dict, pins, pin_used)
        head_node.set_depth([comp_num, pin])
        head_node.routing_points[0].set_number([comp_num, pin])
        
        # Set the prev - don't need to set the number of the rp object 
        comp_num, pin = find_cell(head_node.routing_points[0], net, cell_coor_dict, pins, pin_used, False)
        head_node.set_prev([comp_num, pin])
        
    return node_number, head_node.routing_points[index]

# =============================================================================
# 
# =============================================================================
def setup_prev(cur_rp_matched, rp_matched, rp):
    rp.set_prev(cur_rp_matched.number)
    rp_matched.set_number(cur_rp_matched.number)
    
# =============================================================================
# 
# =============================================================================
def setup_depth(rp, net, cell_coor_dict, pins, node_number, pin_used, no_adjecent = False, connected_to_pin_or_cell = False):
    comp_num, pin = None, None
    if rp.isVia and rp.bottom_layer == 1 and not connected_to_pin_or_cell:
        comp_num, pin = find_cell(rp.routing_points[0], net, cell_coor_dict, pins, pin_used, prevent_duplicate = True)
        if comp_num == None and pin == None:
            comp_num, pin = net.number, node_number
            node_number += 1
            
        rp.set_depth([comp_num, pin])
        rp.routing_points[0].set_number([comp_num, pin])
        
    elif no_adjecent:
        if not rp.isVia:
            # End of the line - check whether it is connected to a PIN or a CELL
            # 1  - Check for PIN connection
            for i in range (0,2):
                comp_num, pin = find_cell(rp.routing_points[i], net, cell_coor_dict, pins, pin_used, find_cell = False)
                if comp_num:
                    rp.set_depth([comp_num, pin])
                    rp.routing_points[i].set_number([comp_num, pin])
                    break
            
            # 2 - Check for CELL connection if no PIN connection found
            if not comp_num:
                for i in range (0,2):
                    comp_num, pin = find_cell(rp.routing_points[i], net, cell_coor_dict, pins, pin_used, find_pin = False)
                    if comp_num:
                        rp.set_depth([comp_num, pin])
                        rp.routing_points[i].set_number([comp_num, pin])
                        break
        
        elif rp.isVia:
            comp_num, pin = find_cell(rp.routing_points[0], net, cell_coor_dict, pins, pin_used)
            rp.set_depth([comp_num, pin])
            rp.routing_points[0].set_number([comp_num, pin])
    
    else:
        if not rp.isVia:
            if glob.TECH_LEF_DICT['Layer'][rp.metal_layer]['metal_layer'] == 1:
                found_connection = False
                for i in range (0,2):
                    comp_num, pin = find_cell(rp.routing_points[i], net, cell_coor_dict, pins, pin_used)
                    if comp_num:
                        rp.set_depth([comp_num, pin])
                        rp.routing_points[i].set_number([comp_num, pin])
                        found_connection = True
                    else:
                        if rp.routing_points[i].number == None:
                            rp.set_depth([net.number, node_number])
                            rp.routing_points[i].set_number([net.number, node_number])
                        
                # Break out of the function
                if found_connection:   
                    return node_number
                    
            rp.set_depth([net.number, node_number])
            for i in range (0,2):
                if rp.routing_points[i].number == None:
                    rp.routing_points[i].set_number([net.number, node_number])
                    break
        
        elif rp.isVia:
            if rp.routing_points[0].hasExt:
                comp_num, pin = find_cell(rp.routing_points[0], net, cell_coor_dict, pins, pin_used)
                if comp_num:
                    rp.set_depth([comp_num, pin])
                    rp.routing_points[0].set_number([comp_num, pin])
                    return node_number
            
            rp.set_depth([net.number, node_number])      
            rp.routing_points[0].set_number([net.number, node_number])
                
        node_number += 1
        
    return node_number

def connect_rps(cur_RP, wire_RPs, via_wire = False, wire_via = False, mid_RP = None):
    """
    Desc:
        * Having a routing point found between two routing points
          break the old connection and add the new routing point as a steiner node
        * If the connection is a via to a wire:
            - The Via point will be a pivot point 
            - viaP.next contains both routing points in the wire (a Steiner Node)
        
    Parameters:
        cur_rp_routingP: instance of the routing point between the reference wire (can e from Wire or Via instance)
        wire_RPs: is one of the Wire routingPoints Instances
        via_wire: A boolean that indicates the type of connection
    """
    if len(wire_RPs.NEXT) == 0:
        return False
    
    found_connection = False
    
    for next_wire_RPs in wire_RPs.NEXT:
        if found_connection:
            return True
        
        if cur_RP.isBetween(wire_RPs,next_wire_RPs):
            found_connection = True
            wire_RPs.NEXT.remove(next_wire_RPs)
            if via_wire:
                cur_RP.set_next(mid_RP)
                mid_RP.set_next(wire_RPs)
                mid_RP.set_next(next_wire_RPs)
            elif wire_via:
                wire_RPs.set_next(mid_RP)
                mid_RP.set_next(cur_RP)
                mid_RP.set_next(next_wire_RPs)
            else:
                wire_RPs.set_next(cur_RP)
                cur_RP.set_next(next_wire_RPs)
        
        else:
            if not wire_RPs.isVia:
                if wire_RPs == cur_RP:
                    wire_RPs.set_next(cur_RP)
                    return True
            found_connection = connect_rps(cur_RP, next_wire_RPs, via_wire, wire_via, mid_RP)
    
    return found_connection