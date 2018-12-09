"""
Python file which actually performs retrieval of documents for stemmed queries
"""

import argparse
import json
from pathlib import Path
import os
from baseline_runs import write_top_100_scores_to_txt, new_bm25_scores, tf_idf, jm_likelihood_scores


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


def convert_to_non_os_specific_path(fname):
    """
    This is a utility function that converts the the given fname
    (which is a relative in Windows path format) to a path which can be used
    on all OS'
    :param fname: a relative path on Windows path format(using \\)
    :return: a non-OS specific path
    """
    return Path(os.path.realpath(".") + fname)


def parse_user_args():
    """
    Function that passes the arguments passed by the user on the command line
    :return: a dictionary with all the user arguments in the form of key
    value pairs
    """

    ap = argparse.ArgumentParser()

    ap.add_argument("-m", "--method", help="Enter the type of baseline run, "
                                           "bm_25, tf_idf or jm_qlm", required=True)

    ap.add_argument("-j", "--json_fname", help="Enter the path to the json "
                                               "filename containing"
                                               "all the paths to the "
                                               "test_collection", required=True)

    return vars(ap.parse_args())


# Get the user arguments
user_args = parse_user_args()
baseline = user_args["method"]
json_fname_relative_paths = user_args["json_fname"]

# Note the file "all_paths.json" has all the relative paths
# We will read this file and store the json file in a dictionary
all_paths_dict = read_json_document(json_fname_relative_paths)

print("Running ", baseline, " model")

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
                                 "stemmed_corpus_json_fname"])

with open(collection_data_fname) as c_fd:
    url_text_dict = json.load(c_fd)


# Now that we have received a dictionary containing all the doc_IDs as keys
# and their contents parsed as values, we will create the inverted index
# The inverted index is of the form
# {term_1 : {doc_1 : term_1_freq_in_doc_1, doc_2 : term_1_freq_in_doc_2},
# term_2 : {doc_1 : term2_freq_in_doc_1, doc_2 : term2_freq_in_doc_2} .....}

# NOTE: We have already created the index and stored it in the json file
# stopped_queries_output.json( Done by script create_index.py)


stemmed_queries_inverted_index = Path(os.path.realpath(".") +
                             all_paths_dict[
                                 "stemmed_inverted_index"])


with open(stemmed_queries_inverted_index) as inv_fd:
    inverted_index = json.load(inv_fd)

# We will use this inverted index to score the documents
# Get the non-OS dependent path to the query text file
query_text_file = convert_to_non_os_specific_path(all_paths_dict["test_data"]["stem_queries"])
print("the query text file is ", query_text_file)

# Get the non-OS dependent path to the query text file
relevance_text_file = convert_to_non_os_specific_path(all_paths_dict["test_data"]["relevance_text_file"])
print("the relevenace text file is ", relevance_text_file)


# Get the BM25 scores in a dictionary
if baseline == "bm25":
    bm_25_scores = new_bm25_scores(url_text_dict, inverted_index, query_text_file, relevance_text_file, normal_query_file=True)

    # Writing the results to a text filerelevant_json_fname
    output_text_fname = Path(os.path.realpath(".") +
                                 all_paths_dict[
                                     "bm25_stem_queries"])
    write_top_100_scores_to_txt(bm_25_scores, output_text_fname, "bm25")
elif baseline == "tf_idf":
    tf_idf_scores = tf_idf(url_text_dict, inverted_index, query_text_file, normal_query_file=True)
    tf_idf_output_text_fname = Path(os.path.realpath(".") +
                                 all_paths_dict[
                                     "tf_idf_stem_queries"])
    write_top_100_scores_to_txt(tf_idf_scores, tf_idf_output_text_fname, "tf_idf")

elif baseline == "jm_qlm":
    jm_qlm_scores = jm_likelihood_scores(url_text_dict, inverted_index, query_text_file, normal_query_file=True)
    jm_qlm_score_output_text_file = Path(os.path.realpath(".") +
                                         all_paths_dict["jm_qlm_stem_queries"])

    write_top_100_scores_to_txt(jm_qlm_scores, jm_qlm_score_output_text_file,"jm_qlm")