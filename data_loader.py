import gzip
import struct

import numpy as np

np.set_printoptions(np.inf)


def load_images(data_file):
    with gzip.open(data_file, 'rb') as f:
        buffers = f.read()
        head = struct.unpack_from('>iiii', buffers, 0)
        magic = head[0]
        if magic != 2051:
            return None
        total = head[1]
        width = head[2]
        height = head[3]
        bits_size = width * height * total
        fmt = ">{}B".format(bits_size)
        bits = struct.unpack_from(fmt, buffers, 16)
        images = np.reshape(np.array(bits), (total, width, height))
        return images


def load_labels(data_file):
    with gzip.open(data_file, 'rb') as f:
        buffers = f.read()
        head = struct.unpack_from('>ii', buffers, 0)
        magic = head[0]
        if magic != 2049:
            return None
        total = head[1]
        fmt = '>{}B'.format(total)
        bits = struct.unpack_from(fmt, buffers, 8)
        labels = np.reshape(np.array(bits), (total, 1))
        return labels


images = load_images('data/train-images-idx3-ubyte.gz')
labels = load_labels('data/train-labels-idx1-ubyte.gz')
print(labels)
