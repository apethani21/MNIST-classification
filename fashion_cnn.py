import sys
import pickle
import logging
import tensorflow as tf
import tensorflow_datasets as tfds


def get_data():
    dataset, metadata = tfds.load('fashion_mnist',
                                  as_supervised=True,
                                  with_info=True)
    train_dataset, test_dataset = dataset['train'], dataset['test']
    return train_dataset, test_dataset, metadata


def normalise(images, labels):
    images = tf.cast(images, tf.float32)
    images /= 255
    return images, labels


def train(model_name, batch_size=32, epochs=15):
    model = getattr(__import__('models'), model_name)()
    print(model.summary())
    train_dataset, test_dataset, metadata = get_data()
    num_train_examples = metadata.splits['train'].num_examples
    train_dataset = (train_dataset
                     .map(normalise)
                     .repeat()
                     .shuffle(num_train_examples)
                     .batch(batch_size))
    test_dataset = (test_dataset
                    .map(normalise)
                    .batch(batch_size))
    print("Data prepared")
    model_checkpoint = (tf
                        .keras
                        .callbacks
                        .ModelCheckpoint('./config/fashion_cnn.h5',
                                         verbose=True))
    steps = int((num_train_examples/batch_size) + 1)
    history = model.fit(x=train_dataset,
                        epochs=epochs,
                        steps_per_epoch=steps,
                        callbacks=[model_checkpoint])
    model.save('./config/fashion_cnn.h5')
    return history, steps, test_dataset


def evaluate_model(model, steps, test_dataset):
    acc = model.evaluate(test_dataset, steps=steps)
    print('Accuracy: ', acc)


def compute(model, *args):
    (history,
     steps,
     test_dataset) = train(model, batch_size=64, epochs=10, *args)
    with open('./config/history', 'wb') as f:
        pickle.dump(history.history, f)
    evaluate_model(model, steps, test_dataset)


if __name__ == "__main__":
    arg = sys.argv[1]
    model_name = arg.split('=')[-1]
    logger = tf.get_logger()
    logger.setLevel(logging.ERROR)
    compute(model_name)
