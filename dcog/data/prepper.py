import itertools
import csv
from Bio import SeqIO
import logging
import textwrap
import os
import sys
import json

csv.field_size_limit(sys.maxsize)

from multiprocessing import Pool


class DataPrepper:
    def __init__(
        self,
        eggnog_proteins_dir: str,
        protein_id_conversion: str,
        ngrams: int = 1,
        vocab: str = "ACDEFGHIKLMNPQRSTVWYUOx",
        ambig_dict: dict = {},
    ):

        self.eggnog_proteins_dir = eggnog_proteins_dir
        self.protein_id_conversion = protein_id_conversion

        self.ngrams = ngrams

        self.vocab = [x for x in vocab]
        self.ambig_dict = self._generate_ambig_probabilities(ambig_dict)

        self.ngram_dict = self._generate_ngram_dict()

        self.nog_annots = self._load_annots()

        self.is_processed = False

    def _generate_ambig_probabilities(self, ambig_dict: dict) -> dict:
        def __generate_probabilities_table() -> dict:
            return {aa: 0 for aa in self.vocab}

        probabilities_dict = {}

        for aa in self.vocab:
            _p = __generate_probabilities_table()
            _p[aa] = 1.0

            probabilities_dict[aa] = list(_p.values())

        for aa in ambig_dict:
            _p = __generate_probabilities_table()

            calc_prob = 1 / len(ambig_dict[aa])

            for prob in ambig_dict[aa]:
                _p[prob] = calc_prob

            probabilities_dict[aa] = list(_p.values())

        return probabilities_dict

    def _generate_labels(self) -> dict:
        logging.info(">>> Loading in aliases file.")

        alias_dict = {}
        with open(self.sequence_aliases_fp, "r") as infile:
            csv_reader = csv.reader(infile, delimiter="\t")
            for row in csv_reader:
                if row[2] == "Ensembl_UniProt":
                    alias_dict[row[0]] = row[1]

        logging.info(">>> ✅ Aliases file loaded.")

        return alias_dict

    def _load_annots(self) -> dict:
        logging.info(">>> Loading in annotation file.")

        nog_annots = {}
        with open(self.protein_id_conversion, "r") as infile:
            csv_reader = csv.reader(infile, delimiter="\t")

            for row in csv_reader:
                _anot = []

                # MIGHT NEED TO CHECK FOR U ON ITS OWN
                for s in row[4]:
                    if s not in [x for x in "[,u,],'"]:
                        _anot.append(s)

                _seq_id = row[-1]

                for sequence in _seq_id.split(","):
                    if _seq_id not in nog_annots:
                        nog_annots[sequence] = []
                    nog_annots[sequence].extend(_anot)

        logging.info(">>> ✅ Annotation file loaded.")
        return nog_annots

    def _generate_ngram_dict(self) -> dict:
        logging.info(">>> Generating ngram dictonary file.")

        d = {}

        vocab = self.vocab + list(self.ambig_dict.keys())

        for i in range(self.ngrams + 1):
            if len(d.values()) == 0:
                _mv = 0
            else:
                _mv = max(d.values())

            _i_d = {
                "".join(x): i + _mv
                for i, x in enumerate(itertools.product(vocab, repeat=i))
            }

            d.update(_i_d)

        logging.info(">>> ✅ ngram dictionary created.")

        return d

    def load_fasta(self, fp) -> list:
        return SeqIO.parse(fp, "fasta")

    def _process_data(self, fp: str) -> None:

        fp, out_dir = fp

        output = {}

        for index, seq in enumerate(SeqIO.parse(fp, "fasta")):
            id = seq.id
            try:
                annotations = self.nog_annots[id]
                process = True

            except KeyError:
                process = False

            if process:
                sequence_str = str(seq.seq)

                ngrams = [
                    self.ngram_dict[x] for x in textwrap.wrap(sequence_str, self.ngrams)
                ]

                p_table = [self.ambig_dict[x] for x in sequence_str]

                output[id] = {
                    "COG": annotations,
                    "ngrammed_sequence": ngrams,
                    # "probability_table": p_table,
                }

        bfn = os.path.basename(fp)
        woe = os.path.splitext(bfn)[0] + ".json"

        sequences_out_dir = os.path.join(out_dir, "sequences")

        if not os.path.isdir(sequences_out_dir):
            os.mkdir(sequences_out_dir)

        with open(os.path.join(sequences_out_dir, woe), "w") as outfile:
            json.dump(output, outfile, indent=4)

        return None

    def process(self, out_dir: str) -> None:

        logging.info(">>> Processing data.")

        fps = [
            [os.path.join(self.eggnog_proteins_dir, x), out_dir]
            for x in os.listdir(self.eggnog_proteins_dir)
        ]

        #p = Pool(None)
        #p.map(self._process_data, fps[0])

        self._process_data(fps[0])

        self.is_processed = True

    def export(self, out_dir) -> None:
        if self.is_processed:
            with open(os.path.join(out_dir, "ngram_dict.json"), "w") as outfile:
                json.dump(self.ngram_dict, outfile, indent=4)
        else:
            print("Please apply run process on this class before exporting")
