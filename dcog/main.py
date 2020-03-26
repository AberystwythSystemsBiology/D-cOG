import os
from data import DataPrepper


# Load the data and export it to a means suited for DL.
eggnog_proteins_fp = "/home/keo7/Data/dcog/e5.proteomes_smol.faa"
nog_annotations_fp = "/home/keo7/Data/dcog/e5.og_annotations.tsv"
sequence_aliases_fp = "/home/keo7/Data/dcog/e5.sequence_aliases_v_smol.tsv"

ambig_dict = {
            "X": [x for x in "ACDEFGHIKLMNPQRSTVWY"],
            "B" : ["D", "N"],
            "Z" : ["E", "Q"],
            "J" : ["I", "L"]
        }

dp = DataPrepper(eggnog_proteins_fp, nog_annotations_fp, sequence_aliases_fp, 3, ambig_dict=ambig_dict)

