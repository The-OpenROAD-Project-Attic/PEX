######################### USER DEFINE #######################
# Set Technology Node
set techNode 45 
set cpuUsage 16

# Verilog file name
set design calibration 

set clkp _CLKP_
set util 0.5

############### PATH - USER DEFINE ####################
set libdir ""

# QRC Corner Directory 
# Always leave the quote there to indicate that the variable exists 
set Cmin ""
set Cmax ""
set RC_max ""
set RC_min ""
set Typical "./kits/nangate45/captables/NCSU_FreePDK_45nm.capTbl" 

# rc_type is either qx_tech_file or cap_table
set rc_type "cap_table"

# Verilog and SDC file directories
set netlist "${inputDir}/rtl/${design}.v"
set sdc "${inputDir}/constraint/${design}.sdc"

#Is used by the python script - even though it is redundant
set cell_lef "./kits/nangate45/nangate45.macro.lef"
set tech_lef "./kits/nangate45/nangate45.tech.lef"

#List of all LEF library directories
set lef "${tech_lef}
${cell_lef}" 

#MCMM setup
#Edit the directories of the PVT libraries - e.g. [glob $libdir/*ss28_0.80V_*125C.lib]
set wc_lib_dir [glob ./kits/nangate45/nangate45Library_fast.lib]
set bc_lib_dir [glob ./kits/nangate45/nangate45Library_fast.lib]
set typ_lib_dir [glob ./kits/nangate45/nangate45Library_typ.lib]

# Floorplan Site
set fp_site FreePDK45_38x28_10R_NP_162NW_34O

#Cell used for the calibration
set cell_name "INV_X4"
