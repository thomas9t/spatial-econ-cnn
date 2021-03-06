import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ['TF_GPU_THREAD_MODE'] = 'gpu_private'
from models import *
from data_loader import *

tf.random.set_seed(1234567)
physical_devices = tf.config.experimental.list_physical_devices('GPU')
if len(physical_devices) > 0:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)
tf.config.threading.set_inter_op_parallelism_threads(1)

construct = sys.argv[1]  # BG or block
region = sys.argv[2]  # ['national', 'mw']
model_type = sys.argv[3]  # ['base', 'RGB', 'nl']
size = sys.argv[4]  # ['large', 'small']
datatype = sys.argv[5]  # ['inc', 'pop', 'inc_pop']
resolution = sys.argv[6]  # ['high', 'low']
with_feature = get_bool(sys.argv[7])  # [True, False]
epochs = int(sys.argv[8])  # how many epochs to train for?
data_dir = sys.argv[9]  # /source/data or ../temp
out_dir = sys.argv[10]  # /storage/national_level_result large or small
all_sample = get_bool(sys.argv[11]) # [True, False]

HP_LR = hp.HParam('lr', hp.Discrete([1e-4]))
HP_L2 = hp.HParam('l2', hp.Discrete([1e-6, 1e-7, 1e-8]))
HP_BS = hp.HParam('bs', hp.Discrete([16]))
HP_DS = hp.HParam('ds', hp.Discrete([50, 100, 200]))
HP_NF = hp.HParam('nf', hp.Discrete([32]))
HP_DR = hp.HParam('dr', hp.Discrete([0.5]))

ds_dir = '{}/{}_{}_{}_{}/{}_{}_{}_{}_{}_*-of-*.tfrecords' \
    .format(data_dir, size, construct, '{}', region, '{}', construct, size, '{}', region)
out_dir = '{}/{}_{}_{}_level_{}{}{}_{}_{}{}' \
    .format(out_dir, construct, size, region, model_type, '_feature' if with_feature else '',
            '_high' if resolution == 'high' else '', datatype, epochs, '_all' if all_sample else '')
logdir = '{}/logs'.format(out_dir)
checkdir = '{}/checkpoints'.format(out_dir)


def main():
    print("Start finetuning of {}_{}_level_{}{}{}_{}{} model with epochs={}"
          .format(size, region, model_type, '_feature' if with_feature else '',
                  '_high' if resolution == 'high' else '', datatype, epochs, '_all' if all_sample else '')
          )
    print("You can use tensorboard to monitor the process $ tensorboard --logdir='{}'".format(logdir))

    session_num = 0
    combined = [(lr, l2, bs, ds, nf, dr)
                for lr in HP_LR.domain.values
                for l2 in HP_L2.domain.values
                for bs in HP_BS.domain.values
                for ds in HP_DS.domain.values
                for nf in HP_NF.domain.values
                for dr in HP_DR.domain.values
                ]
    year = 'merged'
    bs = 16
    img_size, _, _, n_bands, _ = get_img_size(size, model_type, region, resolution)

    train = get_dataset(ds_dir, size, datatype, model_type, with_feature, bs, year, region, resolution, 'train', all_sample)
    valid = get_dataset(ds_dir, size, datatype, model_type, with_feature, bs, year, region, resolution, 'test' if all_sample else 'validation', all_sample)
    test = get_dataset(ds_dir, size, datatype, model_type, with_feature, bs, year, region, resolution, 'test', all_sample)

    with tf.summary.create_file_writer(logdir + '/hparam_tuning/').as_default():
        hp.hparams_config(
            hparams=[HP_LR, HP_L2, HP_BS, HP_DS, HP_NF, HP_DR],
            metrics=[hp.Metric('valid_r_square', display_name='Valid_R_square'),
                     hp.Metric('test_r_square', display_name='Test_R_square')
                     ],
        )

    for (lr, l2, bs, ds, nf, dr) in combined:
        hparams = {
            'lr': lr,
            'l2': l2,
            'bs': bs,
            'ds': ds,
            'nf': nf,
            'dr': dr,
        }
        tf.keras.backend.clear_session()
        run_name = "run-%d" % session_num
        print('--- Starting trial: %s' % run_name)
        print({h: hparams[h] for h in hparams})
        model = make_level_model(img_size, n_bands, l2, nf, dr, with_feature)
        run_dir = logdir + '/hparam_tuning/{}_{}_{}_{}_{}_{}'.format(lr, l2, bs, ds, nf, dr)
        run(run_dir, hparams, model, train, valid, test, logdir, checkdir, epochs)
        session_num += 1
        print('--- End trial: %s' % run_name)

    print("Complete! please use tensorboard to check the result. $ tensorboard --logdir='{}'".format(logdir))


if __name__ == "__main__":
    main()
