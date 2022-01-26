text_relative_frequencies = {'a': 0.082, 'b': 0.015, 'c': 0.028, 'd': 0.043, 'e': 0.13, 'f': 0.022, 'g': 0.02,
                             'h': 0.061, 'i': 0.07, 'j': 0.0015, 'k': 0.0077, 'l': 0.04, 'm': 0.025, 'n': 0.067,
                             'o': 0.075, 'p': 0.019, 'q': 0.00095, 'r': 0.06, 's': 0.063, 't': 0.091, 'u': 0.028,
                             'v': 0.0098, 'w': 0.024, 'x': 0.0015, 'y': 0.02, 'z': 0.00074}

# Five letter dictionary file: https://eslforums.com/5-letter-words/
# Another list of common words, filtered to just the five letter words: http://sherwoodschool.ru/vocabulary/proficiency/
with open('common_five_letter_words.txt', 'r+') as f:
    common_word_list = f.read().replace(' ', '').split('\n')

# Starting with the third guess, rare letter bonus kicks into score. Based on dictionary frequencies.
rare_letter_bonus = {'a': 0.0, 'b': 0.05, 'c': 0.0, 'd': 0.0, 'e': 0.0, 'f': 0.05, 'g': 0.05,
                    'h': 0.05, 'i': 0.0, 'j': 0.15, 'k': 0.05, 'l': 0.0, 'm': 0.05, 'n': 0.0,
                    'o': 0.0, 'p': 0.05, 'q': 0.15, 'r': 0.0, 's': 0.0, 't': 0.0, 'u': 0.05,
                    'v': 0.10, 'w': 0.10, 'x': 0.15, 'y': 0.05, 'z': 0.15}


# Uses word file of all English words and produces word file of all five letter English words (lowercase)
def all_words_to_five_letter_words():
    with open('workspace.txt', 'r+') as f:
        data = f.read().replace(' ', '').split('\n')
        for i, word in enumerate(data):
            for letter in word:
                if letter in '1234567890&-\'./,' or len(word) != 5:
                    data[i] = ''
        data = [x.lower() for x in data if len(x) == 5]
        data = sorted(list(set(data)))
        with open('past_answers.txt', 'w+') as g:
            g.write('\n'.join(data))
    return


# Given the known information, is this word a valid potential word? Returns True/False
def potential_word(word, green, yellow, gray, next_guess_count):
    if next_guess_count < 3:  # Don't need to use green clues on the second guess
        for i, letter in enumerate(green):
            if word[i] in yellow[i] or word[i] in gray:
                return False
    else:  # Guess words that fit all known information
        for i, letter in enumerate(green):
            if (letter != '' and word[i] != letter) or word[i] in yellow[i] or word[i] in gray:
                return False

    for letter in ''.join(yellow):  # Letters in wrong spots must be present in the word though
        if letter not in word:
            return False
    return True


# Calculates the frequency score of a word based on the letters in the other valid words
# Only counts repeated letters once
def calculate_word_score(word, frequencies, next_guess_count):
    score = 0

    if next_guess_count < 3:
        letters = [x for i, x in enumerate(word) if word.index(x) == i]  # Remove duplicates if trying to max information
        score += sum(frequencies.get(x, 0) for x in letters)  # dictionary frequencies
        score += sum(text_relative_frequencies[x] for x in letters)  # text frequencies
    else:
        letters = [x for x in word]

    if word in common_word_list:  # common word bonus
        score += 0.5
    if word[4] == 's' and word[3] not in 'us':  # likely plural penalty
        score -= 0.3
    if next_guess_count >= 3:  # rare letter bonus
        score += 0.75 * sum(rare_letter_bonus[x] for x in letters)

    return score


# Takes a list of valid words and returns a sorted list of valid words based on letter-frequency of the original list
def order_by_score(valid_words, next_guess_count):
    frequencies = {}
    for word in valid_words:
        for letter in word:
            frequencies[letter] = frequencies.get(letter, 0) + 1
    total = sum(frequencies.values())
    for letter in frequencies.keys():
        frequencies[letter] /= total
    scored_list = [(word, calculate_word_score(word, frequencies, next_guess_count)) for word in valid_words]
    scored_list.sort(key=lambda x: x[1], reverse=True)
    return scored_list


# Takes known information, produces a list of valid words. Also produces frequencies of letters in remaining valid words
# and returns an ordered list of high letter-frequency words to help gather maximum information with future clues.
def wordle_helper(green, yellow, gray, next_guess_count):
    with open('all_five_letter_words.txt', 'r') as f:
        all_words = f.read().split('\n')
        valid_words = [word for word in all_words if potential_word(word, green, yellow, gray, next_guess_count)]
        return order_by_score(valid_words, next_guess_count)


# Given a word as the Wordle, simulates this program attempting to guess that word.
def simulate_word(word):
    guess_count = 1
    guesses = []
    green = ['', '', '', '', '']  # Green letters
    yellow = ['', '', '', '', '']  # Yellow letters
    gray = ''  # Gray letters
    recommended_guesses = wordle_helper(green, yellow, gray, guess_count)

    while len(recommended_guesses) > 0:
        guess = recommended_guesses[0][0]
        guesses.append(guess)
        if guess == word:
            print('Guesses: ', guesses)
            return
        else:
            guess_count += 1
            for i in range(len(guess)):
                if guess[i] == word[i]:
                    green[i] = guess[i]
                elif guess[i] in word and guess[i] not in yellow[i]:
                    yellow[i] += guess[i]
                else:
                    gray += guess[i]
        recommended_guesses = wordle_helper(green, yellow, gray, guess_count)

    print('error: ', word, guesses)
    exit(1)


# Takes current algorithm and calculates average number of guesses required in order to guess past Wordles
# Useful for benchmarking value-add of changes.
def calculate_average_guess_metric():
    with open('past_answers.txt', 'r+') as f:
        words = f.read().replace(' ', '').split('\n')
        print('Inputs: ', words)
        print('Average Num Guesses per Wordle: ', sum(len(simulate_word(word)) for word in words) / len(words))
        return


# simulate_word('apple')
# calculate_average_guess_metric()

'''
correct_spots = ['', '', '', '', '']  # Green letters
wrong_spots = ['a', 'a', 'c', 'a', '']  # Yellow letters
wrong_letters = 'rosepintdul'  # Gray letters
next_guess_count = 3  # e.g. 1 -> 1st guess

scored_list = wordle_helper(correct_spots, wrong_spots, wrong_letters, next_guess_count)
for word, score in scored_list[:50]:  # Only prints the top 20 words
    print(word, score)
'''

