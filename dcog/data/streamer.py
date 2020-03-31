from keras.utils import Sequence
from keras.preprocessing.sequence import pad_sequences
import numpy as np
import json

from multiprocessing import Pool

class DataGenerator(Sequence):

    def __init__(self, filepaths: str, encoded_labels: dict, max_length: int, batch_size: int=32, shuffle: bool=True, mp: bool=True):
        self.filepaths = np.array(filepaths)
        self.encoded_labels = encoded_labels
        self.max_length = max_length
        self.batch_size = batch_size
        self.shuffle = shuffle

        self.mp = mp

        self.on_epoch_end()

    def __len__(self) -> int:
        return int(np.floor(len(self.filepaths) / self.batch_size))

    def on_epoch_end(self):
        self.indexes = np.arange(len(self.filepaths))
        if self.shuffle is True:
            np.random.shuffle(self.indexes)

    def __getitem__(self, index):
        indexes = self.indexes[index * self.batch_size:self.batch_size * (index + 1)]

        file_paths_temp = [self.filepaths[k] for k in indexes]

        X, y = self.__data_generation(file_paths_temp)

        return X, y


    def _process_data(self, filepath):
        with open(filepath, "r") as infile:
            data = json.load(infile)
            seq = np.array(data["ngrammed_sequence"])
            con = self.encoded_labels[data["COG"][0]]

        return seq, con

    def __data_generation(self, file_paths_temp):

        if self.mp:
            p = Pool(None)
            d = p.map(self._process_data, file_paths_temp)
        
        else:
            d = [self._process_data(x) for x in file_paths_temp]
        
        X, y = [x[0] for x in d], [x[1] for x in d]

        X = pad_sequences(np.array(X), self.max_length)

        return X, np.array(y)
