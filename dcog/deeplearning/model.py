from keras.models import Sequential, load_model
from keras.layers import Dense, Embedding
from keras.layers import LSTM
from keras.callbacks import ModelCheckpoint, EarlyStopping, CSVLogger
import os, json
import matplotlib.pyplot as plt
import csv
from sklearn.metrics import classification_report, roc_auc_score

class Model:
    def __init__(self, ngrams_dict: dict, nogs: dict, output_dir: str="/tmp/dcog_model"):
        
        self.nogs = nogs
        self.output_dir = output_dir

        self._prepare_output()
        self.clf = self._generate_model(ngrams_dict)

    
    def _prepare_output(self) -> None:


        if not os.path.isdir(self.output_dir):
            os.mkdir(self.output_dir)

        self.checkpoint_fp = os.path.join(self.output_dir, "model_checkpoint")
        self.log_fp = os.path.join(self.output_dir, "training.csv")


    @property
    def num_outputs(self) -> int:
        return len(self.nogs.keys())


    def _generate_model(self, ngrams_dict: dict) -> Sequential:

        def __get_max_features(ngrams_dict: dict) -> None:
            self.max_features = max(ngrams_dict.items())[1] + 1

        
        def __export_model(clf) -> None:
            with open(os.path.join(self.output_dir, "model.json"), "w") as json_file:
                json.dump(clf.to_json(), json_file, indent=4)

        __get_max_features(ngrams_dict)

        clf = Sequential()
        clf.add(Embedding(self.max_features, 128))
        clf.add(LSTM(128, dropout=0.2, recurrent_dropout=0.2))
        clf.add(Dense(self.num_outputs, activation='softmax'))

        clf.compile(loss='sparse_categorical_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])

        __export_model(clf)

        return clf

    
    def train(self, train_generator, validation_data = None, epochs: int=5, validation_split: float=0.2, shuffle:bool = False):


        mc = ModelCheckpoint(self.checkpoint_fp, save_best_only=True)
        es = EarlyStopping(patience=100, restore_best_weights=True)
        cl = CSVLogger(self.log_fp)


        self.clf.fit(train_generator, validation_data=validation_data, epochs=epochs, shuffle=shuffle, callbacks=[mc, es, cl])

        # Load best model.
        self.clf = load_model(self.checkpoint_fp)

        self._plot_training()



    def evaluate(self, test_generator, encoded_labels):

        def _invert_dict(encoded_labels: dict) -> dict:
            return {v: k for k, v in encoded_labels.items()}

        enc_labels = _invert_dict(encoded_labels)

        pred_prob = self.clf.predict(test_generator)
        y_pred = pred_prob.argmax(axis=-1)

        y_true = []

        for X, y in test_generator:
            y_true.extend(y.tolist())

        print(classification_report([enc_labels[x] for x in y_true], [enc_labels[x] for x in y_pred]))


    
    def _plot_training(self):
        
        train_loss = []
        val_loss = []

        with open(self.log_fp, "r") as infile:
            infile.readline()
            

            csv_reader = csv.reader(infile, delimiter=",")
            for row in csv_reader:
                train_loss.append(float(row[1]))
                val_loss.append(float(row[-1]))
                
        plt.figure()
        plt.plot(range(len(train_loss)), train_loss, label="Training Loss")
        plt.plot(range(len(val_loss)), val_loss, label="Validation Loss")
        plt.legend(loc="upper right")
        plt.xlabel("Epochs")
        plt.ylabel("Loss")
        plt.tight_layout()
        plt.savefig("%s/training_history.pdf" % (self.output_dir))