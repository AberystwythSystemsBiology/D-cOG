import os, json
from data import DataPrepper, DataGenerator
import logging

logging.basicConfig(level=logging.INFO)

# Load the data and export it to a means suited for DL.
eggnog_proteins_dir = "/home/keo7/Data/dcog/sequence"
protein_id_conversion = "/home/keo7/Data/dcog/all_OG_annotations.tsv"

ambig_dict = {
    "X": [x for x in "ACDEFGHIKLMNPQRSTVWY"],
    "B": ["D", "N"],
    "Z": ["E", "Q"],
    "J": ["I", "L"],
    "*": [x for x in "ACDEFGHIKLMNPQRSTVWY"]
}

out_dir = "/home/keo7/Data/dcog/test_output/"

dp = DataPrepper(eggnog_proteins_dir, protein_id_conversion, ngrams=3, ambig_dict=ambig_dict)
dp.process(out_dir)
dp.export(out_dir)

nogs = {
    "D": "Cell cycle control, cell division, chromosome partitioning",
    "M": "Cell wall/membrane/envelope biogenesis",
    "N": "Cell motility",
    "O": "Post-translational modification, protein turnover, and chaperones",
    "T": "Signal transduction mechanisms",
    "U": "Intracellular trafficking, secretion, and vesicular transport",
    "V": "Defense mechanisms",
    "W": "Extracellular structures",
    "Y": "Nuclear structure",
    "Z": "Cytoskeleton",
    "A": "RNA processing and modification",
    "B": "Chromatin structure and dynamics",
    "J": "Translation, ribosomal structure and biogenesis",
    "K": "Transcription",
    "L": "Replication, recombination and repair",
    "C": "Energy production and conversion",
    "E": "Amino acid transport and metabolism",
    "F": "Nucleotide transport and metabolism",
    "G": "Carbohydrate transport and metabolism",
    "H": "Coenzyme transport and metabolism",
    "I": "Lipid transport and metabolism",
    "P": "Inorganic ion transport and metabolism",
    "Q": "Secondary metabolites biosynthesis, transport, and catabolism",
    "R": "General function prediction only",
    "S": "Function unknown"
}

encoded_labels = {a: i for i, a in enumerate(nogs.keys())}

sequences_dir = os.path.join(out_dir, "sequences")
ngram_dict_fp = os.path.join(out_dir, "ngram_dict.json")

with open(ngram_dict_fp, "r") as infile:
    ngrams = json.load(infile)

max_features = max(ngrams.items())[1] + 1

filepaths = [os.path.join(sequences_dir, x) for x in os.listdir(sequences_dir)]

dg = DataGenerator(filepaths, encoded_labels, 100, batch_size=1024)

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Embedding
from tensorflow.keras.layers import LSTM

print(max_features)

model = Sequential()
model.add(Embedding(max_features, 128))
model.add(LSTM(128, dropout=0.2, recurrent_dropout=0.2))
model.add(Dense(len(nogs.keys()), activation='softmax'))

# try using different optimizers and different optimizer configs
model.compile(loss='sparse_categorical_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])

#model.fit_generator(dg)


for X, y in dg:
   model.fit(X, y, batch_size=64, epochs=10)
