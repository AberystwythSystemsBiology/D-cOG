import os
from data import DataPrepper
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

'''
dp = DataPrepper(eggnog_proteins_dir, protein_id_conversion, 3, ambig_dict=ambig_dict,)
dp.process(out_dir)
dp.export(out_dir)
'''

