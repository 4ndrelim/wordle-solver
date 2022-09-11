# An algorithm to solve wordle challenges
# A naive algorithm and one with a smarter guess function

# Libraries
import random
from collections import defaultdict

# get all dictionary of words
word_dictionary = None
with open('dictionary.txt', 'r') as f:
    word_dictionary = f.read().split()



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
    rules: https://wordfinder.yourdictionary.com/blog/can-letters-repeat-in-wordle-a-closer-look-at-the-rules/

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
##    guess_word = guess_word.lower() # uncomment this if guess_word not of consistent case
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
##        word = word.lower() # uncomment this if words in possible_words not of consistent case
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



def make_evaluate_guess(word, word_list):
    '''
    evaluates the guess word against the actual word
    
    Parameters
    ----------
    word_list:
        list of all possible words
    word:
        the actual word
    Returns
    -------
        A list of possible words after making this guess.
    '''
    def evaluate_guess(guess_word):
        '''
        evaluate_guess is a function that runs the Wordle-game logic
        i.e takes in a guess word as input and returns the colour sequence as a string
        '''
        if guess_word not in word_list:
            raise Exception("Guess word not in word list")
        word_length = len(word)
        if len(guess_word) != word_length:
            raise Exception("Guess word not of correct length")

        result = ['B']*word_length
        word_l = list(word)
        ignore_index = []
        for i in range(word_length):
            if i in ignore_index:
                continue
            if guess_word[i] == word_l[i]:
                result[i] = 'G'
                word_l[i] = '-'
                ignore_index.append(i)
        for i in range(word_length):
            if i in ignore_index:
                continue
            for j in range(word_length):
                if guess_word[i] == word_l[j]:
                    result[i] = 'Y'
                    word_l[j] = '-'
                    break
        return ''.join(result)
    return evaluate_guess

def solver(word_list, evaluate_guess_func):
    '''
    Solves the wordle game, getting the hidden word.

    Parameters
    ----------
    word_list:
        A list of strings of all words in the word list.
        
    evaluate_guess_func:
        takes in a guess as input and returns a colour sequence as a string

        Parameters
        ----------
        guess_word:
            A string of the word to guess.

        Returns
        -------
            A string representation of the colours of the result of the guess word.
    
    Returns
    -------
        A string of the hidden word of evaluate_guess_func.
    '''
  
    curr = word_list 
    while (len(curr) > 1):
        guess = generate_random_guess_word(curr)
        score = evaluate_guess_func(guess)
        curr = filter_available_words(guess, score, curr)
        
    if (len(curr) == 1):
        score = evaluate_guess_func(curr[0])
        if score == "G"*len(curr[0]):
            return curr[0]
    return "NOT POSSIBLE"



## BASIC TESTING (or observation..)
test_filter = filter_available_words("tests", "BGYBB", word_dictionary)
# print(test_filter)

''' Test cases for `solver` '''
game_one = make_evaluate_guess("anime", word_dictionary)
print(solver(word_dictionary, game_one)) # Should print 'anime'

game_two = make_evaluate_guess("abyss", word_dictionary)
print(solver(word_dictionary, game_two)) # Should print 'abyss'


game_not_pos = make_evaluate_guess("vosts", word_dictionary)
print(solver(word_dictionary, game_not_pos)) # Should print 'NOT POSSIBLE'






'''
Rattionale for smarter guess:
Want the AI to exploit what it knows but also explore the
impossible words that could possibly provide more information.

For e.g. suppose we have narrowed the letters down to
CHA_E
and within the possibility space, there still exists:
CHASE
CHAVE
CHAFE
CHAPE

Exploitation would require you to iterate and check each letter whereas
guessing an alternative word like ANTSY would have given the remaining info
that the hidden word is CHASE

'''

def generate_smart_guess(word_list, possible_words, nth_guess):
    '''
    Generates a good guess word from the list of possible words.

    Parameters
    ----------
    word_list:
        A list of strings of all words in the word list.
    possible_words:
        A list of strings of all possible remaining words in the word list.
    nth_guess:
        A number indicating how many guesses have been made so far inclusive of this one.
    
    Returns
    -------
        A string of a good guess.
    '''
    
    # Inspiration: https://youtu.be/fVMlnSfGq0c 
    # Off of 3b1b except no log cost was computed, instead cost for a word is 
    # overall product, for each letter, 
    # squared difference of the frequency of the letter in that pos wrt to highest freq of any letter at that pos
    # intuitively, calculating 'similarity'
    
    size = len(word_list[0])
    
    freq_dict = defaultdict(lambda : [0 for i in range(size)]) # numbers represents no. letter appears in a 5-letter word
    
    for word in possible_words: # consider remaining words; similarity of a word with all rem. words
        word = word.lower()
        for i, letter in enumerate(word):
            freq_dict[letter][i] += 1
            
    max_freq = [0,0,0,0,0] # max freq for each position for every letter
    # get max freq
    for letter, counts in freq_dict.items():
        for i in range(size):
            if counts[i] > max_freq[i]:
                max_freq[i] = counts[i]
    
    # compute score for each word
    word_scores = {}
    for word in possible_words:
        score = 1
        for i in range(0,size):
            if (word[i] == 't'):
            score *= (1 + (freq_dict[word[i]][i] - max_freq[i])**2)
        word_scores[word] = score
    
    # return word with lowest score
    return min(word_scores, key = word_scores.get)


# Refer smarter guess function
def generate_smart_guess(word_list, possible_words, nth_guess):
    '''
    Generates a good guess word from the list of possible words.

    Parameters
    ----------
    word_list:
        A list of strings of all words in the word list.
    possible_words:
        A list of strings of all possible remaining words in the word list.
    nth_guess:
        A number indicating how many guesses have been made so far inclusive of this one.
    
    Returns
    -------
        A string of a good guess.
    '''
    
    # Inspiration: https://youtu.be/fVMlnSfGq0c 
    # Off of 3b1b except no log cost was computed, instead cost for a word is 
    # overall product, for each letter, 
    # squared difference of the frequency of the letter in that pos wrt to highest freq of any letter at that pos
    # intuitively, calculating 'similarity'

    if len(possible_words) == 1:
        return possible_words[0] # might as well return the last possible word
    
    size = len(word_list[0])
    
    freq_dict = defaultdict(lambda : [0 for i in range(size)]) # numbers represents no. letter appears in a 5-letter word
    
    for word in possible_words: # consider remaining words; similarity of a word with all rem. words
        word = word.lower()
        for i, letter in enumerate(word):
            freq_dict[letter][i] += 1
            
    max_freq = [0,0,0,0,0] # max freq for each position for every letter
    # get max freq
    for letter, counts in freq_dict.items():
        for i in range(size):
            if counts[i] > max_freq[i]:
                max_freq[i] = counts[i]
    
    # compute score for each word
    word_scores = {}
    for word in possible_words:
        score = 1
        for i in range(0,size):
            if (word[i] == 't'):
            score *= (1 + (freq_dict[word[i]][i] - max_freq[i])**2)
        word_scores[word] = score

    if random.random() < 0.3: # intuitively, after approx 3 tries of exploiting knowledge to make the best choice, make random choice
        impossible_words = set(word_list) - set(possible_words)
        return random.choice(list(impossible_words))
    
    # return word with lowest score
    return min(word_scores, key = word_scores.get)
