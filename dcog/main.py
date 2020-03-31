import os, json
from data import DataPrepper, DataGenerator
from deeplearning import Model
import logging
from sklearn.model_selection import KFold, train_test_split
import numpy as np
import random

logging.basicConfig(level=logging.INFO)

# Load the data and export it to a means suited for DL.
eggnog_proteins_dir = "/home/keo7/Data/dcog/sequence"
protein_id_conversion = "/home/keo7/Data/dcog/all_OG_annotations.tsv"


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


ambig_dict = {
    "X": [x for x in "ACDEFGHIKLMNPQRSTVWY"],
    "B": ["D", "N"],
    "Z": ["E", "Q"],
    "J": ["I", "L"],
    "*": [x for x in "ACDEFGHIKLMNPQRSTVWY"]
}

out_dir = "/home/keo7/Data/dcog/test_output/"
sequences_dir = os.path.join(out_dir, "sequences")
ngram_dict_fp = os.path.join(out_dir, "ngram_dict.json")


encoded_labels = {a: i for i, a in enumerate(nogs.keys())}

with open(ngram_dict_fp, "r") as infile:
    ngrams_dict = json.load(infile)

filepaths = np.array([os.path.join(sequences_dir, x) for x in os.listdir(sequences_dir)])
random.shuffle(filepaths)

kf = KFold(n_splits=10)
for k, (train_index, test_index) in enumerate(kf.split(filepaths)):

    training_fps = filepaths[train_index]
    training_fps, val_fps = train_test_split(training_fps, test_size=0.2)
    test_fps = filepaths[test_index]

    train_dg = DataGenerator(training_fps, encoded_labels, 130, batch_size=32, mp=False)
    val_dg = DataGenerator(training_fps, encoded_labels, 130, batch_size=32, mp=False)
    test_dg = DataGenerator(test_fps, encoded_labels, 130, batch_size=32, mp=False)

    output_dir = "/tmp/dcog/k_fold_%i/" % (k)

    clf = Model(ngrams_dict, nogs, output_dir)
    clf.train(train_dg, val_dg, epochs=500)
    clf.evaluate(test_dg, encoded_labels)