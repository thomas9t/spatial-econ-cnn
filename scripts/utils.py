import sys
import tensorflow as tf


def get_feature_description(feature_type):
    if feature_type == "level":
        feature_description = {
            'image': tf.io.FixedLenFeature((), tf.string),
            'img_id': tf.io.FixedLenFeature((), tf.int64),
            'inc': tf.io.FixedLenFeature((), tf.float32),
            'pop': tf.io.FixedLenFeature((), tf.float32),
            'lat': tf.io.FixedLenFeature((), tf.float32),
            'lng': tf.io.FixedLenFeature((), tf.float32),
            'urban_share': tf.io.FixedLenFeature((), tf.float32),
            'pop_share': tf.io.FixedLenFeature((), tf.float32),
            'baseline_features': tf.io.FixedLenFeature((), tf.string),
            'categorical_values': tf.io.FixedLenFeature((), tf.string)
        }
    elif feature_type == "diff":
        feature_description = {
            'image0': tf.io.FixedLenFeature((), tf.string),
            'image1': tf.io.FixedLenFeature((), tf.string),
            'img_id': tf.io.FixedLenFeature((), tf.int64),
            'inc0': tf.io.FixedLenFeature((), tf.float32),
            'inc1': tf.io.FixedLenFeature((), tf.float32),
            'pop0': tf.io.FixedLenFeature((), tf.float32),
            'pop1': tf.io.FixedLenFeature((), tf.float32),
            'lat': tf.io.FixedLenFeature((), tf.float32),
            'lng': tf.io.FixedLenFeature((), tf.float32),
            'urban_share': tf.io.FixedLenFeature((), tf.float32),
            'pop_share': tf.io.FixedLenFeature((), tf.float32),
            'baseline_features': tf.io.FixedLenFeature((), tf.string),
            'categorical_values': tf.io.FixedLenFeature((), tf.string)
        }
    elif feature_type == 'mw_level':
        feature_description = {
            'image_low': tf.io.FixedLenFeature((), tf.string),
            'image_high': tf.io.FixedLenFeature((), tf.string),
            'img_id': tf.io.FixedLenFeature((), tf.int64),
            'inc': tf.io.FixedLenFeature((), tf.float32),
            'pop': tf.io.FixedLenFeature((), tf.float32),
            'lat': tf.io.FixedLenFeature((), tf.float32),
            'lng': tf.io.FixedLenFeature((), tf.float32),
            'urban_share': tf.io.FixedLenFeature((), tf.float32),
            'pop_share': tf.io.FixedLenFeature((), tf.float32),
            'baseline_features': tf.io.FixedLenFeature((), tf.string)
        }
    elif feature_type == 'mw_diff':
        feature_description = {
            'image_low_0': tf.io.FixedLenFeature((), tf.string),
            'image_high_0': tf.io.FixedLenFeature((), tf.string),
            'image_low_1': tf.io.FixedLenFeature((), tf.string),
            'image_high_1': tf.io.FixedLenFeature((), tf.string),
            'img_id': tf.io.FixedLenFeature((), tf.int64),
            'inc0': tf.io.FixedLenFeature((), tf.float32),
            'inc1': tf.io.FixedLenFeature((), tf.float32),
            'pop0': tf.io.FixedLenFeature((), tf.float32),
            'pop1': tf.io.FixedLenFeature((), tf.float32),
            'lat': tf.io.FixedLenFeature((), tf.float32),
            'lng': tf.io.FixedLenFeature((), tf.float32),
            'urban_share': tf.io.FixedLenFeature((), tf.float32),
            'pop_share': tf.io.FixedLenFeature((), tf.float32),
            'baseline_features': tf.io.FixedLenFeature((), tf.string)
        }
    elif feature_type == "prediction":
        feature_description = {
            'image{}'.format(i): tf.io.FixedLenFeature((), tf.string) for i in range(20)
        }
        feature_description['img_id'] = tf.io.FixedLenFeature((), tf.int64)
        feature_description['baseline_features'] = tf.io.FixedLenFeature((), tf.string)
    else:
        sys.exit('pls use a correct model_type')
    return feature_description


