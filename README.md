# PEX
[![Standard](https://img.shields.io/badge/python-3.6-blue)](https://commons.wikimedia.org/wiki/File:Blue_Python_3.6_Shield_Badge.svg)
[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

Regression model-based on-chip parasitic extraction (PEX) at the post-route
stage. The tool comprises of two flows:

+ Calibration Flow
+ Inference Flow

## Calibration Flow:
- Inputs:
	* Technology LEF
	* Cell LEF
	* PVT Libraries
	* qrcTech files
	* User-defined environment file
- Training data generation using Cadence Innovus
- Regression model training 
- Output files:
	* config_file_{corner_name}.txt

The training data generation involves running a
calibration script and a script to train the data. The instruction on how
to run the calibration flow can be found
[here](docs/calibration_instructions.md). The output format can
be referred [here](./docs/RegressionModelFormat.txt). 

## Inference Flow:
The tool uses the constructed regression models to estimate parasitics on a given routed 
design.

- Inputs:
	* Technology LEF
	* Cell LEF
	* PVT Libraries
    * User-defined environment file
    * **routed DEF**
- Output files:
	* {design_name}.spef 

The detailed information about the flow can be found
[here](docs/inference_instructions.md).

## Getting Started
### Prerequisite
- python 3.6
- Cadence Innovus 17.1 or newer
- pip 18.1
- python3-venv

Additionally, please refer to *requirements.txt* file in this repository. 
The packages in requirements.txt will be installed in a virtual environment during build.

### 3-party Module
- Tcl v8.4.20

### Clone repo and submodules
`git clone --recursive https://github.com/The-OpenROAD-Project/PEX.git`

### Install
```
cd PEX 
make clean
make build
```

## Usage
**Training flow**
- This flow  must be run only once for a new PDK and corner
- It involves running a tcl script that generates the required data to train
	the regression model. 
- How to run:
	* Point to the paths of the Tech LEF, Cell LEF, qrcTech files, Liberty file, and
		the user-defined environment file
	* In the terminal:
 `make calibration`

**Inference Flow**
- How to run:
    * Point to the paths of:
        * Tech LEF
        * Cell LEF
        * Liberty file
        * Design layout (DEF)
        * Configuration file (contains regression model data)
    * In the terminal:
 `make inference`

## License
The PEX repository is licensed under the BSD 3-Clause License. The flow is built
and tested using a third party PDK, the Nangate45 PDK, that is licensed under a
different license. The license can be found below:

+ [PEX](./LICENSE): Regression model-based on-chip parasitic extraction (PEX)
+ [NanGate 45nm Library](./kits/nangate45/LICENSE): open-source standard-cell library for testing and exploring EDA flows
