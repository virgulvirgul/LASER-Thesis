#!/usr/bin/python3


import argparse
import os
import sys
assert os.environ.get('NEWS_TASK'), 'Please set the environment variable NEWS_TASK'
NEWS_TASK = os.environ['NEWS_TASK']
sys.path.append(NEWS_TASK + '/common')
sys.path.append(NEWS_TASK + '/similarity')

from database_connector import get_database_connection
from sentence_repository import get_articles_from_sentence, get_sentences_from_article
from triple_similarity_repository import *


MINIMUM_CANDIDATE_SENTENCE_LENGTH = 5


def _get_argument_parser():
    parser = argparse.ArgumentParser(description='Get similar articles in all three languages')
    parser.add_argument('--output-base-file-name', default='../output_files/triple_similar_articles',
                        help='output base file name')
    return parser


def _get_article_sentences_as_text(sentences):
    return "\n".join(sentence_tuple[0] for sentence_tuple in sentences)


def _get_output_file_name(output_base_file_name, language):
    return output_base_file_name + '_' + language


def _get_output_article_id(triple_article_index):
    return 'article-' + str(triple_article_index) + '\n'


if __name__ == "__main__":
    parser = _get_argument_parser()
    arguments = parser.parse_args()

    try:
        database_connection = get_database_connection()
        database_cursor = database_connection.cursor()

        de_output_file_name = _get_output_file_name(arguments.output_base_file_name, 'de')
        pt_output_file_name = _get_output_file_name(arguments.output_base_file_name, 'pt')
        en_output_file_name = _get_output_file_name(arguments.output_base_file_name, 'en')

        with open(de_output_file_name, 'w') as de_output_file, \
             open(pt_output_file_name, 'w') as pt_output_file, \
             open(en_output_file_name, 'w') as en_output_file:

            triple_articles = get_triple_similar_articles(database_cursor)

            for triple_article_index, triple_article in enumerate(triple_articles, start=1):
                en_article_sentences = get_sentences_from_article(triple_article[0], database_cursor)
                pt_article_sentences = get_sentences_from_article(triple_article[1], database_cursor)
                de_article_sentences = get_sentences_from_article(triple_article[2], database_cursor)

                en_article_sentences_text = _get_article_sentences_as_text(en_article_sentences)
                pt_article_sentences_text = _get_article_sentences_as_text(pt_article_sentences)
                de_article_sentences_text = _get_article_sentences_as_text(de_article_sentences)

                output_article_id= _get_output_article_id(triple_article_index)

                en_output_file.write(output_article_id)
                pt_output_file.write(output_article_id)
                de_output_file.write(output_article_id)

                en_output_file.write(en_article_sentences_text)
                pt_output_file.write(pt_article_sentences_text)
                de_output_file.write(de_article_sentences_text)

                en_output_file.write('\n')
                pt_output_file.write('\n')
                de_output_file.write('\n')
    finally:
        if database_connection is not None:
            database_connection.close()