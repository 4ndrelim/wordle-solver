# An algorithm to solve wordle challenges
# A naive algorithm and one with a smarter guess function

# Libraries
import random
from collections import defaultdict

def generate_random_guess_word(possible_words):
    '''
    Generates a random word from the list of possible words.

    Parameters
    ----------
    possible_words:
        A list of strings of all possible remaining words in the word list.
    
    Returns
    -------
        A random string from possible_words.
    '''
    return random.choice(possible_words)


def filter_available_words(guess_word, colours, possible_words):
    '''
    Filters the list of possible words after making a guess.
    algorithm below accounts for repeats 
    (accordance with conventional wordle rules & how colouring is handled for repeats)

    Parameters
    ----------
    guess_word:
        A string of the guess word.
    colours:
        A string representation of the colours of the result of the guess word.
    possible_words:
        A list of strings of all possible remaining words in the word list before this guess.
    
    Returns
    -------
        A list of possible words after making this guess.
    '''
    guess_word = guess_word.lower()
    # return list of plausible words after filtering; 
    ret = []
    
    # 1. make sure elements marked G are present and in the correct place of the possible word
    #    a. encoded in a dictionary - key is index/position, value is letter
    check_green = {}
    
    # 2. make sure elements marked Y or B will not appear in these position in the possible word
    #    a. dictionary encoding
    avoid_yellow_black_spots = {}
    
    # 3. make sure elements marked Y have their counts collated and met in the possible word
    #    a. dictionary where index is the letter and value is the count
    count_char_yellow = defaultdict(lambda: 0)
    
    # 4. after counting letters in a plausible word, and accounting for (3), make sure no excess elements marked B are present
    #    a. just define a set to check presence
    check_black = set()
    
    for i in range(len(guess_word)):
        char = guess_word[i]
        if colours[i] == 'G':
            check_green[i] = char
        elif colours[i] == 'Y':
            avoid_yellow_black_spots[i] = char
            count_char_yellow[char] += 1
        else:
            check_black.add(char)
            avoid_yellow_black_spots[i] = char
  
    for word in possible_words:
        word = word.lower() 
        if len(word) != len(guess_word):
            continue
        count_char = defaultdict(lambda: 0)
        possible = True
        for i, char in enumerate(word):
            if i in check_green:
                if char != check_green[i]:
                    possible = False
                    break
            else:
                if i in avoid_yellow_black_spots:
                    if char == avoid_yellow_black_spots[i]:
                        possible = False
                        break
            
                count_char[char] += 1
                
        for char in count_char_yellow:
            count_char[char] -= count_char_yellow[char]
        for char in count_char:
            if count_char[char] < 0 or (count_char[char] > 0 and char in check_black):
                possible = False
                break
        if possible:
            ret.append(word)
    return ret
