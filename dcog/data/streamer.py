from keras.utils import Sequence
from keras.preprocessing.sequence import pad_sequences
import numpy as np

class DataGenerator(Sequence):

    def __init__(self, data_dir: str, encoding_dict: dict, encoded_labels: dict, max_length: int, batch_size: int=32, shuffle: bool=True):
        self.data_dir = data_dir
        self.encoding_dict = encoding_dict
        self.encoded_labels = encoded_labels
        self.max_length = max_length
        self.batch_size = batch_size
        self.shuffle = shuffle


    def __len__(self):
        return int(np.floor(len(self.filepaths) / self.batch_size))