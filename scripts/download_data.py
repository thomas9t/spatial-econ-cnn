import os
import sys
import tables
import logging

import numpy as np
import pandas as pd
import tensorflow as tf
np.random.seed(13298)
tf.config.threading.set_inter_op_parallelism_threads(1)

tf.compat.v1.disable_eager_execution()

from google_drive_utils import GDFolderDownloader
from params import *

LOG = logging.getLogger(os.path.basename(__file__))
ch = logging.StreamHandler()
log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
ch.setFormatter(logging.Formatter(log_fmt))
ch.setLevel(logging.INFO)
LOG.addHandler(ch)
LOG.setLevel(logging.INFO)

YEARS = list(range(0,20))
path = "../data/small_images_all_years_raw.h5"  # Where should the output HDF5 file be written?

root_dir_id = "1d1Fw4nuM_9a8xAguehLFW7UmsZVk8dt-"  # The folder in Google Drive that contains the raw data (this will need to be changed if you created a new extract)
IMG_ROWS_RAW = 54  # The number of rows in the raw images (54 for small, 94 for large)
IMG_COLS_RAW = 54  # The number of columns in the raw images (54 for small, 94 for large)
CHANNEL_NAMES = CHANNEL_NAMES_SMALL
IMG_SHAPE = (IMG_ROWS_RAW, IMG_COLS_RAW, len(CHANNEL_NAMES))
class IMGData(tables.IsDescription):
    img0 = tables.Float32Col(shape=IMG_SHAPE)
    img1 = tables.Float32Col(shape=IMG_SHAPE)
    img2 = tables.Float32Col(shape=IMG_SHAPE)
    img3 = tables.Float32Col(shape=IMG_SHAPE)
    img4 = tables.Float32Col(shape=IMG_SHAPE)
    img5 = tables.Float32Col(shape=IMG_SHAPE)
    img6 = tables.Float32Col(shape=IMG_SHAPE)
    img7 = tables.Float32Col(shape=IMG_SHAPE)
    img8 = tables.Float32Col(shape=IMG_SHAPE)
    img9 = tables.Float32Col(shape=IMG_SHAPE)
    img10 = tables.Float32Col(shape=IMG_SHAPE)
    img11 = tables.Float32Col(shape=IMG_SHAPE)
    img12 = tables.Float32Col(shape=IMG_SHAPE)
    img13 = tables.Float32Col(shape=IMG_SHAPE)
    img14 = tables.Float32Col(shape=IMG_SHAPE)
    img15 = tables.Float32Col(shape=IMG_SHAPE)
    img16 = tables.Float32Col(shape=IMG_SHAPE)
    img17 = tables.Float32Col(shape=IMG_SHAPE)
    img18 = tables.Float32Col(shape=IMG_SHAPE)
    img19 = tables.Float32Col(shape=IMG_SHAPE)
    lat  = tables.Float32Col()
    lng  = tables.Float32Col()
    img_id = tables.Int64Col()
    urban_share = tables.Float32Col()

def main():
    # This may need to be updated periodically
    
    if not os.path.exists("../temp_small"):
        os.mkdir("../temp_small")
    if not os.path.exists("../output"):
        os.mkdir("../output")
    mode = "w" if not os.path.exists(path) else "a"
    h5_file = tables.open_file(path, mode=mode)
    if "/data" not in h5_file:
        h5_file.create_table("/", "data", IMGData)
    table = h5_file.get_node("/data")
    
    # Used to keep track of what data has already been downloaded
    # in case the pod crashes and we need to restart
    processed_paths_file = "../output/processed_paths_small.txt"
    if not os.path.exists(processed_paths_file):
        with open(processed_paths_file, "w") as fh:
            pass

    # Note: we should not expect these images to "look" reasonable if displayed
    # They are coded using a different scheme.
    GD = GDFolderDownloader(
        root_dir_id, 
        "../temp_small", os.getcwd() + "/client_secrets.json",
        processed_paths_file)
    GD.file_list = filter(lambda x: ".tfrecord" in x["title"], GD.file_list)

    key = lambda x: int(x["title"].split("-")[-1].replace(".tfrecord",""))
    GD.file_list = sorted(GD.file_list, key=key)
    
    ix = 0
    invalid_data = 0

    outfh_path = "../output/valid_imgs_small.txt"
    mode = "w" if not os.path.exists(outfh_path) else "a"
    out_fh = open(outfh_path, mode)
    if mode == "w":
        out_fh.write("filename,img_num_in_file,img_id,lat,lng,urban\n")
 
    LOG.info("Total Images to download: {}".format(len(GD.file_list)))

    total_imgs = 0
    for fpath in GD.file_iterator():
        img_num = 0
        if fpath is None:
            LOG.info("File exists - Delete it to download again...")
            continue
        
        it = tfr_data_pipeline(fpath, IMG_ROWS_RAW, IMG_COLS_RAW)
        with tf.compat.v1.Session() as sess:
            while True:
                try:
                    imgs, lat, lng, urban = sess.run(it)
                    img_num += 1
                    
                    urban[np.isnan(urban)] = 0
                    if np.mean(urban) < 0.1:
                        continue

                    lat = lat[IMG_ROWS_RAW//2,IMG_COLS_RAW//2]
                    lng = lng[IMG_ROWS_RAW//2,IMG_COLS_RAW//2]
                    ix += 1
                    out_fh.write("{},{},{},{},{},{}\n".format(
                        fpath, img_num, ix, lat, lng, np.nanmean(urban)))
                    
                    for y in YEARS:
                        table.row["img{}".format(y)] = imgs[y]
                    table.row["urban_share"] = np.nanmean(urban)
                    table.row["lat"] = lat
                    table.row["lng"] = lng
                    table.row["img_id"] = ix
                    table.row.append()
                    total_imgs += 1

                except tf.errors.OutOfRangeError:
                    break
                except tf.errors.DataLossError:
                    invalid_data += 1
                    break
            
        LOG.info("Wrote: {} images".format(total_imgs))
        with open(processed_paths_file, "a") as fh:
            fh.write(fpath + "\n")
        os.unlink(fpath)

    LOG.info("Total images processed: {}".format(ix))
    LOG.info("Invalid data errors: {}".format(invalid_data))

    h5_file.close()

def tfr_data_pipeline(path, img_rows, img_cols):
    channel_names = ["{}_{}".format(x,y) for x in CHANNEL_NAMES for y in YEARS]
    other_vars = ["urban", "longitude", "latitude"]

    varnames = channel_names + other_vars
    features = [tf.compat.v1.FixedLenFeature([img_rows*img_cols], tf.float32)] * len(varnames)
    features_dict = dict(zip(varnames, features))

    def parse_example(example_proto):
        parsed_features = tf.compat.v1.parse_single_example(example_proto, features_dict)
        
        # reshape the vector data into an image suitable for use in a net
        f = lambda x: tf.reshape(x, (img_rows, img_cols))
        imgs = {}
        axes = [2, 1, 0]
        for y in YEARS:
            cname = ["{}_{}".format(x,y) for x in CHANNEL_NAMES]
            ii = tf.stack([f(parsed_features[x]) for x in cname], 0)
            ii = tf.transpose(ii, axes)
            imgs[y] = ii
        
        urban = f(parsed_features["urban"])

        lat = f(parsed_features["latitude"])
        lng = f(parsed_features["longitude"])

        return imgs, lat, lng, urban

    ds = tf.data.TFRecordDataset(path)
    parsed_ds = ds.map(parse_example)
    it = tf.compat.v1.data.make_one_shot_iterator(parsed_ds)
    return it.get_next()


if __name__=="__main__":
    main()