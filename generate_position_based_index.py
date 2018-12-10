"""
Python file which is used to generate position based inverted index
This positional based inverted index will be used for exact match and
ordered proximity match
"""

import argparse
import json
import os
from pathlib import Path
import errno


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

    return vars(ap.parse_args())


def create_position_index(corpus, pos_ind_fname):
    """
    Function to create positional inverted index
    :return: a dictionary of the form
    {term : { doc : [freq, [pos_1, pos_2, pos_3]]}
    """

    # Create a dictionary to hold the inverted index
    inv_index = {}

    # Now all_data is a dictionary that is of the form
    # {doc_id : parsed_output from doc_Id}

    # We will iterate through this dictionary
    for doc in corpus:
        # Read the contents of the document
        doc_contents = corpus[doc]

        # Note: doc_contents is a string
        # To count the number of words we will split this string into a list
        doc_content_list = doc_contents.split()

        # Cut the ".txt" part from the filename
        filename = doc

        # Now call helper function
        inverted_index_helper(doc_content_list, filename, inv_index)

        # Note that the dictionary inv_index
        # will be updated by the helper function
        # inverted_index_helper

    if not os.path.exists(os.path.dirname(pos_ind_fname)):
        try:
            os.makedirs(os.path.dirname(pos_ind_fname))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise

    # Write the inverted index to a specific.json file
    with open(pos_ind_fname, "w+") as o_fd:
        json.dump(inv_index, o_fd, indent=4)


def inverted_index_helper(doc_content_list, filename, inv_index):
    """
    A helper that updates the inverted index dicitionary
    :param doc_content_list: a list of all strings present in a document
    :param filename: The name of the file that we are currently dealing with
    :param inv_index: the actual inverted index dicitonary
    """

    for i, item in enumerate(doc_content_list):
        if item not in inv_index:
            # No such key is present
            # This is the first occurrence in any of the files
            # we need to create a new entry
            # We need to update the inv_index dictionary
            inv_index[item] = {filename: [1, [i]]}
        else:
            # Such a key is present
            # Then we need to update the term
            # frequency for this particular document
            if filename in inv_index[item]:
                # Such a document ID already exists in our data strcuture
                # Just increment the term frequency here
                inv_index[item][filename][0] += 1
                inv_index[item][filename][1].append(i)
            else:
                # This is the first occurrence of this filename with repsect to
                # this particular word
                # i.e this word was already present in some other filenames
                # but this is the first time that this word has appeared
                # in this document
                inv_index[item].update({filename: [1, [i]]})


# Get the user arguments
user_args = parse_user_args()
json_fname_relative_paths = user_args["json_fname"]

# Note the file "all_paths.json" has all the relative paths
# We will read this file and store the json file in a dictionary
all_paths_dict = read_json_document(json_fname_relative_paths)


# Now we will load this json file into a dictionary
# Note: url_text_dict is of the form
# {CACM_file_1 : parsed_tokenized_text_file_1,
# CACM_file_2 : parsed_tokenized_text_file_2}

collection_data_fname = Path(os.path.realpath(".") +
                             all_paths_dict[
                                 "parsed_tokenized_output_json_file"])

with open(collection_data_fname) as c_fd:
    url_text_dict = json.load(c_fd)


positional_inverted_fname = Path(os.path.realpath(".") + all_paths_dict["positional_index"])

create_position_index(url_text_dict, positional_inverted_fname)
