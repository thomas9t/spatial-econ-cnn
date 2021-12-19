import numpy as np
from utils import *


def read_files(files_dir, ds_map, mode="test"):
    files = tf.io.matching_files(files_dir)
    shards = tf.data.Dataset.from_tensor_slices(files)
    if mode == 'train':
        shards = shards.shuffle(buffer_size=len(files), reshuffle_each_iteration=True)
    elif (mode == 'test') | (mode == 'validation'):
        pass
    else:
        print('pls use a correct data loading mode')
    dataset = shards.interleave(tf.data.TFRecordDataset)
    dataset = dataset.map(ds_map, num_parallel_calls=tf.data.experimental.AUTOTUNE)
    return dataset


def decode(serialized_example, feature_description, img_size, n_origin_bands, n_bands, datatype, res, year=''):
    example = tf.io.parse_single_example(serialized_example, feature_description)
    image = tf.io.parse_tensor(example[paste_string(['image', year, res])], out_type=float)
    image = tf.reshape(image, (img_size, img_size, n_origin_bands))
    image = image[:, :, 0:n_bands]
    image = tf.clip_by_value(image, 0, 1)
    if datatype == "inc_pop":
        label = tf.reshape(example["inc" + year] - example["pop" + year], [-1])
    else:
        label = tf.reshape(example[datatype + year], [-1])
    label = tf.reshape(example[datatype + year], [-1])
    features = tf.io.parse_tensor(example['baseline_features'], out_type=float)
    features = tf.reshape(features, (34,))

    return image, features, label


def decode_diff(serialized_example, feature_description, img_size, n_origin_bands, n_bands, datatype, res):
    example = tf.io.parse_single_example(serialized_example, feature_description)
    image0 = tf.io.parse_tensor(example['image0' if res == '' else paste_string(['image', res, '0'])], out_type=float)
    image1 = tf.io.parse_tensor(example['image1' if res == '' else paste_string(['image', res, '1'])], out_type=float)
    image0 = tf.reshape(image0, (img_size, img_size, n_origin_bands))
    image1 = tf.reshape(image1, (img_size, img_size, n_origin_bands))
    image0 = image0[:, :, 0:n_bands]
    image1 = image1[:, :, 0:n_bands]
    image0 = tf.clip_by_value(image0, 0, 1)
    image1 = tf.clip_by_value(image1, 0, 1)
    if datatype=="inc_pop":
        label0 = tf.reshape(example['inc0'] - example['pop0'], [-1])
        label1 = tf.reshape(example['inc1'] - example['pop1'], [-1])
    else:
        label0 = tf.reshape(example['{}0'.format(datatype)], [-1])
        label1 = tf.reshape(example['{}1'.format(datatype)], [-1])
    label = label1 - label0
    features = tf.io.parse_tensor(example['baseline_features'], out_type=float)
    features = tf.reshape(features, (34,))

    return image0, image1, features, label


def data_process_train(image, features, label, img_size, img_augmented_size, n_bands, with_feature):
    fraction = np.random.uniform(0.90, 1.0, 1)
    image = tf.image.random_flip_left_right(image)
    image = tf.image.central_crop(image, fraction)
    image = tf.image.resize(image, [img_size, img_size])
    image = tf.image.resize_with_crop_or_pad(image, img_augmented_size, img_augmented_size)
    image = tf.image.random_crop(image, size=[tf.shape(image)[0], img_size, img_size, n_bands])
    if with_feature:
        return (image, features), label
    else:
        return image, label


def data_process_diff_train(image0, image1, features, label, img_size, img_augmented_size, n_bands, with_feature):
    fraction = np.random.uniform(0.90, 1.0, 1)
    image0 = tf.image.central_crop(image0, fraction)
    image0 = tf.image.resize(image0, [img_size, img_size])
    image0 = tf.image.resize_with_crop_or_pad(image0, img_augmented_size, img_augmented_size)
    image0 = tf.image.random_crop(image0, size=[tf.shape(image0)[0], img_size, img_size, n_bands])
    image1 = tf.image.central_crop(image1, fraction)
    image1 = tf.image.resize(image1, [img_size, img_size])
    image1 = tf.image.resize_with_crop_or_pad(image1, img_augmented_size, img_augmented_size)
    image1 = tf.image.random_crop(image1, size=[tf.shape(image1)[0], img_size, img_size, n_bands])
    if with_feature:
        return (image0, image1, features), label
    else:
        return (image0, image1), label


def data_process(image, features, label, with_feature):
    if with_feature:
        return (image, features), label
    else:
        return image, label


def data_process_diff(image0, image1, features, label, with_feature):
    if with_feature:
        return (image0, image1, features), label
    else:
        return (image0, image1), label


def get_dataset(ds_dir, size, datatype, model_type, with_feature, bs, year, region, resolution, subset):
    img_size, img_augmented_size, n_origin_bands, n_bands, res = get_img_size(size, model_type, region, resolution)
    test_type, feature_type, year = get_type(year, region)
    feature_description = get_feature_description(feature_type)
    decode_map = lambda x: decode(x, feature_description, img_size, n_origin_bands, n_bands, datatype, res, year)
    ds = read_files(ds_dir.format(test_type, subset, test_type), decode_map, subset)
    if subset == "train":
        process_map = lambda x, y, z: data_process_train(x, y, z, img_size, img_augmented_size, n_bands, with_feature)
        ds = ds.shuffle(10000)
    elif (subset == "validation") | (subset == "test"):
        process_map = lambda x, y, z: data_process(x, y, z, with_feature)
    ds = ds.batch(bs).map(process_map, num_parallel_calls=tf.data.experimental.AUTOTUNE)
    return ds


def get_diff_dataset(ds_dir, size, datatype, model_type, with_feature, bs, year, region, resolution, subset):
    img_size, img_augmented_size, n_origin_bands, n_bands, res = get_img_size(size, model_type, region, resolution)
    test_type, feature_type, year = get_type(year, region)
    feature_description = get_feature_description(feature_type)
    decode_map = lambda x: decode_diff(x, feature_description, img_size, n_origin_bands, n_bands, datatype, res)
    ds = read_files(ds_dir.format(test_type, subset, test_type), decode_map, subset)
    if subset == "train":
        process_map = lambda a, b, c, d: data_process_diff_train(a, b, c, d, img_size, img_augmented_size, n_bands, with_feature)
        ds = ds.shuffle(10000, reshuffle_each_iteration=True)
    elif (subset == "validation") | (subset == "test"):
        process_map = lambda a, b, c, d: data_process_diff(a, b, c, d, with_feature)
    ds = ds.batch(bs).map(process_map, num_parallel_calls=tf.data.experimental.AUTOTUNE)
    return ds
