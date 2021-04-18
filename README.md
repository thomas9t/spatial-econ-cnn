# Using Neural Networks to Predict Micro-Spatial Economic Growth
Repository of code associated with the paper "Using Neural Networks to Predict Micro-Spatial Economic Growth"

This code was run on a Linux computer using `Python 3.6–3.8, pip and venv >= 19.0, tensorflow >= 2.0, numpy >= 1.2`

# Instructions
1. Download data ([GoogleDrive](https://drive.google.com/drive/folders/1MnyQddPAzGWjZrHXlErNDfbJv9dMhr_I?usp=sharing))
2. Un-compress `tar -xvf ...` and move into `data/` directory
3. Download pretrained model weights ([GoogleDrive](https://drive.google.com/drive/folders/1n8znM2_A3Q6RLhVRxgU1HBW8FG_g6ndY?usp=sharing))
4. Un-compress `tar -xvf ..` and move into `weights/` directory
5. Run the script `run.sh`. The script will create a virtual-environment, install dependencies and run scripts for training. There are several different run configurations listed in `run.sh` which can reproduce various aspects of the paper (e.g. `RGB only` models or models with nighlights). Inspect `run.sh` for more detail.