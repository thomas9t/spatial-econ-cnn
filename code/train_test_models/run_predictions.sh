# download data and pretrained weights
# data: https://drive.google.com/drive/folders/1MnyQddPAzGWjZrHXlErNDfbJv9dMhr_I?usp=sharing
# weights: https://drive.google.com/drive/folders/1n8znM2_A3Q6RLhVRxgU1HBW8FG_g6ndY?usp=sharing
# unzip and put data files into "data/"
# put weights files into "weights/"

# make predictions for levels

DATA=${CNN_PROJECT_ROOT}/data
OUTPUTS=${CNN_PROJECT_ROOT}/data/predictions/level
WEIGHTS=${CNN_PROJECT_ROOT}/weights

# base
python make_predictions_level.py block national base large inc low True 200 $DATA $OUTPUTS $WEIGHTS 1e-4 1e-6 16 50 32 0.5 False
python make_predictions_level.py block national base large inc low False 200 $DATA $OUTPUTS $WEIGHTS 1e-4 1e-8 16 50 32 0.5 False
python make_predictions_level.py block national base large pop low True 200 $DATA $OUTPUTS $WEIGHTS 1e-4 1e-7 16 100 32 0.5 False
python make_predictions_level.py block national base large pop low False 200 $DATA $OUTPUTS $WEIGHTS 1e-4 1e-7 16 50 32 0.5 False
python make_predictions_level.py block national base small inc low True 200 $DATA $OUTPUTS $WEIGHTS 1e-4 1e-8 16 100 32 0.5 False
python make_predictions_level.py block national base small inc low False 200 $DATA $OUTPUTS $WEIGHTS 1e-4 1e-8 16 100 32 0.5 False
python make_predictions_level.py block national base small pop low True 200 $DATA $OUTPUTS $WEIGHTS 1e-4 1e-7 16 50 32 0.5 False
python make_predictions_level.py block national base small pop low False 200 $DATA $OUTPUTS $WEIGHTS 1e-4 1e-7 16 50 32 0.5 False
 
# rgb
python make_predictions_level.py block national RGB large inc low True 200 $DATA $OUTPUTS $WEIGHTS 1e-4 1e-6 16 50 32 0.5 False
python make_predictions_level.py block national RGB large inc low False 200 $DATA $OUTPUTS $WEIGHTS 1e-4 1e-8 16 50 32 0.5 False
python make_predictions_level.py block national RGB large pop low True 200 $DATA $OUTPUTS $WEIGHTS 1e-4 1e-7 16 100 32 0.5 False
python make_predictions_level.py block national RGB large pop low False 200 $DATA $OUTPUTS $WEIGHTS 1e-4 1e-7 16 50 32 0.5 False

# nl
python make_predictions_level.py block national nl large inc low True 200 $DATA $OUTPUTS $WEIGHTS 1e-4 1e-6 16 50 32 0.5 False
python make_predictions_level.py block national nl large inc low False 200 $DATA $OUTPUTS $WEIGHTS 1e-4 1e-8 16 100 32 0.5 False
python make_predictions_level.py block national nl large pop low True 200 $DATA $OUTPUTS $WEIGHTS 1e-4 1e-6 16 100 32 0.5 False
python make_predictions_level.py block national nl large pop low False 200 $DATA $OUTPUTS $WEIGHTS 1e-4 1e-7 16 50 32 0.5 False

# mw
python make_predictions_level.py block mw RGB small inc low False 200 $DATA $OUTPUTS $WEIGHTS 1e-4 1e-7 16 200 32 0.5 False
python make_predictions_level.py block mw RGB small inc high False 200 $DATA $OUTPUTS $WEIGHTS 1e-4 1e-7 16 200 32 0.5 False
python make_predictions_level.py block mw RGB small pop low False 200 $DATA $OUTPUTS $WEIGHTS 1e-4 1e-7 16 200 32 0.5 False
python make_predictions_level.py block mw RGB small pop high False 200 $DATA $OUTPUTS $WEIGHTS 1e-4 1e-7 16 200 32 0.5 False

python make_predictions_level.py block mw RGB small inc low True 200 $DATA $OUTPUTS $WEIGHTS 1e-4 1e-7 16 200 32 0.5 False
python make_predictions_level.py block mw RGB small inc high True 200 $DATA $OUTPUTS $WEIGHTS 1e-4 1e-7 16 200 32 0.5 False
python make_predictions_level.py block mw RGB small pop low True 200 $DATA $OUTPUTS $WEIGHTS 1e-4 1e-7 16 200 32 0.5 False
python make_predictions_level.py block mw RGB small pop high True 200 $DATA $OUTPUTS $WEIGHTS 1e-4 1e-7 16 200 32 0.5 False

