import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
import pandas as pd
from models import *
from data_loader import *
from tqdm import tqdm

tf.random.set_seed(1234567)
physical_devices = tf.config.experimental.list_physical_devices('GPU')
if len(physical_devices) > 0:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)

construct = sys.argv[1]  # BG or block
region = sys.argv[2]  # ['national']
model_type = sys.argv[3]  # ['base', 'RGB', 'nl']
size = sys.argv[4]  # ['large', 'small']
datatype = sys.argv[5]  # ['inc', 'pop', 'inc_pop']
resolution = sys.argv[6]  # ['low']
with_feature = get_bool(sys.argv[7])  # [True, False]
data_dir = sys.argv[8]  # dir of dataset
out_dir = sys.argv[9]  # dir of output
weight_dir = sys.argv[10]
lr = float(sys.argv[11])
l2 = float(sys.argv[12])
bs = int(sys.argv[13])
ds = int(sys.argv[14])
nf = int(sys.argv[15])
dr = float(sys.argv[16])
epochs = int(sys.argv[17])
sep = int(sys.argv[18])
all_sample = get_bool(sys.argv[19]) # [True, False]
test_type = 'prediction'

if (region != 'national') | (model_type != 'base'):
        sys.exit('Currently all-year prediction only works for national base model')

ds_dir = '{}/{}_{}_{}_{}_sharded/{}_{}_{}_{}_{}_*-of-*.tfrecords' \
        .format(data_dir, size, construct, test_type, region, '*', construct, size, test_type, region)

weight_dir = '{}/{}_{}_{}_diff_{}{}_{}_{}{}/checkpoints/{}_{}_{}_{}_{}_{}' \
        .format(weight_dir, construct, size, region, model_type, '_feature' if with_feature else '', datatype, epochs, '_all' if all_sample else '', lr, l2, bs, ds, nf, dr)

def main():
    columns = ['{}_{}_{}'.format(datatype, year, year+sep) for year in range(20-sep)]
    columns = ['img_id'] + columns
    df = pd.DataFrame(columns=columns)
    img_size, _, _, n_bands, _ = get_img_size(size, model_type, region, resolution)
    model = make_level_model(img_size, n_bands, l2, nf, dr, with_feature)
    diff_model = make_diff_model(img_size, n_bands, l2, nf, dr, with_feature, model)
    diff_model.load_weights(weight_dir).expect_partial()
    ds = read_files(ds_dir.format(ds_dir), lambda x: parse(x, get_feature_description(test_type)))
    df = predict(ds, diff_model, df)
    df.to_csv('{}/{}_{}_{}_diff_{}{}_{}{}_{}_years_predictions.csv'.format(out_dir, construct, size, region, model_type, '_feature' if with_feature else '', datatype, '_all' if all_sample else '',  sep), index=False)
    print('complete!')


def predict(ds, diff_model, df):
    if with_feature:
        for img0, img1, features, img_id in tqdm(ds.as_numpy_iterator()):
            predictions = diff_model((img0, img1, features), training=False)
            row = {'img_id': img_id}
            row.update({'{}_{}_{}'.format(datatype, year, year+sep): predictions[year].numpy()[0] for year in range(20-sep)})
            df = df.append(row, ignore_index=True)
    else:
        for img0, img1, img_id in tqdm(ds.as_numpy_iterator()):
            predictions = diff_model((img0, img1), training=False)
            row = {'img_id': img_id}
            row.update({'{}_{}_{}'.format(datatype, year, year+sep): predictions[year].numpy()[0] for year in range(20-sep)})
            df = df.append(row, ignore_index=True)
    return df


def parse(serialized_example, feature_description):
    example = tf.io.parse_single_example(serialized_example, feature_description)
    img0 = tf.stack([tf.clip_by_value(tf.io.parse_tensor(example['image{}'.format(y)], out_type=float)[:, :, 0:7], 0, 1) for y in range(20-sep)], 0)
    img1 = tf.stack([tf.clip_by_value(tf.io.parse_tensor(example['image{}'.format(y+sep)], out_type=float)[:, :, 0:7], 0, 1) for y in range(20-sep)], 0)
    img_id = example['img_id']
    if with_feature:
        features = tf.io.parse_tensor(example['baseline_features'], out_type=float)
        features = tf.reshape(features, (34,))
        features = tf.stack([features for y in range(20-sep)], 0)
        return img0, img1, features, img_id
    else:
        return img0, img1, img_id


if __name__ == "__main__":
    main()
