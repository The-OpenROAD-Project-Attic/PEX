# OpenROAD-PEX
Regression model-based on-chip parasitic extraction (PEX) at the post-route stage

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
	* config_file_{corner_name_min}.txt
	* config_file_{corner_name_max}.txt

The training data generation is a one-time step which involves running a
calibration script and a training script to train the data. The output format can
be referred to the ./doc/config_file.txt  

## Getting Started
### Prerequisite
- python 3.6
- Cadence Innovus 17.1 or newer
- pip 18.1
- python3-venv

Additionally, please refer to *requirements.txt* file in this repository. 
The packages in requirements.txt will be installed in a virtual environment during build.

### Install on a bare-metal machine

#### Clone repo and submodules
`git clone --recursive https://github.com/GeraldoPradipta/OpenROAD-PEX`

#### Install
```
cd OpenROAD-PEX 
make clean
source install.sh
```

## Usage
**Training flow**
- This flow  must be run only once for a new PDK and corner
- It involves running a tcl script that generates the required data to train
	the regression model. 
- How to run:
	* Point to the paths of the Tech LEF, Cell LEF, qrcTech files, PVT libraries, and
		the user-defined environment file
	* In the terminal:
 `make all`

