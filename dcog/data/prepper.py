import itertools
import csv
from Bio import SeqIO
import logging
import textwrap

class DataPrepper:
    def __init__(self,
                eggnog_proteins_dir:str,
                nog_annotations_fp:str,
                sequence_aliases_fp:str,
                ngrams:int=1,
                vocab:str="ACDEFGHIKLMNPQRSTVWYUOx",
                ambig_dict:dict = {}
                ):

        self.vocab = [x for x in vocab]
        self.ambig_dict = self._generate_ambig_probabilities(ambig_dict)

        self.eggnog_proteins_dir = eggnog_proteins_dir

        self.nog_annotations_fp = nog_annotations_fp
        self.sequence_aliases_fp = sequence_aliases_fp

        self.ngrams = ngrams

        self.nog_annots = self._load_annots()

        self.ngram_dict = self._generate_ngram_dict()
        self.alias_dict = self._generate_aliases_dict()

        self.is_processed = False

    def _generate_ambig_probabilities(self, ambig_dict: dict) -> dict:

        def __generate_probabilities_table() -> dict:
            return {aa : 0  for aa in self.vocab}

        probabilities_dict = {}

        for aa in self.vocab:
            _p = __generate_probabilities_table()
            _p[aa] = 1.0

            probabilities_dict[aa] = list(_p.values())

        for aa in ambig_dict:
            _p = __generate_probabilities_table()

            calc_prob = (1 / len(ambig_dict[aa]))

            for prob in ambig_dict[aa]:
                _p[prob] = calc_prob

            probabilities_dict[aa] = list(_p.values())

        return probabilities_dict

    def _generate_aliases_dict(self) -> dict:
        logging.info(">>> Loading in aliases file.")

        alias_dict = {}
        with open(self.sequence_aliases_fp, "r") as infile:
            csv_reader = csv.reader(infile, delimiter="\t")
            for row in csv_reader:
                alias_dict[row[0]] = row[1]

        logging.info(">>> ✅ Aliases file loaded.")

        return alias_dict

    def _load_annots(self) -> dict:
        logging.info(">>> Loading in annotation file.")

        nog_annots = {}
        with open(self.nog_annotations_fp, "r") as infile:
            csv_reader = csv.reader(infile, delimiter="\t")

            for row in csv_reader:
                _, anot, nog_anot, _ = row
                nog_annots[anot] = nog_anot

        logging.info(">>> ✅ Annotation file loaded.")
        return nog_annots

    @property
    def proteome(self) -> list:
        return SeqIO.parse(self.eggnog_proteins_fp, "fasta")

    def _generate_ngram_dict(self) -> dict:
        logging.info(">>> Loading in annotation file.")

        d = {}

        vocab = self.vocab + list(self.ambig_dict.keys())

        for i in range(self.ngrams+1):
            if len(d.values()) == 0:
                _mv = 0
            else:
                _mv = max(d.values())

            _i_d = {"".join(x) : i+_mv for i, x in enumerate(itertools.product(vocab, repeat=i))}

            d.update(_i_d)
        return d


    def process(self) -> None:

        def _ngram(seq: str) -> list:
            return [self.ngram_dict[x] for x in textwrap.wrap(str(seq), self.ngrams)]

        logging.info(">>> Processing data.")

        for seq in self.proteome:
            ng_seq = _ngram(seq.seq)

        self.is_processed = True

    def export(self) -> None:
        if self.is_processed:
            pass
        else:
            print("Please apply run process on this class before exporting")

