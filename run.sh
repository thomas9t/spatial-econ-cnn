# download data and pretrained weights
# data: https://drive.google.com/drive/folders/1MnyQddPAzGWjZrHXlErNDfbJv9dMhr_I?usp=sharing
# weights: https://drive.google.com/drive/folders/1n8znM2_A3Q6RLhVRxgU1HBW8FG_g6ndY?usp=sharing
# put data files into "data/"
# put weights files into "weights/"

# require Python 3.6–3.8, pip and venv >= 19.0, tensorflow >= 2.0, numpy >= 1.2
python3 -m venv --system-site-packages ./scnn
source ./scnn/bin/activate
pip install --upgrade pip
pip install --upgrade tensorflow numpy pytables pydrive pandas tqdm


# train level model
# mw data only have RGB channels for both high and low resolution
# small images don't have nightlight channel
# True: with initial conditions, False: without initial conditions
# Arguments:
# construct: Level of analysis. May be: BG or block
# region: Region of analysis. May be: 'national' or 'mw' (for midwest)
# model_type: What channels should be used. May be: 'base', 'RGB' (for RGB only), 'nl' (for base + nighlights)
# size: What size of images should be used. May be:'large' (for 2.4 km^2) 'small' (for 1.2 km^2)
# datatype: What outcome variable should be predicted. May be: 'inc' or 'pop' or 'inc_pop'
# resolution: What data resolution should be used. May be: 'high' or 'low'
# with_feature: Should initial conditions be included. May be: True, False
# epochs: How many epochs should be used for training? May be: positive integer
# data_dir: Where is the data. May be: string path
# out_dir: Where should output be written? May be: string path
# all_images: Whether use all images for training. May be: True, False. 
# Note: When all_images == False, model will be trained on training set and validated on validation set for hyperparameter tuning then test on test set
# when all_images == True, model will be trained on training set + validation set and validated on test set, so the results of validation set and 
# test set in tensorboard will be the same.

python scripts/train_level_model.py block national base large inc low True 200 data outputs False
# python scripts/train_level_model.py block national base large pop low True 200 data outputs False
# python scripts/train_level_model.py block national RGB large inc low True 200 data outputs False
# python scripts/train_level_model.py block national RGB large pop low True 200 data outputs False
# python scripts/train_level_model.py block national nl large inc low True 200 data outputs False
# python scripts/train_level_model.py block national nl large pop low True 200 data outputs False
# python scripts/train_level_model.py block national base small inc low True 200 data outputs False
# python scripts/train_level_model.py block national base small pop low True 200 data outputs False
# python scripts/train_level_model.py block national RGB small inc low True 200 data outputs False
# python scripts/train_level_model.py block national RGB small pop low True 200 data outputs False
# python scripts/train_level_model.py block mw RGB small inc low True 200 data outputs False
# python scripts/train_level_model.py block mw RGB small pop low True 200 data outputs False
# python scripts/train_level_model.py block mw RGB small inc high True 200 data outputs False
# python scripts/train_level_model.py block mw RGB small pop high True 200 data outputs False
# python scripts/train_level_model.py block national base large inc low False 200 data outputs False
# python scripts/train_level_model.py block national base large pop low False 200 data outputs False
# python scripts/train_level_model.py block national RGB large inc low False 200 data outputs False
# python scripts/train_level_model.py block national RGB large pop low False 200 data outputs False
# python scripts/train_level_model.py block national nl large inc low False 200 data outputs False
# python scripts/train_level_model.py block national nl large pop low False 200 data outputs False
# python scripts/train_level_model.py block national base small inc low False 200 data outputs False
# python scripts/train_level_model.py block national base small pop low False 200 data outputs False
# python scripts/train_level_model.py block national RGB small inc low False 200 data outputs False
# python scripts/train_level_model.py block national RGB small pop low False 200 data outputs False
# python scripts/train_level_model.py block mw RGB small inc low False 200 data outputs False
# python scripts/train_level_model.py block mw RGB small pop low False 200 data outputs False
# python scripts/train_level_model.py block mw RGB small inc high False 200 data outputs False
# python scripts/train_level_model.py block mw RGB small pop high False 200 data outputs False

# train difference model
# Arguments:
# construct: Level of analysis. May be: BG or block
# region: Region of analysis. May be: 'national' or 'mw' (for midwest)
# model_type: What channels should be used. May be: 'base', 'RGB' (for RGB only), 'nl' (for base + nighlights)
# size: What size of images should be used. May be:'large' (for 2.4 km^2) 'small' (for 1.2 km^2)
# datatype: What outcome variable should be predicted. May be: 'inc' or 'pop' or 'inc_pop'
# resolution: What data resolution should be used. May be: 'high' or 'low'
# with_feature: Should initial conditions be included. May be: True, False
# epochs: How many epochs should be used for training? May be: positive integer
# data_dir: Where is the data. May be: string path
# out_dir: Where should output be written? May be: string path
# weight_dir: Where are weights (produced by training levels models)? May be: string path
# Levels models hyperparameters (each is a separate argument):
    # level_lr
    # level_l2
    # level_bs
    # level_ds
    # level_nf
    # level_dr
    # level_epochs
python scripts/train_diff_model.py block national base large inc low True 100 <dirname> outputs weights 1e-4 1e-8 16 200 32 0.5 200 False
# python scripts/train_diff_model.py block national base large pop low True 100 <dirname> outputs weights 1e-4 1e-7 16 50 32 0.5 200 False
# python scripts/train_diff_model.py block national base small inc low True 100 <dirname> outputs weights 1e-4 1e-8 16 200 32 0.5 200 False
# python scripts/train_diff_model.py block national base small pop low True 100 <dirname> outputs weights 1e-4 1e-7 16 50 32 0.5 200 False
