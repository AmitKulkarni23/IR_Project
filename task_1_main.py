"""
Python file that will be used to perform all the tasks related to Task1
"""

import argparse
from baseline_runs import new_bm25_scores, write_top_100_scores_to_txt, tf_idf, jm_likelihood_scores
import json
from pathlib import Path
import os


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


def display_first_n_items_in_dict(given_dict, n):
    """
    This is just a utility function to display the first n items in a dictionary
    :param given_dict: a dictionary
    """
    count = 0
    for k in given_dict:
        print(k , "-> ", given_dict[k])
        count += 1
        if count >= n:
            break


def write_output_to_json_file(inv_index, fname):
    """
    Function that writes to a json file
    :param inv_index: The inverted index which is of the form
    {term_1 : {doc_1 : term_1_freq_in_doc_1, doc_2 : term_1_freq_in_doc_2},
    term_2 : {doc_1 : term2_freq_in_doc_1, doc_2 : term2_freq_in_doc_2} .....}
    :param fname: The json file name where you want to write the dictionary
    into
    """

    with open(fname, "w+") as o_fd:
        json.dump(inv_index, o_fd, indent=4)


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
                                 "parsed_tokenized_output_json_file"])

print("THE COLLECTION DATA FNMAE IS ", collection_data_fname)

with open(collection_data_fname) as c_fd:
    url_text_dict = json.load(c_fd)

# Now that we have received a dictionary containing all the doc_IDs as keys
# and their contents parsed as values, we will create the inverted index
# The inverted index is of the form
# {term_1 : {doc_1 : term_1_freq_in_doc_1, doc_2 : term_1_freq_in_doc_2},
# term_2 : {doc_1 : term2_freq_in_doc_1, doc_2 : term2_freq_in_doc_2} .....}

# NOTE: WE HAVE ALREADY CREATED THE INVERTED INDEX AND STORED IT IN A JSON FILE
# using the script(create_index.py)

# We will load the json file and read it into a dictionary
inverted_index_json_fname = Path(os.path.realpath(".") +
                             all_paths_dict[
                                 "indexer_output_json_file"])

print("The inverted index filename is ", inverted_index_json_fname)
with open(inverted_index_json_fname) as inv_fd:
    inverted_index = json.load(inv_fd)


# Print the first 5 items of dictionary
# display_first_n_items_in_dict(inverted_index, 2)


# Get the non-OS dependent path to the query text file
query_text_file = convert_to_non_os_specific_path(all_paths_dict["test_data"]["query_text_file"])
print("the query text file is ", query_text_file)

# Get the non-OS dependent path to the query text file
relevance_text_file = convert_to_non_os_specific_path(all_paths_dict["test_data"]["relevance_text_file"])
print("the relevenace text file is ", relevance_text_file)

# Get the path of the json file where you want to
# store the relevant data dictionary
relevant_json_fname = convert_to_non_os_specific_path(all_paths_dict["relevant_docs_json_output_fname"])

# Get the BM25 scores in a dictionary
if baseline == "bm25":
    bm_25_scores = new_bm25_scores(url_text_dict, inverted_index, query_text_file, relevance_text_file)

    # Writing the results to a text file
    output_text_fname = Path(os.path.realpath(".") +
                                 all_paths_dict[
                                     "bm_25_score_output_text_file"])
    write_top_100_scores_to_txt(bm_25_scores, output_text_fname, "bm25")
elif baseline == "tf_idf":
    tf_idf_scores = tf_idf(url_text_dict, inverted_index, query_text_file)
    tf_idf_output_text_fname = Path(os.path.realpath(".") +
                                 all_paths_dict[
                                     "tf_idf_score_output_text_file"])
    write_top_100_scores_to_txt(tf_idf_scores, tf_idf_output_text_fname, "tf_idf")

elif baseline == "jm_qlm":
    jm_qlm_scores = jm_likelihood_scores(url_text_dict, inverted_index, query_text_file)
    jm_qlm_score_output_text_file = Path(os.path.realpath(".") +
                                         all_paths_dict["jm_qlm_score_output_text_file"])

    write_top_100_scores_to_txt(jm_qlm_scores,jm_qlm_score_output_text_file,"jm_qlm")