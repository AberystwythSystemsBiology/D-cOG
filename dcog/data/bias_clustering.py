import csv
from Bio import SeqIO
import logging
import os
import sys

# Temporary fix for field_size_limit.
csv.field_size_limit(sys.maxsize)


eggnog_proteins = "./eggnogv4.proteins.all.fa"
annotations = "./all_OG_annotations.tsv"


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



def _load_annots(protein_id_conversion):
    logging.info(">>> Loading in annotation file.")

    nog_annots = {}
    with open(protein_id_conversion, "r") as infile:
        csv_reader = csv.reader(infile, delimiter="\t")

        for row in csv_reader:
            _anot = []

            # MIGHT NEED TO CHECK FOR U ON ITS OWN
            #Check if its a nac nog
            if 'bacNOG' in row[1]:
                for s in row[4]:
                    if s not in [x for x in "[,u,],'"]:
                        _anot.append(s)

                _seq_id = row[-1]

                for sequence in _seq_id.split(","):
                    if _seq_id not in nog_annots:
                        nog_annots[sequence] = []
                    else:
                        print(nog_annots[sequence])
                        print("Wa")
                    nog_annots[sequence].extend(_anot)


    logging.info(">>> ✅ Annotation file loaded.")
    return nog_annots




def _process_data(seqs,out_dir,nog_annots) -> None:



    process = False
    for index, seq in enumerate(SeqIO.parse(seqs, "fasta")):
        #print(seq)
        id = seq.id


        try:
            annotations = nog_annots[id]
            process = True
            annots = ''
            if len(annotations) >1:

                for a in annotations:
                    if a in nogs.keys():
                        annots += ('_'+str(a))
            else:
                annots = '_'+annotations[0]

            output = '>'+str(id)+str(annots)+'\n'+str(seq.seq)+'\n'
            print(output)
            with open(str(out_dir)+"/bacNOG_seqs.fasta" , "a") as outfile:
                outfile.write(output)



        except KeyError:
            process = False




    return None

def process(self, out_dir: str) -> None:

    logging.info(">>> Processing data.")

    sequences_out_dir = os.path.join(out_dir, "sequences")

    if not os.path.isdir(sequences_out_dir):
        os.mkdir(sequences_out_dir)

    fps = [
        [os.path.join(self.eggnog_proteins_dir, x), sequences_out_dir]
        for x in os.listdir(self.eggnog_proteins_dir)
    ]



    #p = Pool(None)
    #p.map(self._process_data, fps[0])

    self._process_data(fps[0])

    self.is_processed = True


nog_annots = _load_annots(annotations)

_process_data(eggnog_proteins,'./out',nog_annots)