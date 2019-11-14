from nltk import ngrams

class DataPrepper:
    def __init__(self,
                eggnog_proteins_fp:str,
                nog_annotations_fp:str,
                ngrams:int=1,
                vocab:str="ATGE"
                ):
        
        self.ngrams = ngrams
        self.vocab = [x for x in vocab]

        self.ngram_dict = self._generate_ngram_dict()

    def _generate_ngram_dict(self) -> dict:
        return {"".join(x) : i for i, x in enumerate(ngrams(self.vocab, self.ngrams))}

    def to_csv() -> None:
        pass

if __name__ == "__main__":
    dp = DataPrepper()
    print(dp.ngram_dict)