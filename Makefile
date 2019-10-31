SHELL:=/bin/bash
PC = python3
CI = innovus
COMMAND = $(shell source install.sh)
.PHONY: work clean

export DEF_DIR = ./example/gcd_nangate_triton.def# example/aes_nangate_triton.def
export TECH_LEF_DIR = ./kits/nangate45/nangate45.tech.lef
export MARCRO_LEF_DIR = ./kits/nangate45/nangate45.macro.lef
export CONFIG_FILE_DIR = ./kits/nangate45/NAND45_config_file.txt
export LIB_DIR = ./kits/nangate45/nangate45Library_fast.lib 


all: clean
	@make inference	

inference: output virtual
	@python3 ./src/SPEF_writer.py

clean: 
	@rm -rf innovus*
	@rm -rf work/
	@rm -rf extLogDir/ rc_model.bin src/__pycache__/
	@rm -rf ./*.sw* ./*/*.sw* *.ece* input/constraint/*.sdc

work:
	@mkdir -p work

output:
	@mkdir -p output

build:
	 @./install.sh

calibration: clean virtual
	@mkdir -p ./work
	@mkdir -p ./output
	@$(CI) -init ./script/run_script.tcl
	@$(PC) ./src/RegressionModel_Res.py
	@$(PC) ./src/RegressionModel_Cap.py
	@$(PC) ./src/cap_table_parser.py
	@rm -rf innovus*

virtual:
	@echo "Virtual Activated"
	@if [ ! -d "./PEX" ]; then make build; else source PEX/bin/activate; fi
