from nltk.corpus import wordnet as wn
import random

class Generator:
    def generate_username():
        length1 =  len(list(wn.all_synsets('a')))
        length2 =  len(list(wn.all_synsets('n')))

        adj = list(wn.all_synsets('a'))[random.randint(0, length1)].lemmas()[0].name()
        noun = list(wn.all_synsets('n'))[random.randint(0, length2)].lemmas()[0].name()

        return (adj + "-" +  noun)