# inc/pop model
python make_predictions_level.py block national base large inc_pop low True 200 $DATA $OUTPUTS $WEIGHTS 1e-5 1e-7 16 200 32 0.5 False
python make_predictions_level.py block national base large inc_pop low False 200 $DATA $OUTPUTS $WEIGHTS 1e-4 1e-8 16 200 32 0.5 False
python make_predictions_level.py block national base small inc_pop low True 200 $DATA $OUTPUTS $WEIGHTS 1e-5 1e-6 16 200 32 0.5 False
python make_predictions_level.py block national base small inc_pop low False 200 $DATA $OUTPUTS $WEIGHTS 1e-4 1e-8 16 200 32 0.5 False

# make predictions for diffs

OUTPUTS=${CNN_PROJECT_ROOT}/data/predictions/diff
mkdir -p $OUTPUTS

# base
python make_predictions_diff.py block national base large inc low True 100 $DATA $OUTPUTS $WEIGHTS 1e-5 1e-8 16 50 32 0.5 False
python make_predictions_diff.py block national base large inc low False 100 $DATA $OUTPUTS $WEIGHTS 1e-5 1e-7 16 200 32 0.5 False
python make_predictions_diff.py block national base large pop low True 100 $DATA $OUTPUTS $WEIGHTS 1e-5 1e-8 16 50 32 0.5 False
python make_predictions_diff.py block national base large pop low False 100 $DATA $OUTPUTS $WEIGHTS 1e-4 1e-6 16 50 32 0.5 False
python make_predictions_diff.py block national base small inc low True 100 $DATA $OUTPUTS $WEIGHTS 1e-5 1e-8 16 50 32 0.5 False
python make_predictions_diff.py block national base small inc low False 100 $DATA $OUTPUTS $WEIGHTS 1e-5 1e-8 16 50 32 0.5 False
python make_predictions_diff.py block national base small pop low True 100 $DATA $OUTPUTS $WEIGHTS 1e-5 1e-8 16 50 32 0.5 False
python make_predictions_diff.py block national base small pop low False 100 $DATA $OUTPUTS $WEIGHTS 1e-4 1e-7 16 50 32 0.5 False
 
# rgb
python make_predictions_diff.py block national RGB large inc low True 100 $DATA $OUTPUTS $WEIGHTS 1e-4 1e-8 16 50 32 0.5 False
python make_predictions_diff.py block national RGB large inc low False 100 $DATA $OUTPUTS $WEIGHTS 1e-5 1e-8 16 50 32 0.5 False
python make_predictions_diff.py block national RGB large pop low True 100 $DATA $OUTPUTS $WEIGHTS 1e-4 1e-8 16 100 32 0.5 False
python make_predictions_diff.py block national RGB large pop low False 100 $DATA $OUTPUTS $WEIGHTS 1e-5 1e-8 16 50 32 0.5 False

# mw
python make_predictions_diff.py block mw RGB small inc low False 100 $DATA $OUTPUTS $WEIGHTS 1e-5 1e-8 16 200 32 0.5 False
python make_predictions_diff.py block mw RGB small inc high False 100 $DATA $OUTPUTS $WEIGHTS 1e-5 1e-8 16 200 32 0.5 False
python make_predictions_diff.py block mw RGB small pop low False 100 $DATA $OUTPUTS $WEIGHTS 1e-5 1e-6 16 200 32 0.5 False
python make_predictions_diff.py block mw RGB small pop high False 100 $DATA $OUTPUTS $WEIGHTS 1e-5 1e-8 16 200 32 0.5 False

python make_predictions_diff.py block mw RGB small inc low True 100 $DATA $OUTPUTS $WEIGHTS 1e-5 1e-8 16 200 32 0.5 False
python make_predictions_diff.py block mw RGB small inc high True 100 $DATA $OUTPUTS $WEIGHTS 1e-5 1e-8 16 200 32 0.5 False
python make_predictions_diff.py block mw RGB small pop low True 100 $DATA $OUTPUTS $WEIGHTS 1e-5 1e-8 16 200 32 0.5 False
python make_predictions_diff.py block mw RGB small pop high True 100 $DATA $OUTPUTS $WEIGHTS 1e-5 1e-8 16 200 32 0.5 False

