import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
import tensorflow as tf
import sys
from tqdm import tqdm
# physical_devices = tf.config.experimental.list_physical_devices('GPU')
# tf.config.experimental.set_memory_growth(physical_devices[0], True)
# tf.config.threading.set_inter_op_parallelism_threads(1)


size = sys.argv[1]
construct = sys.argv[2] # BG or block
model = sys.argv[3] # all or diff
n_images_shard = int(sys.argv[4])
region = sys.argv[5] # national or mw 
train = tf.data.TFRecordDataset('../temp/train_{}_{}_{}_{}.tfrecords'.format(construct, size, model, region))
valid = tf.data.TFRecordDataset('../temp/validation_{}_{}_{}_{}.tfrecords'.format(construct, size, model, region))
test = tf.data.TFRecordDataset('../temp/test_{}_{}_{}_{}.tfrecords'.format(construct, size, model, region))
if not os.path.exists('../temp/{}_{}_{}_{}'.format(size, construct, model, region)):
    os.makedirs('../temp/{}_{}_{}_{}'.format(size, construct, model, region))
out_dir = '../temp/{}_{}_{}_{}/{}_{}_{}_{}_{}_{}.tfrecords'.format(size, construct, model, region, '{}', construct, size, model, region, '{}')


def main():
    make_shard(train, n_images_shard, out_dir.format('train', '{}'))
    make_shard(valid, n_images_shard, out_dir.format('validation', '{}'))
    make_shard(test, n_images_shard, out_dir.format('test', '{}'))
    print('Finish!')


def ds_len(ds):
    return len(list(ds.map(lambda x: 1, num_parallel_calls=tf.data.experimental.AUTOTUNE)))


def make_shard(ds, n_image_shards, output_path):
    length = ds_len(ds)
    n_shards = int(length / n_images_shard) + (1 if length % n_image_shards != 0 else 0)
    n = 0
    for shard in tqdm(ds.shuffle(length).batch(n_images_shard).as_numpy_iterator()):
        tfrecords_shard_path = output_path.format('%.5d-of-%.5d' % (n, n_shards - 1))
        n += 1
        with tf.io.TFRecordWriter(tfrecords_shard_path) as writer:
            for row in shard:
                writer.write(row)


if __name__ == "__main__":
    main()