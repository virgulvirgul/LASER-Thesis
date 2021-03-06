#!/usr/bin/python3


import os
from os import listdir
from os.path import isfile, join
import sys
assert os.environ.get('NEWS_TASK'), 'Please set the environment variable NEWS_TASK'

NEWS_TASK = os.environ['NEWS_TASK']
sys.path.append(NEWS_TASK + '/extraction')
sys.path.append(NEWS_TASK + '/extraction/en_de_corpus')

import re
import syntok.segmenter as segmenter

from en_de_article_id_sentence_extractor import extract_articles_from_file
from id_sentence_writer import write_id_sentence_pair_to_file, write_sentence_to_file
from language_identification import is_sentence_language_not_correct

INPUT_DIRECTORY = NEWS_TASK + '/input_files/'
OUTPUT_DIRECTORY = NEWS_TASK + '/output_files/'

FINDING_LANGUAGE_IN_FILE_NAME_REGEX = 'de-news-\d{4}-\d{2}-\d{2}.(\w{2}).al'


def _get_file_lines(input_file):
    return input_file.readlines()


def _get_language(input_file_name):
    matches = re.search(FINDING_LANGUAGE_IN_FILE_NAME_REGEX, input_file_name)
    return matches.group(1)


def _get_id_sentence_output_file_name(language):
    return OUTPUT_DIRECTORY + language + '_id_sentence_pairs'


def _get_sentences_output_file_name(language):
    return OUTPUT_DIRECTORY + language + '_sentences'


def _write_id_sentence_pair_to_file(output_file, article_id, sentence, sentence_index):
    sentence_id = _get_sentence_id(article_id, sentence_index)
    id_sentence_pair = _get_id_sentence_pair(sentence, sentence_id)
    output_file.write(id_sentence_pair)


def _write_sentence_to_file(output_file, sentence):
    sentence_line = _get_sentence_line(sentence)
    output_file.write(sentence_line)


def _get_sentence_id(article_id, sentence_index):
    return article_id + '_sentence_' + str(sentence_index)


def _get_id_sentence_pair(sentence, sentence_id):
    return sentence_id + '\t' + sentence + '\n'


def _get_sentence_line(sentence):
    return sentence + '\n'


def _segment_text_into_sentences(raw_sentence: str):
    sentences = []
    for segmented_sentences in segmenter.process(raw_sentence):
        for sentence in segmented_sentences:
            sentences.append("".join(map(str, sentence)).lstrip())
    return sentences


def _get_segmented_sentences(raw_article_sentences):
    segmented_sentences = []
    for raw_sentence in raw_article_sentences:
        segmented_sentences.extend(_segment_text_into_sentences(raw_sentence))
    return segmented_sentences


if __name__ == "__main__":

    input_file_names = [f for f in listdir(INPUT_DIRECTORY) if isfile(join(INPUT_DIRECTORY, f))]

    for input_file_name in input_file_names:

        language = _get_language(input_file_name)
        articles = extract_articles_from_file(INPUT_DIRECTORY + input_file_name, language)

        with open(_get_id_sentence_output_file_name(language), 'a') as id_sentence_pairs_file, \
             open(_get_sentences_output_file_name(language), 'a') as sentences_file:

            for article_id in articles.keys():
                raw_article_sentences = articles[article_id]
                article_sentences = _get_segmented_sentences(raw_article_sentences)

                for sentence_index, sentence in enumerate(article_sentences, start=1):
                    if is_sentence_language_not_correct(sentence, language):
                        print('sentence language not valid')
                        continue
                    _write_id_sentence_pair_to_file(id_sentence_pairs_file, article_id, sentence, sentence_index)
                    _write_sentence_to_file(sentences_file, sentence)