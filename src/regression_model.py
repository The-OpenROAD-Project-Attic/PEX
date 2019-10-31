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
      
class CONFIG_FILE(object):
    def __init__(self, filename):
        self.file = filename
        self.r = {}
        self.c = {}
        self.via_res = {}
        self.via_cap = {}
        
        self.parse_config_file()
        
    def parse_config_file(self):
        resistance = False
        CapToGnd = False
        via_res = False
        via_cap = False
        
        with open(self.file) as f:
            for line in f:
                if re.search("RESISTANCE", line):
                    resistance = True
                
                if re.match("CAPACITANCE", line):
                    CapToGnd = True
                    
                if re.search("VIA RES", line):
                    via_res = True
                
                if re.match("VIA CAP", line):
                    via_cap = True
                    
                if resistance:
                    res_data = self.process_data(line)
                    if res_data != None:
                        self.r[res_data[0]] = {'a': float(res_data[1]), 'b' : float(res_data[2])}
                        
                    if re.match('END',line, flags=re.IGNORECASE):
                        resistance = False
                    
                        
                if CapToGnd:
                    cap_data = self.process_data(line)
                    if cap_data != None:
                        self.c[cap_data[0]] = {'a' : float(cap_data[1]), 'b' : float(cap_data[2])}
                        
                    if re.match('END',line, flags=re.IGNORECASE):
                        CapToGnd = False
                
                if via_res:
                    via_res_data = self.process_data(line)
                    if via_res_data != None:
                        self.via_res[via_res_data[0]] = {'1_CUT': float(via_res_data[1])}
                        
                    if re.match('END',line, flags=re.IGNORECASE):
                        via_res = False
                    
                        
                if via_cap:
                    via_cap_data = self.process_data(line)
                    if via_cap_data != None:
                        self.via_cap[via_cap_data[0]] = {'1_CUT' : float(via_cap_data[1])}
                        
                    if re.match('END',line, flags=re.IGNORECASE):
                        via_cap = False
    
    def process_data(self, line):
        data = line.split()
        if not data[0].isdigit():
            return None
        
        return data
    
    def get_wire_parasitic(self, metal_layer, length, r = False, c = False):
        assert r or c, 'Wire - Need to set one or both flag(s) to true!'
        
        if r:
            res = self.r[str(metal_layer)]['a'] * float(length) + self.r[str(metal_layer)]['b']
            if res <= 0:
                res = self.r[str(metal_layer)]['a'] * float(length)
            
        if c:
            cap = self.c[str(metal_layer)]['a'] * float(length) + self.r[str(metal_layer)]['b']
            if cap <= 0:
                cap = self.c[str(metal_layer)]['a'] * float(length)
                
        if r and not c:
            return res
        elif c and not r:
            return cap
        else:
            return res, cap
        
    def get_via_parasitic(self, total_cut, bottom_layer, via_res = False, via_cap = False):
        assert via_res or via_cap, 'Via - Need to set one or both flag(s) to true!'
        
        if via_res and not via_cap:
            return self.via_res[str(bottom_layer)]['{}_CUT'.format(total_cut)]   
        
        elif not via_res and via_cap:
            return self.via_cap[str(bottom_layer)]['{}_CUT'.format(total_cut)]  
        
        else:
            return self.via_res[str(bottom_layer)]['{}_CUT'.format(total_cut)], self.via_cap[str(bottom_layer)]['{}_CUT'.format(total_cut)]