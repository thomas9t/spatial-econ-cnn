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

FEATURES = ['log_pop_cnty_00', 'log_pop_cnty_10', 'log_pop_cnty_15',
            'log_inc_cnty_00', 'log_inc_cnty_10', 'log_inc_cnty_15', 'area',
            'image_coverage', 'white_00', 'black_00', 'hispanic_00', 'workage_00',
            'female_00', 'groupshare_00', 'emp_sec1_00', 'emp_sec2_00',
            'emp_sec3_00', 'emp_sec4_00', 'emp_sec5_00', 'emp_sec6_00',
            'emp_sec7_00', 'emp_sec8_00', 'emp_sec9_00', 'emp_sec10_00',
            'emp_sec11_00', 'emp_sec12_00', 'emp_sec13_00', 'emp_sec14_00',
            'emp_sec15_00', 'emp_sec16_00', 'emp_sec17_00', 'emp_sec18_00',
            'emp_sec19_00', 'emp_sec20_00', 'emp_bus_serv_00', 'emp_nonbus_serv_00',
            'emp_prod_00', 'emp_bus_serv_cnty_00', 'emp_nonbus_serv_cnty_00',
            'emp_prod_cnty_00']

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
        dataset = tables.open_file("../temp/high_resolution_small_images_raw.h5")
    elif region == "national":
        dataset = tables.open_file("../temp/{}_images_all_years_raw.h5".format(size))
    label = pd.read_csv('../temp/{}cw_labelled_imgs_{}_{}.csv'.format(construct, region, size))
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
    print("Prep testing dataset for {} {} {} images".format(construct, region, size))
    write_example(dataset, label, 'train', scaler, scaled_features, categorical_values)
    write_example(dataset, label, 'validation', scaler, scaled_features, categorical_values)
    write_example(dataset, label, 'test', scaler, scaled_features, categorical_values)
    print("Complete!")
    
def write_example(dataset, label, subset, scaler, scaled_features, categorical_values):
    print("Start creating {} set...".format(subset))
    with tf.io.TFRecordWriter('../temp/{}_{}_{}_{}_{}.tfrecords'.format(subset,construct,size, "15", region)) as writer:
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
                        example = get_serialize_test(row, label, scaler, scaled_features, check_id, img_id, categorical_values)
                        writer.write(example)
                        ne += 1
                    elif region == "mw":
                        example = get_serialize_mw_test(row, label, scaler, scaled_features, check_id, img_id)
                        writer.write(example)
                        ne += 1
                    else:
                        sys.exit('invalid region')
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


def serialize_example_test(image0, image10, image15, img_id, inc0, inc10, inc15,
                      pop0, pop10, lat, lng, urban_share, pop_share, features, cats):
    feature = {
        'image0': _bytes_feature(image0),
        'image10': _bytes_feature(image10),
        'image15': _bytes_feature(image15),
        'img_id': _int64_feature(img_id),
        'inc0': _float_feature(inc0),
        'inc10': _float_feature(inc10),
        'inc15': _float_feature(inc15),
        'pop0': _float_feature(pop0),
        'pop10': _float_feature(pop10),
        'lat': _float_feature(lat),
        'lng': _float_feature(lng),
        'urban_share': _float_feature(urban_share),
        'pop_share': _float_feature(pop_share),
        'baseline_features': _bytes_feature(features),
        'categorical_values': _bytes_feature(cats)
    }
    example_proto = tf.train.Example(features=tf.train.Features(feature=feature))
    return example_proto.SerializeToString()


def get_serialize_test(row, label, scaler, scaled_features, check_id, img_id, categorical_values):
    img0 = row['img{}'.format(0)].astype(np.float32)
    img0 = img0 / scaler
    img0 = img0[7:-7, 7:-7, :]
    img0_bytes = tf.io.serialize_tensor(img0)
    img10 = row['img{}'.format(10)].astype(np.float32)
    img10 = img10 / scaler
    img10 = img10[7:-7, 7:-7, :]
    img10_bytes = tf.io.serialize_tensor(img10)
    img15 = row['img{}'.format(15)].astype(np.float32)
    img15 = img15 / scaler
    img15 = img15[7:-7, 7:-7, :]
    img15_bytes = tf.io.serialize_tensor(img15)
    lat = np.array(row["lat"], dtype=np.float32)
    lng = np.array(row["lng"], dtype=np.float32)
    urban_share = np.array(label[check_id]['urban'].item(), dtype=np.float32)
    pop_share = np.array(label[check_id]['popshare_00'].item(), dtype=np.float32)
    inc0 = np.array(label[check_id]['log_inc_00'].item(), dtype=np.float32)
    pop0 = np.array(label[check_id]['log_pop_00'].item(), dtype=np.float32)
    inc10 = np.array(label[check_id]['log_inc_10'].item(), dtype=np.float32)
    pop10 = np.array(label[check_id]['log_pop_10'].item(), dtype=np.float32)
    inc15 = np.array(label[check_id]['log_inc_15'].item(), dtype=np.float32)
    features = scaled_features[check_id.to_numpy()]
    features = np.concatenate((features.loc[:, ['log_pop_cnty_{}'.format('00'), 'log_inc_cnty_{}'.format('00')]],
                               features.loc[:,'white_00':]), axis=-1)
    features = features.astype(np.float32)
    features_bytes = tf.io.serialize_tensor(features)
    cats = np.array(categorical_values[check_id.to_numpy()], dtype=np.float32)
    cats_bytes = tf.io.serialize_tensor(cats)
    return serialize_example_test(img0_bytes, img10_bytes, img15_bytes, img_id, inc0, inc10, inc15, pop0, pop10, lat, lng, urban_share, pop_share, features_bytes, cats_bytes)


