# Using Neural Networks to Predict Micro-Spatial Economic Growth
Repository of code associated with the paper "Using Neural Networks to Predict Micro-Spatial Economic Growth"

This code was run on a Linux computer using `Python 3.6–3.8, pip and venv >= 19.0, tensorflow >= 2.0, numpy >= 1.2`

# Overview

Our code pipeline is generally divided into three phases: (1) raw data extraction and processing, (2) model training and validation, and (3) predictions and analysis. The output of phase (1) is a set of `.tfrecord` files containing the train, validation, and test data. The output of phase (2) are trained CNNs. The output of phase (3) are predictions of our outcome variables.

Phases (1) and (2) will be of interest for those interested in extending our basic approach to other sources of imagery and/or outcome variables as well as those interested in understanding our approach in (possibly excruciating) detail. Phase (3) will be of interest to those who want to use the predictions generated by us for another application. Each of these phases are described in more detail below. Those interested primarily in using our predicted values are encouraged to skip to the section entitled "Phase (3) - Predictions" below.

## Phase (1) - Data Extraction and Processing

In this phase, we extract the raw imagery and census data used to train our models. This phase is divided into the following steps:

**General order of operations**: `extract_gee_data.py -> download_data.py -> prep_data_levels.py -> prep_data_diffs.py -> shard_data.py`

1. **Create raw data export from GoogleEarthEngine**: This is performed by the file `scripts/extract_gee_data.py`. The file will define the extract and the resulting data will be written (as many small TFRecord files) to a folder in Google Drive.
2. **Download Data**: We next download the data produced by step (1) and prepare it for training. The script `download_data.py` downloads the raw data from google drive (using `google_drive_utils.py`), discard images that do not meet our urbanization threshold and convert them into a large `HDF5` file which is easier to store locally than many small `tfrecord files`. We also assign each image an identifier in this stage that can be used to match it with its label(s).
3. **Prepare Training Data**: Next, we process the HDF5 file produced in the previous stage into a form suitable for use in tensorflow. In this phase, we also match each image with its ground truth label (e.g. the outcome to be predicted), partition the data into train, validation, and test sets, and strip off the overlap that GoogleEarth engine adds (e.g. the KernelSize parameter in GEE). This is performed in `prep_data_levels.py` and `prep_data_diffs.py` for levels and diffs models repsectively. Finally, to improve processing speed by TensorFlow, we split the large TFrecord files producted by these scripts into small shards that can be loaded more efficiently. This is performed in `shard_data.py`.

The output of this phase (before sharding) is made available here [GoogleDrive](https://drive.google.com/drive/folders/1MnyQddPAzGWjZrHXlErNDfbJv9dMhr_I?usp=sharing). Users who wish to use our existing data, but experiment with new model architectures may download this data, and uncompress (`tar -xvf ...`) it to the `data` sub-folder of this repository.

## Phase (2) - Model Training and Validation

This phase defines model architectures, trains models, and performs hyperparameter tuning. Model architecture and training code is contained in `train_level_model.py` and `train_diff_model.py`. We have provided the `run.sh` script which includes detailed descriptions of parameters and command line arguments used by the training scripts.

**General order of operations**: `train_level_model.py -> train_diff_model.py`

Trained models are available here: [GoogleDrive](https://drive.google.com/drive/folders/1n8znM2_A3Q6RLhVRxgU1HBW8FG_g6ndY?usp=sharing). These trained weights may be used for transfer learning (e.g. using our weights to generate features from different imagery). Models are named according to the following conventions:

`block_[small,large]_national_[level,diff]_base[_feature]_[inc,pop][_all]`, where `small/large` indicates the imagery size (e.g. the `40x40` vs `80x80` imagery), `level/diff` indicates models for levels vs. diffs, the presence `_feature` indicates models trained with initial conditions (e.g. auxiliary features), `inc/pop` indicates the outcome variable, and the presence of `_all` indicates models trained on the entire set of images in 2000/2010 (e.g. used to produce the out-of-period results in Table 2).

# Instructions
1. Download data 
2. Move into `data/` directory and un-compress `tar -xvf ...`
3. Download pretrained model weights ([GoogleDrive](https://drive.google.com/drive/folders/1n8znM2_A3Q6RLhVRxgU1HBW8FG_g6ndY?usp=sharing))
4. Move into `weights/` directory and un-compress `tar -xvf ..`
5. Run the script `run.sh`. The script will create a virtual-environment, install dependencies and run scripts for training. There are several different run configurations listed in `run.sh` which can reproduce various aspects of the paper (e.g. `RGB only` models or models with nighlights). Inspect `run.sh` for more detail.


## Phase (3) - Predictions

Predictions and geographic shapefiles at the level of our large images can be accessed [here](https://drive.google.com/drive/folders/1JZ_AnYVqfM1AxX5Gzfin0Lw0s_20ilB9?usp=sharing). Also shared is a version which has been geographically crosswalked to 2010 Census Blocks. The unique identifier for images is img_id, and for Census Blocks is gisjoin (as defined by NHGIS [here](https://www.nhgis.org/geographic-crosswalks)). Within each file are predictions of income and population which are generated in our out of sample model (as described in section 3.4). The variable inc_0_feature for example refers to the predicted log income in 2000, using the model including initial conditions. The variable dpop_9_19, conversely is our prediction of the log change in population from 2009 to 2019, in the model excluding initial conditions. Note that difference predictions are not crosswalked to the Block version of these data.
