# User Guide

The calibration flow is an alternative way to get the RC information for a given
technology. It has the capability to calibrate one or more RC corners
simultenously.

Typically, for a given technology, the foundary provides these RC corners:
   * Cmax
   * Cmin
   * RCmax
   * RCmin
   * Typical  

## Instruction 
For a new PDK and corner, user needs to change the following:
1. Open ./script/user_env.tcl, and change:
	* cell_lef --> set the variable to the path to the cell lef directories 
	* tech_lef --> set the variable to the path to the tech lef directories
	* libdir, wc_lib_dir, bc_lib_dir --> set these variables to the desired PVT library paths
		- wc_lib_dir: name of the worst case Liberty files
		- bc_lib_dir: name of the best case Liberty files

	* qrcTechDir --> set the variable to the path of the qrcTech files
	* Cmin, Cmax, RCmin, RCmax, and Typical --> set these variables to the corner types used in the flow 
	* rc_type --> Type of the RC technology file, either a cap_table or qx_tech_file
	* techNode --> set to the technology node
		- Example:
			* ASAP7 PDK --> 7
			* GF14 PDK --> 14
	
2. Next, open the selected Cell LEF, and choose an inverter cell (strongly recommended) to be used in the flow
	* Open ./script/user_env.tcl, and change the following:
		- cell_name --> set to the chosen inverter cell's name
		- fp_site --> set to the FP site defined in the MACRO section in the cell LEF  
			- Example of a cell LEF: 
            ```
			    MACRO <cell_name>  
                    CLASS <class_name> ;  
                        SIZE <x_size> BY <y_size> ;  
                    SYMMETRY X Y ;  
                    SITE <core_name> ;  
            ```
			- <core_name> is the FP site name
			- <cell_name> is the inverter cell name
           
	* Open ./input/rtl/calibration.v netlist file, and do the following:
		- Replace the name of the cell used in the netlist with the new inverter cell's name
		- Replace the input and output pins of the netlist with the new inverter cell IO pins
			- Ex:  
				In Nangate45 PDK, inverter IO pins are A and ZN respectively  

## Note
If the PDK has predefined captables or any equivalent human-readable RC tech files, then the
calibration flow can be skipped. Populate the configuration file based on the
per unit R and C values from the captables and proceed to the inference flow.  