def serialize_example_mw_test(image_low_0, image_low_10, image_low_15, image_high_0, image_high_10, image_high_15, img_id,
                      inc0, inc10, inc15, pop0, pop10, lat, lng, urban_share, pop_share, features):
    feature = {
        'image_low_0': _bytes_feature(image_low_0),
        'image_low_10': _bytes_feature(image_low_10),
        'image_low_15': _bytes_feature(image_low_15),
        'image_high_0': _bytes_feature(image_high_0),
        'image_high_10': _bytes_feature(image_high_10),
        'image_high_15': _bytes_feature(image_high_15),
        'img_id': _int64_feature(img_id),
        'inc0': _float_feature(inc0),
        'inc10': _float_feature(inc10),
        'inc15': _float_feature(inc15),
        'pop0': _float_feature(pop0),
        'pop10': _float_feature(pop10),
        'lat': _float_feature(lat),
        'lng': _float_feature(lng),
        'urban_share': _float_feature(urban_share),
        'pop_share': _float_feature(pop_share),
        'baseline_features': _bytes_feature(features)
    }
    example_proto = tf.train.Example(features=tf.train.Features(feature=feature))
    return example_proto.SerializeToString()


def get_serialize_mw_test(row, label, scaler, scaled_features, check_id, img_id):
    img0 = row['img{}'.format(0)].astype(np.float32)
    img0 = img0 / scaler
    img0 = img0[14:-14, 14:-14, :]
    img_low_0 = img0[:, :, 0:3]
    img_high_0 = img0[:, :, 3:6]
    img_low_bytes_0 = tf.io.serialize_tensor(img_low_0)
    img_high_bytes_0 = tf.io.serialize_tensor(img_high_0)
    img10 = row['img{}'.format(10)].astype(np.float32)
    img10 = img10 / scaler
    img10 = img10[14:-14, 14:-14, :]
    img_low_10 = img10[:, :, 0:3]
    img_high_10 = img10[:, :, 3:6]
    img_low_bytes_10 = tf.io.serialize_tensor(img_low_10)
    img_high_bytes_10 = tf.io.serialize_tensor(img_high_10)
    img15 = row['img{}'.format(15)].astype(np.float32)
    img15 = img15 / scaler
    img15 = img15[14:-14, 14:-14, :]
    img_low_15 = img15[:, :, 0:3]
    img_high_15 = img15[:, :, 3:6]
    img_low_bytes_15 = tf.io.serialize_tensor(img_low_15)
    img_high_bytes_15 = tf.io.serialize_tensor(img_high_15)
    lat = np.array(row["lat"], dtype=np.float32)
    lng = np.array(row["lng"], dtype=np.float32)
    urban_share = np.array(label[check_id]['urban'].item(), dtype=np.float32)
    pop_share = np.array(label[check_id]['popshare_00'].item(), dtype=np.float32)
    inc0 = np.array(label[check_id]['log_inc_00'].item(), dtype=np.float32)
    pop0 = np.array(label[check_id]['log_pop_00'].item(), dtype=np.float32)
    inc10 = np.array(label[check_id]['log_inc_10'].item(), dtype=np.float32)
    pop10 = np.array(label[check_id]['log_pop_10'].item(), dtype=np.float32)
    inc15 = np.array(label[check_id]['log_inc_15'].item(), dtype=np.float32)
    features = scaled_features[check_id.to_numpy()]
    features = np.concatenate((features.loc[:, ['log_pop_cnty_{}'.format('00'), 'log_inc_cnty_{}'.format('00')]],
                               features.loc[:, 'white_00':]), axis=-1)
    features = features.astype(np.float32)
    features_bytes = tf.io.serialize_tensor(features)
    return serialize_example_mw_test(img_low_bytes_0,img_low_bytes_10,img_low_bytes_15, img_high_bytes_0, img_high_bytes_10, img_high_bytes_15, img_id, inc0, inc10, inc15, pop0, pop10, lat, lng, urban_share, pop_share, features_bytes)


if __name__=="__main__":
    main()