# nl
python make_predictions_diff.py block national nl large inc low True 100 $DATA $OUTPUTS $WEIGHTS 1e-4 1e-8 16 50 32 0.5 False
python make_predictions_diff.py block national nl large inc low False 100 $DATA $OUTPUTS $WEIGHTS 1e-5 1e-8 16 50 32 0.5 False
python make_predictions_diff.py block national nl large pop low True 100 $DATA $OUTPUTS $WEIGHTS 1e-4 1e-8 16 50 32 0.5 False
python make_predictions_diff.py block national nl large pop low False 100 $DATA $OUTPUTS $WEIGHTS 1e-5 1e-7 16 100 32 0.5 False

# inc/pop

python make_predictions_diff.py block national base large inc_pop low True 100 $DATA $OUTPUTS $WEIGHTS 1e-4 1e-8 16 200 32 0.5 False
python make_predictions_diff.py block national base large inc_pop low False 100 $DATA $OUTPUTS $WEIGHTS 1e-4 1e-7 16 200 32 0.5 False
python make_predictions_diff.py block national base small inc_pop low True 100 $DATA $OUTPUTS $WEIGHTS 1e-4 1e-8 16 200 32 0.5 False
python make_predictions_diff.py block national base small inc_pop low False 100 $DATA $$OUTPUTS $WEIGHTS 1e-4 1e-6 16 200 32 0.5 False


# "out of period" models

OUTPUTS=${CNN_PROJECT_ROOT}/data/predictions/out_of_period_model

python scripts/make_predictions_level.py block national base large inc low True 200 $DATA $OUTPUTS $WEIGHTS 1e-4 1e-8 16 200 32 0.5 True
python scripts/make_predictions_level.py block national base large inc low False 200 $DATA $OUTPUTS $WEIGHTS 1e-5 1e-8 16 200 32 0.5 True
python scripts/make_predictions_level.py block national base large pop low True 200 $DATA $OUTPUTS $WEIGHTS 1e-4 1e-6 16 200 32 0.5 True
python scripts/make_predictions_level.py block national base large pop low False 200 $DATA $OUTPUTS $WEIGHTS 1e-4 1e-7 16 200 32 0.5 True
python scripts/make_predictions_level.py block national base small inc low True 200 $DATA $OUTPUTS $WEIGHTS 1e-4 1e-8 16 200 32 0.5 True
python scripts/make_predictions_level.py block national base small inc low False 200 $DATA $OUTPUTS $WEIGHTS 1e-5 1e-8 16 200 32 0.5 True
python scripts/make_predictions_level.py block national base small pop low True 200 $DATA $OUTPUTS $WEIGHTS 1e-4 1e-8 16 200 32 0.5 True
python scripts/make_predictions_level.py block national base small pop low False 200 $DATA $OUTPUTS $WEIGHTS 1e-4 1e-6 16 200 32 0.5 True

python scripts/make_predictions_diff.py block national base large inc low True 100 $DATA $OUTPUTS $WEIGHTS 1e-5 1e-8 16 200 32 0.5 True
python scripts/make_predictions_diff.py block national base large inc low False 100 $DATA $OUTPUTS $WEIGHTS 1e-5 1e-8 16 200 32 0.5 True
python scripts/make_predictions_diff.py block national base large pop low True 100 $DATA $OUTPUTS $WEIGHTS 1e-5 1e-8 16 200 32 0.5 True
python scripts/make_predictions_diff.py block national base large pop low False 100 $DATA $OUTPUTS $WEIGHTS 1e-5 1e-8 16 200 32 0.5 True
python scripts/make_predictions_diff.py block national base small inc low True 100 $DATA $OUTPUTS $WEIGHTS 1e-5 1e-8 16 200 32 0.5 True
python scripts/make_predictions_diff.py block national base small inc low False 100 $DATA $OUTPUTS $WEIGHTS 1e-5 1e-8 16 200 32 0.5 True
python scripts/make_predictions_diff.py block national base small pop low True 100 $DATA $OUTPUTS $WEIGHTS 1e-5 1e-6 16 200 32 0.5 True
python scripts/make_predictions_diff.py block national base small pop low False 100 $DATA $OUTPUTS $WEIGHTS 1e-4 1e-8 16 200 32 0.5 True