def get_img_size(size, model_type, region, resolution):
    if (size == 'small') & (model_type == 'nl'):
        sys.exit('small imagery has no nl band')

    if size == 'large':
        img_size = 80
        img_augmented_size = 86
        n_origin_bands = 8
    elif size == 'small':
        if region == 'mw':
            img_size = 80
            img_augmented_size = 86
            n_origin_bands = 3
        else:
            img_size = 40
            img_augmented_size = 43
            n_origin_bands = 7
    else:
        sys.exit('pls use "large" or "small" for size')

    if model_type == 'base':
        n_bands = 7
    elif model_type == 'nl':
        n_bands = 8
    elif model_type == 'RGB':
        n_bands = 3
    else:
        sys.exit('pls use "base", "feature", "nl" or "RGB" for model_type')

    if region == 'mw':
        if (model_type == 'RGB') & (size == 'small'):
            if resolution == 'high':
                res = resolution
            elif resolution == 'low':
                res = resolution
            else:
                sys.exit('pls use "high" or "low" for resolution')
        else:
            sys.exit('only small and RGB model for mw data')
    elif region == 'national':
        if resolution == 'high':
            sys.exit('only small mw data has high resolution bands')
        elif resolution == 'low':
            res = ''
        else:
            sys.exit('pls use "high" or "low" for resolution')
    else:
        sys.exit('pls use "nw" or "national" for region')

    return img_size, img_augmented_size, n_origin_bands, n_bands, res


def get_type(year, region):
    if year == 'merged':
        if region == 'mw':
            feature_type = 'mw_level'
        else:
            feature_type = 'level'
        test_type = 'all'
        year = ''
    elif year == '2000':
        test_type = '15'
        feature_type = 'test'
        year = '0'
    elif year == '2010':
        test_type = '15'
        feature_type = 'test'
        year = '10'
    elif year == '2015':
        test_type = '15'
        feature_type = 'test'
        year = '15'
    elif year == 'diff':
        if region == 'mw':
            feature_type = 'mw_diff'
        else:
            feature_type = 'diff'
        test_type = 'diff'
        year = ''
    else:
        sys.exit('pls use "merged", "2000", "2010" or "2015" for year')

    return test_type, feature_type, year


def ds_len(ds):
    return len(list(ds.map(lambda x, y: 1, num_parallel_calls=tf.data.experimental.AUTOTUNE)))


def get_bool(x):
    if x == 'True':
        return True
    elif x == 'False':
        return False
    else:
        sys.exit('pls use "True" or "False" for with_feature')


def paste_string(string_list):
    r = string_list[0]
    string_list.pop(0)
    for i in string_list:
        if i == '':
            continue
        r = r + '_' + i
    return r


class RSquare(tf.keras.metrics.Metric):

    def __init__(self, name='r_square', dtype=tf.float32):
        super(RSquare, self).__init__(name=name, dtype=dtype)
        self.squared_sum = self.add_weight("squared_sum", initializer="zeros")
        self.sum = self.add_weight("sum", initializer="zeros")
        self.res = self.add_weight("residual", initializer="zeros")
        self.count = self.add_weight("count", initializer="zeros")

    def update_state(self, y_true, y_pred, sample_weight=None):
        y_true = tf.convert_to_tensor(y_true, tf.float32)
        y_pred = tf.convert_to_tensor(y_pred, tf.float32)
        self.squared_sum.assign_add(tf.reduce_sum(y_true ** 2))
        self.sum.assign_add(tf.reduce_sum(y_true))
        self.res.assign_add(
            tf.reduce_sum(tf.square(tf.subtract(y_true, y_pred))))
        self.count.assign_add(tf.cast(tf.shape(y_true)[0], tf.float32))

    def result(self):
        mean = self.sum / self.count
        total = self.squared_sum - 2 * self.sum * mean + self.count * mean ** 2
        return 1 - (self.res / total)

    def reset_states(self):
        # The state of the metric will be reset at the start of each epoch.
        self.squared_sum.assign(0.0)
        self.sum.assign(0.0)
        self.res.assign(0.0)
        self.count.assign(0.0)


