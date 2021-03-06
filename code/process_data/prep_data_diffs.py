import os 
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
import tensorflow as tf
physical_devices = tf.config.experimental.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], True)
import numpy as np
import pandas as pd
import sys
from sklearn import preprocessing
import tables

from prep_data_levels import FEATURES

ROOT = os.environ.get("CNN_PROJECT_ROOT", "../")

# popshare = 0.85
# urb = 0.1
size = sys.argv[1] # small or large
construct = sys.argv[2] # BG or block
region = sys.argv[3] # national or mw

if size == "large":
    if region == "mw":
        sys.exit('mw data only has small images')
    elif region == "national":
        TOP_CODES = [2500, 2500, 2500, 10000, 10000, 10000, 10000, 63]
    else:
        sys.exit('invalid region')
elif size == "small":
    if region == "mw":
        TOP_CODES = [2500, 2500, 2500, 0.5, 0.5, 0.5]
    elif region == "national":
        TOP_CODES = [2500, 2500, 2500, 10000, 10000, 10000, 10000]
    else:
        sys.exit('invalid region')


def main():
    scaler = np.array(TOP_CODES).astype(np.float32).reshape(1,-1) 
    if region == "mw":
        dataset = tables.open_file(f"{ROOT}/temp/high_resolution_small_images_raw.h5")
    elif region == "national":
        dataset = tables.open_file(f"{ROOT}/temp/{size}_images_all_years_raw.h5")
    label = pd.read_csv(f'{ROOT}/temp/{construct}cw_labelled_imgs_{region}_{size}.csv')
    label = label[~label['log_inc_10'].isnull()]
    label = label[~label['log_inc_00'].isnull()]
    label = label[~label['log_inc_15'].isnull()]
    if construct == 'BG':
        label = label[~label['log_pop_15'].isnull()]
    label = label[~label['log_pop_00'].isnull()]
    label = label[~label['log_pop_10'].isnull()]
    label = label[~label['popshare_00'].isnull()]
    label = label[~label['urban'].isnull()]
    label = label[label['sample']==1]
    
    features = label.loc[:,FEATURES]
    min_max_scaler = preprocessing.MinMaxScaler()
    min_max_scaler.fit(features)
    scaled_features = pd.DataFrame(min_max_scaler.transform(features), columns=features.columns)
    
    categorical_values = pd.get_dummies(label.loc[:,'county':'state'], columns=['county','state'])
    print("Prep training dataset for {} {} {} images".format(construct, region, size))
    write_example(dataset, label, 'train', scaler, scaled_features, categorical_values)
    write_example(dataset, label, 'validation', scaler, scaled_features, categorical_values)
    write_example(dataset, label, 'test', scaler, scaled_features, categorical_values)
    print ("Complete!")
    
def write_example(dataset, label, subset, scaler, scaled_features, categorical_values):
    print("Start creating {} diff set...".format(subset))
    with tf.io.TFRecordWriter(f'{ROOT}/temp/{subset}_{construct}_{size}_diff_national.tfrecords') as writer:
        nr = 0
        ne = 0
        for node in dataset.root:
            for row in node.iterrows():
                if (nr % 10000) == 0:
                    print ("On row: {}".format(nr))
                nr += 1
                img_id = np.array(row["img_id"], dtype=np.int)
                check_id = (label['img_id'] == img_id)
                if check_id.any() and (label[check_id]['subset']==subset).bool():
                    if region == "national":
                        example = get_serialize(row, label, scaler, scaled_features, check_id, img_id, categorical_values)
                        writer.write(example)
                        ne += 1
                    elif region == "mw":
                        example = get_serialize(row, label, scaler, scaled_features, check_id, img_id)
                        writer.write(example)
                        ne += 1
                    else:
                        sys.exit('invalid config')
        print ("Finish! Adding {} samples in {} set".format(ne, subset))

        
def _bytes_feature(value):
    """Returns a bytes_list from a string / byte."""
    if isinstance(value, type(tf.constant(0))):
        value = value.numpy() # BytesList won't unpack a string from an EagerTensor.
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))

def _float_feature(value):
    """Returns a float_list from a float / double."""
    return tf.train.Feature(float_list=tf.train.FloatList(value=[value]))

def _int64_feature(value):
    """Returns an int64_list from a bool / enum / int / uint."""
    return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))

def serialize_example(image0, image1, img_id, inc0, inc1, pop0, pop1, lat, lng, urban_share, pop_share, features, cats):
    feature = {
        'image0': _bytes_feature(image0),
        'image1': _bytes_feature(image1),
        'img_id':_int64_feature(img_id),
        'inc0': _float_feature(inc0),
        'inc1': _float_feature(inc1),
        'pop0': _float_feature(pop0),
        'pop1': _float_feature(pop1),
        'lat': _float_feature(lat),
        'lng': _float_feature(lng),
        'urban_share': _float_feature(urban_share),
        'pop_share': _float_feature(pop_share),
        'baseline_features':_bytes_feature(features),
        'categorical_values':_bytes_feature(cats)
    }
    example_proto = tf.train.Example(features=tf.train.Features(feature=feature))
    return example_proto.SerializeToString()

