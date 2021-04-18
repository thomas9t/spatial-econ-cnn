from tensorboard.plugins.hparams import api as hp
from utils import *


def conv_block(inputs, n_filter, regularizer, common_args):
    x = tf.keras.layers.Conv2D(filters=n_filter,
                               kernel_size=3,
                               strides=1,
                               padding='same',
                               activation='relu',
                               kernel_regularizer=regularizer,
                               **common_args)(inputs)
    x = tf.keras.layers.Conv2D(filters=n_filter,
                               kernel_size=3,
                               strides=1,
                               padding='same',
                               activation='relu',
                               kernel_regularizer=regularizer,
                               **common_args)(x)
    x = tf.keras.layers.Conv2D(filters=n_filter,
                               kernel_size=3,
                               strides=1,
                               padding='same',
                               activation='relu',
                               kernel_regularizer=regularizer,
                               **common_args)(x)
    x = tf.keras.layers.MaxPooling2D((2, 2))(x)
    return x


def dense_block(inputs, n_filter, regularizer, drop_rate, common_args):
    x = tf.keras.layers.Dense(16 * n_filter,
                              activation='relu',
                              kernel_regularizer=regularizer,
                              **common_args)(inputs)
    x = tf.keras.layers.Dropout(drop_rate)(x)
    x = tf.keras.layers.Dense(16 * n_filter, activation='relu',
                              kernel_regularizer=regularizer,
                              **common_args)(x)
    x = tf.keras.layers.Dropout(drop_rate)(x)
    x = tf.keras.layers.Dense(8 * n_filter, activation='relu',
                              kernel_regularizer=regularizer,
                              **common_args)(x)
    x = tf.keras.layers.Dropout(drop_rate)(x)
    return x


def make_level_model(img_size, n_bands, l2, nf, dr, with_feature):
    regularizer = tf.keras.regularizers.l2(l2)
    initializer = tf.keras.initializers.glorot_normal()
    common_args = {"kernel_initializer": initializer}

    inputs = tf.keras.layers.Input(shape=(img_size, img_size, n_bands))
    x = conv_block(inputs, nf, regularizer, common_args)
    x = conv_block(x, nf * 2, regularizer, common_args)
    x = conv_block(x, nf * 4, regularizer, common_args)

    x = tf.keras.layers.Flatten()(x)
    if with_feature:
        inputs_features = tf.keras.Input(shape=(34,))
        x = tf.keras.layers.concatenate([x, inputs_features])
        x = dense_block(x, nf, regularizer, dr, common_args)
        output = tf.keras.layers.Dense(1, **common_args)(x)
        model = tf.keras.Model([inputs, inputs_features], output)
        return model
    x = dense_block(x, nf, regularizer, dr, common_args)
    output = tf.keras.layers.Dense(1, **common_args)(x)

    model = tf.keras.Model(inputs=inputs, outputs=output)
    return model


def make_diff_model(img_size, n_bands, l2, nf, dr, with_feature, model):
    regularizer = tf.keras.regularizers.l2(l2)
    initializer = tf.keras.initializers.glorot_normal()
    common_args = {"kernel_initializer": initializer}

    inputs1 = tf.keras.layers.Input(shape=(img_size, img_size, n_bands))
    inputs2 = tf.keras.layers.Input(shape=(img_size, img_size, n_bands))

    if with_feature:
        inputs_features = tf.keras.Input(shape=(34,))
        level_model = tf.keras.Model(model.input, outputs=model.get_layer('concatenate').output)
        x1 = level_model((inputs1, inputs_features))
        x2 = level_model((inputs2, inputs_features))
        x1 = tf.keras.layers.Flatten()(x1)
        x2 = tf.keras.layers.Flatten()(x2)
        x = tf.keras.layers.Concatenate()([x1, x2])
        x = dense_block(x, nf, regularizer, dr, common_args)
        output = tf.keras.layers.Dense(1, **common_args)(x)
        diff_model = tf.keras.Model([inputs1, inputs2, inputs_features], outputs=output)
        return diff_model
    level_model = tf.keras.Model(model.input, outputs=model.get_layer('max_pooling2d_2').output)
    x1 = level_model(inputs1)
    x2 = level_model(inputs2)
    x1 = tf.keras.layers.Flatten()(x1)
    x2 = tf.keras.layers.Flatten()(x2)
    x = tf.keras.layers.Concatenate()([x1, x2])
    x = dense_block(x, nf, regularizer, dr, common_args)
    output = tf.keras.layers.Dense(1, **common_args)(x)
    diff_model = tf.keras.Model([inputs1, inputs2], outputs=output)
    return diff_model


def train_test_model(hparams, model, train_ds, valid_ds, test_ds, logdir, checkdir, epochs):
    l2 = hparams['l2']
    lr = hparams['lr']
    bs = hparams['bs']
    ds = hparams['ds']
    nf = hparams['nf']
    dr = hparams['dr']
    lr_schedule = tf.keras.optimizers.schedules.InverseTimeDecay(
        lr,
        decay_steps=int(ds_len(train_ds)) * ds,
        decay_rate=1,
        staircase=True)
    optimizer = tf.keras.optimizers.Adam(lr_schedule)
    model.compile(optimizer=optimizer, loss="mean_squared_error", metrics=[RSquare()])
    model.fit(
        train_ds,
        epochs=epochs,
        validation_data=valid_ds,
        callbacks=[tf.keras.callbacks.TensorBoard(logdir + '/fit/{}_{}_{}_{}_{}_{}'.format(lr, l2, bs, ds, nf, dr),
                                                  # profile_batch='4, 8'
                                                  ),
                   tf.keras.callbacks.ModelCheckpoint(
                       filepath=checkdir + '/{}_{}_{}_{}_{}_{}'.format(lr, l2, bs, ds, nf, dr),
                       monitor='val_r_square', mode='max', save_weights_only=True, save_best_only=True),
                   tf.keras.callbacks.EarlyStopping(monitor='val_r_square', min_delta=0, patience=epochs // 4,
                                                    mode='max')]
    )
    model.load_weights(checkdir + '/{}_{}_{}_{}_{}_{}'.format(lr, l2, bs, ds, nf, dr))
    _, valid_accuracy = model.evaluate(valid_ds)
    _, test_accuracy = model.evaluate(test_ds)
    return valid_accuracy, test_accuracy


def run(run_dir, hparams, model, train_ds, valid_ds, test_ds, logdir, checkdir, epochs):
    with tf.summary.create_file_writer(run_dir).as_default():
        hp.hparams(hparams)
        valid_accuracy, test_accuracy = train_test_model(hparams, model, train_ds,
                                                         valid_ds, test_ds, logdir,
                                                         checkdir, epochs)
        tf.summary.scalar('valid_r_square', valid_accuracy, step=1)
        tf.summary.scalar('test_r_square', test_accuracy, step=1)
