import nltk
import sys

import os
import math
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():
    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """

    returning = dict()

    keys = os.listdir(directory)
    for key in keys:
        path = (os.path.join(directory, key))
        with open(path, encoding="utf8") as f:
            s = f.read()
            returning[key] = s

    return returning


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order. ######## what mean >in order<

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    words = word_tokenize(document)  # print(len(words))
    stop_words = set(stopwords.words('english'))

    filtered = []

    for word in words:
        word = word.lower()
        if word not in string.punctuation:
            if word not in stop_words:
                filtered.append(word)
    # print(len(filtered))
    # OR
    # filtered_sentence = [w for w in words_second if not w.lower() in stop_words]
    # print(filtered)  # have: '====' "'s" "''", 'blah', '``' ................ ?

    return filtered


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """

    # print("Extracting words from documents...")
    words = set()
    for key in documents:
        words.update(documents[key])

    # print("Calculating inverse document frequencies...")  #
    idfs = dict()
    for word in words:
        f = sum(word in documents[key] for key in documents)
        idf = math.log(len(documents) / f)
        idfs[word] = idf

    # print(len(idfs))
    return idfs


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    # checking if query words in idfs
    query_words = [word.lower() for word in query
                   if word in idfs.keys()
                   ]

    # Calculate TF-IDFs
    print("Calculating term frequencies...")
    tfidfs = dict()
    # Add keys in dict -> DICT={FILENAME:{QUERY_WORD:HOW_MANY_TIMES_IN FILENAME}}
    for filename in files:
        tfidfs[filename] = dict()
        for word in query_words:
            tfidfs[filename][word] = 0

    # COUNTING
    for filename in files:

        for word in files[filename]:
            for query_word in query_words:
                if word == query_word:
                    tfidfs[filename][query_word] += 1

        for word in query_words:
            tfidfs[filename][word] *= idfs[word]

    sum_dict = dict()
    for key in files:
        sum_dict[key] = 0
        for word in query_words:
            sum_dict[key] += tfidfs[key][word]

    sum_dict = dict(sorted(sum_dict.items(), key=lambda x: x[1], reverse=True))

    return_list = []
    for i in range(n):
        return_list.append(list(sum_dict.keys())[i])

    return return_list


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    #for word in query:
    #    print(word, " -> " , idfs[word])

    sentences_values = dict()

    for sentence in sentences:
        value = 0
        for word in query:  # for every query word
            if word in sentences[sentence]:  # if query word in sentence (ONLY ONCE IS COUNT???????)
                value += idfs[word]
        sentences_values[sentence] = value

    sum_dict = dict(sorted(sentences_values.items(), key=lambda x: x[1], reverse=True))

    set_of_values_to_return_plus_one ={}
    for i in range(n+1):
        set_of_values_to_return_plus_one.add(list(sum_dict.values())[i])
    if len(set_of_values_to_return_plus_one) != n+1:
        # If two sentences have the same value
        pass
        

    return_list = []
    for i in range(n+1):
        return_list.append(list(sum_dict.keys())[i])

    return return_list

    #raise NotImplementedError


if __name__ == "__main__":
    main()