def get_serialize(row, label, scaler, scaled_features, check_id, img_id, categorical_values):
    img0 = row['img{}'.format(0)].astype(np.float32)
    img0 = img0 / scaler
    img0 = img0[7:-7,7:-7,:]
    img0_bytes = tf.io.serialize_tensor(img0)
    img1 = row['img{}'.format(10)].astype(np.float32)
    img1 = img1 / scaler
    img1 = img1[7:-7,7:-7,:]
    img1_bytes = tf.io.serialize_tensor(img1)
    lat = np.array(row["lat"], dtype=np.float32)
    lng = np.array(row["lng"], dtype=np.float32)
    urban_share = np.array(label[check_id]['urban'].item(), dtype=np.float32)
    pop_share = np.array(label[check_id]['popshare_00'].item(), dtype=np.float32)
    inc0 = np.array(label[check_id]['log_inc_{}0'.format(0)].item(), dtype=np.float32)
    pop0 = np.array(label[check_id]['log_pop_{}0'.format(0)].item(), dtype=np.float32)
    inc1 = np.array(label[check_id]['log_inc_{}0'.format(1)].item(), dtype=np.float32)
    pop1 = np.array(label[check_id]['log_pop_{}0'.format(1)].item(), dtype=np.float32)
    features = scaled_features[check_id.to_numpy()]
    features = np.concatenate((features.loc[:,['log_pop_cnty_{}'.format('00'), 'log_inc_cnty_{}'.format('00')]], features.loc[:,'white_00':]), axis=-1)
    features = features.astype(np.float32)
    features_bytes = tf.io.serialize_tensor(features)
    cats = np.array(categorical_values[check_id.to_numpy()], dtype=np.float32)
    cats_bytes = tf.io.serialize_tensor(cats)
    return serialize_example(img0_bytes, img1_bytes, img_id, inc0, inc1, pop0, pop1, lat, lng, urban_share, pop_share, features_bytes, cats_bytes)


def serialize_example_mw(image_low_0, image_low_1, image_high_0, image_high_1, img_id, inc0, inc1, pop0, pop1, lat, lng, urban_share, pop_share, features):
    feature = {
        'image_low_0': _bytes_feature(image_low_0),
        'image_high_0': _bytes_feature(image_high_0),
        'image_low_1': _bytes_feature(image_low_1),
        'image_high_1': _bytes_feature(image_high_1),
        'img_id':_int64_feature(img_id),
        'inc0': _float_feature(inc0),
        'inc1': _float_feature(inc1),
        'pop0': _float_feature(pop0),
        'pop1': _float_feature(pop1),
        'lat': _float_feature(lat),
        'lng': _float_feature(lng),
        'urban_share': _float_feature(urban_share),
        'pop_share': _float_feature(pop_share),
        'baseline_features':_bytes_feature(features)
    }
    example_proto = tf.train.Example(features=tf.train.Features(feature=feature))
    return example_proto.SerializeToString()


def get_serialize_mw(row, label, scaler, scaled_features, check_id, img_id):
    img0 = row['img{}'.format(0)].astype(np.float32)
    img0 = img0 / scaler
    img0 = img0[14:-14, 14:-14, :]
    img_low_0 = img0[:, :, 0:3]
    img_high_0 = img0[:, :, 3:6]
    img_low_0_bytes = tf.io.serialize_tensor(img_low_0)
    img_high_0_bytes = tf.io.serialize_tensor(img_high_0)
    img1 = row['img{}'.format(10)].astype(np.float32)
    img1 = img1 / scaler
    img1 = img1[14:-14, 14:-14, :]
    img_low_1 = img1[:, :, 0:3]
    img_high_1 = img1[:, :, 3:6]
    img_low_1_bytes = tf.io.serialize_tensor(img_low_1)
    img_high_1_bytes = tf.io.serialize_tensor(img_high_1)
    lat = np.array(row["lat"], dtype=np.float32)
    lng = np.array(row["lng"], dtype=np.float32)
    urban_share = np.array(label[check_id]['urban'].item(), dtype=np.float32)
    pop_share = np.array(label[check_id]['popshare_00'].item(), dtype=np.float32)
    inc0 = np.array(label[check_id]['log_inc_{}0'.format(0)].item(), dtype=np.float32)
    pop0 = np.array(label[check_id]['log_pop_{}0'.format(0)].item(), dtype=np.float32)
    inc1 = np.array(label[check_id]['log_inc_{}0'.format(1)].item(), dtype=np.float32)
    pop1 = np.array(label[check_id]['log_pop_{}0'.format(1)].item(), dtype=np.float32)
    features = scaled_features[check_id.to_numpy()]
    features = np.concatenate((features.loc[:,['log_pop_cnty_{}'.format('00'), 'log_inc_cnty_{}'.format('00')]], features.loc[:,'white_00':]), axis=-1)
    features = features.astype(np.float32)
    features_bytes = tf.io.serialize_tensor(features)
    return serialize_example_mw(img_low_0_bytes, img_low_1_bytes, img_high_0_bytes, img_high_1_bytes, img_id, inc0, inc1, pop0, pop1, lat, lng, urban_share, pop_share, features_bytes)


if __name__=="__main__":
    main()