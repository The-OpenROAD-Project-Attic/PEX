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

import numpy as np
import tensorflow as tf
from datetime import datetime
import os

my_env = os.environ.copy()

dataset=np.genfromtxt(my_env["RUN_DIR"]+"/CC_Cap_TrainingSet.txt", delimiter=" ", skip_header=1) #reads file

n_sample_cap = 100
epochs = 1000

layer_max = 7

CC_storage = []

def run_regression(layer):
    start_point = n_sample_cap*layer - 100
    end_point = n_sample_cap*layer
    
    data_cap = dataset[start_point:end_point]
    np.random.shuffle(data_cap)
    data_cap[:,2] = 100*data_cap[:,2]
    data_cap[:,1] = 10*data_cap[:,1]
    
    X1 = tf.placeholder(tf.float32, name="X1")
    X2 = tf.placeholder(tf.float32, name="X2")
    Y = tf.placeholder(tf.float32, name="Y")
    
    W1 = tf.Variable(0.0, name="W1")
    W2 = tf.Variable(0.0, name="W2")
    W3 = tf.Variable(0.0, name="W3")
    b = tf.Variable(0.0, name="bias")
    
    Y_predicted = X1*W1 + (1/X2)*W2 + X1/X2*W3 + b
        
    cost = tf.reduce_sum(tf.pow(Y_predicted-Y, 2))/(2*n_sample_cap)
        
    optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.3).minimize(cost)
    
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        for i in range(epochs): 
            for x1, x2, y in zip(data_cap[:,0],data_cap[:,1],data_cap[:,2]):  
                _,loss_v = sess.run([optimizer,cost], feed_dict={X1: x1, X2: x2, Y: y})
            w1_value, w2_value, w3_value, b_value = sess.run([W1, W2, W3, b])
            print(str(w1_value) + '  ' + str(w2_value) + '  ' + str(w3_value) + '  ' +  str(b_value)+ '  ' +  str(loss_v))
#            cost_history=np.append(cost_history,loss_v)
            
    CC_storage.append([layer_max-layer, w1_value, w2_value, w3_value, b_value])
    
    
def write_toFile(arr, filename):
    with open(my_env["RUN_DIR"]+ '/output/' + filename + '.txt','a') as out:
        out.write('\nCOUPLING CAPACITANCE\n')
        out.write('Layer W1 W2 W3 b\n')
        
        for ele in arr:
            out.write(str(ele[0]) + ' ' + str(ele[1]) + ' ' + str(ele[2]) + ' ' + str(ele[3]) + ' ' + str(ele[4]) +'\n')
        out.write('END\n')
        
def write_viaToFile(filename):
    with open(my_env["RUN_DIR"]+ '/work/' + filename + '.txt','a') as out:
        out.write('\nVIA\n')
        out.write('Via_type Res\n')
        
        out.write('CDS_NORMAL 18\n')
        out.write('NR_VIA 18\n')
        out.write('CDS_BAR 9\n')
        out.write('END\n')
        
def main():
    startTime = datetime.now()
    
    filename = 'exampleData'
    last_layer = 6
    
    for metal_layer in range (1,last_layer+1):
        run_regression(metal_layer)
        
    write_toFile(CC_storage, filename)
    write_viaToFile(filename)
    print("Time taken:", datetime.now() - startTime)
    
main()
