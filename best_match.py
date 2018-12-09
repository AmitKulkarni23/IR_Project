"""
Python file which implements the best_match part of the Extra credit
A document is ranked and shown if it contains atleast 1 query term
"""

import json
import argparse
import os
from pathlib import Path
from parse_queries import parse_query_text_file
from baseline_runs import sort_dict_according_to_scores, write_top_100_scores_to_txt


def read_json_document(json_file_name):
    """
    Helper function to read all the path variables form the json file
    Note: We are maintaining a json file to read all the input paths of our
    test collection and also the output_paths

    This will help us change the output/input paths of
    data easily(just change in the json file) instead of worrying about changing
    paths in the codebase
    :return: a dictionary after the reading the entire json file
    """

    with open(json_file_name) as fd:
        data = json.load(fd)

    return data


def parse_user_args():
    """
    Helper function to parse user arguments
    :return: a dictionary containing the user arguments
    """
    ap = argparse.ArgumentParser()

    ap.add_argument("-j", "--json_fname", help="Enter the path to the json "
                                               "filename containing"
                                               "all the paths to the "
                                               "test_collection", required=True)

    ap.add_argument("-m", "--method", help="Enter the type of baseline run, "
                                           "bm_25, tf_idf or jm_qlm",
                    required=True)

    return vars(ap.parse_args())


def best_match(corpus, inverted_index_arg, query_text_file):
    """
    Method which scores
    :param corpus: # {CACM_file_1 : parsed_tokenized_text_file_1,
    # CACM_file_2 : parsed_tokenized_text_file_2}
    :param inverted_index_arg:
    {term_1 : {doc_1 : term_1_freq_in_doc_1, doc_2 : term_1_freq_in_doc_2},
    term_2 : {doc_1 : term2_freq_in_doc_1, doc_2 : term2_freq_in_doc_2} .....}
    :param query_text_file
    :return:
    """

    # Create another dictionary that will hold the doc_id
    # and their best_match score
    # {query_1 : {doc_id_1 : score_for_doc_id_1, doc_id_2: score_for_doc_id_2}
    # ...query_64 : {}}
    best_match_score = {}

    # Populate the dictionary with empty inner dictionaries
    for i in range(1, 65):
        best_match_score[i] = {}

    # Note:
    # query_dict is of the form
    # {query_numb : <parsed_query>}
    query_dict = parse_query_text_file(query_text_file)

    for q in query_dict:
        # Iterate through all the queries
        for doc in corpus:
            # Iterate through the entire corpus
            flag = False
            score = 0
            for term in set(query_dict[q].split()):
                if term in inverted_index and doc in inverted_index_arg[term]:
                    # This document conatins this particular query term
                    # Just add the freq to the score
                    score += inverted_index_arg[term][doc]

                    # if flag is True -> means that atleast 1 query term is
                    # present in document and this document should be considered
                    # for ranking
                    flag = True

            if flag:
                # Will only come here if document conatins atleast 1 query term
                best_match_score[q][doc] = score

    sort_dict_according_to_scores(best_match_score)
    return best_match_score


# Get the user arguments
user_args = parse_user_args()
retrieval_type = user_args["method"]
json_fname_relative_paths = user_args["json_fname"]

# Note the file "all_paths.json" has all the relative paths
# We will read this file and store the json file in a dictionary
all_paths_dict = read_json_document(json_fname_relative_paths)


# Create Index
# To create index we first need to parse all the 3204 documents
# NOTE: We have already parsed all the 3204 documents and stored it in
# a json file( using the script create_collection_data_dict.py)


# Now we will load this json file into a dictionary
# Note: url_text_dict is of the form
# {CACM_file_1 : parsed_tokenized_text_file_1,
# CACM_file_2 : parsed_tokenized_text_file_2}

collection_data_fname = Path(os.path.realpath(".") +
                             all_paths_dict[
                                 "parsed_tokenized_output_json_file"])

with open(collection_data_fname) as c_fd:
    url_text_dict = json.load(c_fd)


# Now that we have received a dictionary containing all the doc_IDs as keys
# and their contents parsed as values, we will create the inverted index
# The inverted index is of the form
# {term_1 : {doc_1 : term_1_freq_in_doc_1, doc_2 : term_1_freq_in_doc_2},
# term_2 : {doc_1 : term2_freq_in_doc_1, doc_2 : term2_freq_in_doc_2} .....}

# NOTE: We have already created the index and stored it in the json file
# stopped_queries_output.json( Done by script create_index.py)

# We will load the json file and read it into a dictionary
inverted_index_json_fname = Path(os.path.realpath(".") +
                                 all_paths_dict[
                                     "indexer_output_json_file"])


with open(inverted_index_json_fname) as inv_fd:
    inverted_index = json.load(inv_fd)


query_text_fname = Path(os.path.realpath(".") + all_paths_dict["test_data"]["query_text_file"])

# best match Output Filename
best_match_output_fname = Path(os.path.realpath(".") + all_paths_dict["extra_credit_output_best_match"])

best_match_scores = best_match(url_text_dict, inverted_index, query_text_fname)
write_top_100_scores_to_txt(best_match_scores, best_match_output_fname, retrieval_type)


