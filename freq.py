import random
import string
# from wikipedia
FREQS = {"A": 11.7 / 100,


         "B": 4.4 / 100,


         "C": 5.2 / 100,


         "D": 3.2 / 100,


         "E": 2.8 / 100,


         "F": 4 / 100,


         "G": 1.6 / 100,


         "H": 4.2 / 100,


         "I": 7.3 / 100,


         "J": 0.51 / 100,


         "K": 0.86 / 100,


         "L": 2.4 / 100,


         "M": 3.8 / 100,


         "N": 2.3 / 100,


         "O": 7.6 / 100,


         "P": 4.3 / 100,


         "Q": 0.22 / 100,


         "R": 2.8 / 100,


         "S": 6.7 / 100,


         "T": 16 / 100,


         "U": 1.2 / 100,


         "V": 0.82 / 100,


         "W": 5.5 / 100,


         "X": 0.045 / 100,


         "Y": 0.76 / 100,


         "Z": 0.045 / 100
         }


def natural_dist():
    letters, freqs = zip(*FREQS.items())
    return random.choices(
        letters, weights=freqs, k=1
    )[0]


def even_dist():
    return random.choice(string.ascii_uppercase)


get_letter = natural_dist

if __name__ == "__main__":
    print(get_letter())
