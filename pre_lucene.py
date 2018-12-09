"""
Python file which actually creates text files out of the parsed and tokenized
collection
"""
import os
import argparse
from parse_queries import parse_query_text_file
import json
from pathlib import Path


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


def parse_user_arguments():
    """
    Helper function to parse user arguments
    :return: a dictionary containing the user arguments
    """
    ap = argparse.ArgumentParser()

    ap.add_argument("-c", "--corpus_collection", help="Enter the path to "
                                                      "the json file containing "
                                                      "the cleaned corpus", required=True)

    ap.add_argument("-q", "--query_text_file", help="Enter the path to the "
                                                   "query text file "
                                                   "with <DOC> tags", required=True)

    ap.add_argument("-co", "--corpus_out", help="Enter dirname where you "
                                               "want to store the corpus "
                                               "collection", required=True)

    ap.add_argument("-qo", "--query_output", help="Enter the path to the file where "
                                                "you want to store the query outputs",
                    required=True)

    return vars(ap.parse_args())


def write_dict_to_text_file(fname, given_dict):
    """
    Helper function to items present in dictionary to a text file
    :param fname: The text file where we want to write
    :return:
    """

    fp = open(fname, "w+")

    for item in given_dict.values():
        fp.write(item + "\n")
    fp.close()


def write_collection_corpus_to_text_file(fname, corpus_dict):
    """
    Helper function to write corpus collection to text files
    :param fname: The fname where we want to write the collection to
    :param corpus_dict: The corpus collection dictionary
    """
    dir_path = Path(os.path.realpath(".") + "\\" + fname)

    print("the directory path is ", dir_path)

    if not os.path.exists(dir_path):
        os.makedirs(str(dir_path))

        print("Directory created")

    for item in corpus_dict:
        file_path = os.path.join(dir_path, item)

        f = open(file_path + ".txt", "w+")

        # for word in corpus_dict[item].split():
        #     f.write(word + "\n")

        f.write(corpus_dict[item])

        f.close()


# Capture the user arguments
user_args = parse_user_arguments()
query_text_file = user_args["query_text_file"]
cleaned_corpus_file = user_args["corpus_collection"]

query_out = user_args["query_output"]
corpus_out = user_args["corpus_out"]

# Create the query dictionary
query_dict = parse_query_text_file(query_text_file)
write_dict_to_text_file(query_out, query_dict)

# Get the colelction dictionary
with open(cleaned_corpus_file) as fd:
    corpus = json.load(fd)

# Create text files out of the collection
write_collection_corpus_to_text_file(corpus_out, corpus)




