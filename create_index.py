"""
Python file that is used to create unigram index out of the
parsed documents from the CACM collection
"""

import json


def create_inverted_index(all_data):
    """
    Function that creates an inverted index
    :param all_data: A dictionary of the form
    {# {CACM_file_1 : parsed_tokenized_text_file_1,
    # CACM_file_2 : parsed_tokenized_text_file_2}

    :return: a dictionary which is nothing but the inverted index
    of the form
    {term_1 : {doc_1 : term_1_freq_in_doc_1, doc_2 : term_1_freq_in_doc_2},
    term_2 : {doc_1 : term2_freq_in_doc_1, doc_2 : term2_freq_in_doc_2} .....}
    """
    # Create a dictionary to hold the inverted index
    inv_index = {}

    # Now all_data is a dictionary that is of the form
    # {doc_id : parsed_output from doc_Id}

    # We will iterate through this dictionary
    for doc in all_data:
        # print("The doc is ", doc)
        # Read the contents of the document
        doc_contents = all_data[doc]

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

    return inv_index


def inverted_index_helper(doc_content_list, filename, inv_index):
    """
    A helper that updates the inverted index dicitionary
    :param doc_content_list: a list of all strings present in a document
    :param filename: The name of the file that we are currently dealing with
    :param inv_index: the actual inverted index dicitonary
    """

    # We need to handle the gram feature here
    # Hold a variable called as range count
    range_count = len(doc_content_list)

    for i in range(range_count):
        item = doc_content_list[i]
        if item not in inv_index:
            # No such key is present
            # This is the first occurrence in any of the files
            # we need to create a new entry
            # We need to update the inv_index dictionary
            inv_index[item] = {filename : 1}
        else:
            # Such a key is present
            # Then we need to update the term
            # frequency for this particular document
            if filename in inv_index[item]:
                # Such a document ID already exists in our data strcuture
                # Just increment the term frequency here
                inv_index[item][filename] += 1
            else:
                # This is the first occurrence of this filename with repsect to
                # this particular word
                # i.e this word was already present in some other filenames
                # but this is the first time that this word has appeared
                # in this document
                inv_index[item].update({filename : 1})

