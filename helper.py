from difflib import SequenceMatcher
import nltk
from nltk.translate import bleu
from nltk.translate.bleu_score import SmoothingFunction
smoothie = SmoothingFunction().method4

# C1='GZEELE English Laptop keyboard for HP EliteBook Folio 9470M 9470 9480 9480M 702843-001 US Replace Keyboard Silver'
# C2='PT-BR Brasil Keyboard for Compaq Presario CQ-25 CQ-27 CQ-29 Notebook Keyboard Brazil Portuguese MB27716023 MB3661022 MB3181014'

# print('BLEUscore:', bleu([C1], C2, smoothing_function=smoothie))

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def bleu_score(a, b):
    return bleu([a], b, smoothing_function=smoothie)

def mean(items):
    return sum(items) / len(items)

def isLinkValid(link):
    if 'https://' not in link:
        return False
    elif 'aliexpress.com/item/' not in link:
        return False
    
    return True

# print(similar(C1,C2))