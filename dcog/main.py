import os
from data import DataPrepper
import logging

logging.basicConfig(level=logging.INFO)

# Load the data and export it to a means suited for DL.
eggnog_proteins_dir = "/home/keo7/Data/dcog/sequences"
nog_annotations_fp = "/home/keo7/Data/dcog/e5.og_annotations.tsv"
sequence_aliases_fp = "/home/keo7/Data/dcog/e5.sequence_aliases_v_smol.tsv"

ambig_dict = {
    "X": [x for x in "ACDEFGHIKLMNPQRSTVWY"],
    "B": ["D", "N"],
    "Z": ["E", "Q"],
    "J": ["I", "L"],
}

dp = DataPrepper(
    eggnog_proteins_dir,
    nog_annotations_fp,
    sequence_aliases_fp,
    1,
    ambig_dict=ambig_dict,
)

dp.process()
