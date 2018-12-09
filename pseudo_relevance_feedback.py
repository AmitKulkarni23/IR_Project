"""
Python file that performs pseudo relevance feedback on the BM25
scores for documents

Credits -> https://nlp.stanford.edu/IR-book/html/htmledition/the-rocchio71-algorithm-1.html
"""

# Import statements
from baseline_runs import new_bm25_scores, write_top_100_scores_to_txt, \
    parse_query_text_file, get_relevance_information, \
    sort_dict_according_to_scores, get_avg_doc_length, calculate_r_i
import argparse
import json
from pathlib import Path
import os
from task_1_main import read_json_document, convert_to_non_os_specific_path
from collections import Counter
import math
import errno


def parse_user_arguments():
        """
        Function that passes the arguments passed by the user on the command line
        :return: a dictionary with all the user arguments in the form of key
        value pairs
        """

        ap = argparse.ArgumentParser()

        ap.add_argument("-m", "--method",
                        help="Enter the type of baseline run, "
                             "bm_25, tf_idf or jm_qlm", required=True)

        ap.add_argument("-j", "--json_fname", help="Enter the path to the json "
                                                   "filename containing"
                                                   "all the paths to the "
                                                   "test_collection",
                        required=True)

        return vars(ap.parse_args())


def pseudo_relevance_feedback(bm25_doc_scores, q_dict, inv_index, new_query_filename):
    """
    Function that calculates the pseudo relevance feedback for all docs
    given a dictionary which contains documents ranked
    according to their BM25 scores
    ( with prior relevance information included)
    :param: bm25_doc_scores - a list of the tuples of the form
    [(doc_1, doc_1_score), (doc_2, doc_2_score)....]
    :param q_dict: {q_id: < Parsed Query >, q_id_2: < Parsed Query 2 >}
    :param inv_index: The inverted index of the form
    {term_1 : {doc_1 : term_1_freq_in_doc_1, doc_2 : term_1_freq_in_doc_2},
    term_2 : {doc_1 : term2_freq_in_doc_1, doc_2 : term2_freq_in_doc_2} .....}
    :param new_query_filename: The name of the text file where we will be writing
    all the new queries
    :return: A dictionary of the form with scores being the
    pseudo relevance scores
    """

    # Creating a copy of the dictionary passed in as argument.
    # Creating a shallow copy
    pseudo_scores = bm25_doc_scores.copy()

    # The parameters used in the Pseudo Relevance formula
    beta = 0.75
    gamma = 0.15
    alpha = 1

    # k -> Number of documents to consider for the feedback loop
    k = 10

    # Number of terms to be appended to the original query after
    # the query has ben enriched
    enrichment_terms = 30

    # NOTE: Idea behind Pseudo-relevance feedback:
    # Moves the new query being generated towards the centroid of the relevant
    # documents and away from the centroid of the non-relevant_docs

    # query_dict is of the form
    # {q_id: < Parsed Query >, q_id_2: < Parsed Query 2 >}

    # Create a file handler to the file where we will be writing all the
    # enriched queries
    fp = open(new_query_filename, "w+")

    my_query_dict = {}
    count = 1

    for q in q_dict:
        # print("Considering query ", q)
        sorted_scores = pseudo_scores[q]

        # Create a query vector
        # is a dictionary of the form
        query_vector = generate_query_vector(q, q_dict, inv_index)

        # Create a relevance vector
        relevance_vector = generate_rel_non_rel_vector(inv_index,
                                                       sorted_scores, 0, k)

        corpus_len = len(sorted_scores)

        non_relevance_vector = generate_rel_non_rel_vector(inv_index,
                                                           sorted_scores,
                                                           k+1, corpus_len)

        # Get the magnitude of both the vectors
        rel_vec_mag = get_magnitude_vector(relevance_vector)
        non_rel_vec_mag = get_magnitude_vector(non_relevance_vector)

        # GENERATE THE NEW QUERY USING THE PSEUDO RELEVANCE FORMULA
        new_query = {}
        for item in inv_index:
            new_query[item] = alpha * query_vector[item] + (beta / rel_vec_mag) * relevance_vector[item] - (gamma / non_rel_vec_mag) * non_relevance_vector[item]

        sorted_expansion_query_terms = [(k, new_query[k]) for k in
                                        sorted(new_query,
                                               key=new_query.get,
                                               reverse=True)]

        # OK, we have now gotten the expanded query
        # There might be some terms that are not in the original query
        # We have to append such terms to the original query

        # Create a copy of the original query
        original_query = q_dict[q]
        new_query = original_query
        for i in range(enrichment_terms):
            term, term_freq = sorted_expansion_query_terms[i]
            if term not in original_query:
                new_query += (" " + term)

        # Write this query term to a new text_file
        my_query_dict[count] = new_query
        fp.write(new_query + "\n")

        count += 1

    # Now we have gotten new queries (expanded ato a maximum of 30 terms)
    # This is query enrichment
    # Now we have to calculate BM25 scores and rank documents according
    # to these queries

    return redundant_pseudo_bm25(url_text_dict, inv_index, relevance_text_file, my_query_dict, rel_info_enabled=True)


def get_magnitude_vector(given_vector):
    """
    Function that calculates the magnitude of the given vector
    :param given_vector: is a vectors, basically a dictionary
    :return: a scalar, which is the magnitude of the given vector
    """

    # Note: given vector is a dictionary of the form:
    # {term : score}

    magnitude = 0
    for item in given_vector.values():
        magnitude += item ** 2

    return magnitude ** 0.5


def generate_rel_non_rel_vector(inv_index, doc_scores, start, end):
    """
    Helper function which creates relevance(or a non relevance) vector given BM25 scores
    and inverted index and given the start and end indices
    :param inv_index: The inverted index which is of the form
    {term_1 : {doc_1 : term_1_freq_in_doc_1, doc_2 : term_1_freq_in_doc_2},
    term_2 : {doc_1 : term2_freq_in_doc_1, doc_2 : term2_freq_in_doc_2} .....}
    :param doc_scores: is of the form
    [(doc_1, doc_1_score), (doc_2, doc_2_score)....]
    :return: a dictionary which is nothing but the relevance vector
    """

    result_vector = {}

    for i in range(start, end):
        doc_id, doc_score = doc_scores[i]

        # Get the content of this document which will be in the form of a string
        # convert it into a list of words and create a frequency map of the
        # words

        # NOTE: corpus_collection_path is the global variable here

        fp = open(str(corpus_collection_path) + "\\" + doc_id + ".html")
        content = fp.read().split()
        fp.close()

        result_vector = dict(Counter(content))

    # Check with the inverted index
    for index_item in inv_index:
        if index_item not in result_vector:
            result_vector[index_item] = 0

    return result_vector


def generate_query_vector(q, q_dict, inv_index):
    """
    Helper function that will generate the query vector
    Note: The query vector is the basically a dictionary
    with keys as query terms( values = freq_of_query terms in freq)
    keys(indexed terms) -> values(presence or absence of the ternm in the
    query vector. Non - Presnece = 0)
    :param q_dict: {q_id: < Parsed Query >, q_id_2: < Parsed Query 2 >}
    :param inv_index : The inverted index
    :return: dcitionary of key value pairs as described above
    """
    # Create the query vector
    query_vector = dict(Counter(q_dict[q]))

    # Add to this query vector, all the indexed terms
    for i_term in inv_index:
        if i_term not in query_vector:
            query_vector[i_term] = 0

    return query_vector


# ToDO: The original new_bm_25 was giving some pronlems
# with reading new query text file
# Same implementation below, but query dictionary passed in as argument

# ToDo: need to check why file reading is not proper
def redundant_pseudo_bm25(collection_data, indexed_data, relevant_docs_fname, query_dict, rel_info_enabled=False):
    """
    Function that performs BM25 ranking
    :param collection_data: A dictionary containing the parsed output of teh entire
    collection. This dictionary is of the form
    # {CACM_file_1 : parsed_tokenized_text_file_1,
    # CACM_file_2 : parsed_tokenized_text_file_2}
    :param indexed_data: The inverted index
    {term_1 : {doc_1 : term_1_freq_in_doc_1, doc_2 : term_1_freq_in_doc_2},
    term_2 : {doc_1 : term2_freq_in_doc_1, doc_2 : term2_freq_in_doc_2} .....}
    :param query_dict: is a dictionary of the form
    {query_id : actual_query}
    :param relevant_docs_fname: The text file containing the relevance file
    i.e cacm.rel.txt
    :param rel_info_enabled: Default value is False
    If this param is True, then the relevance information is taken into account
    :return: Will return a dictionary with values as lists made up of tuples that are sorted
    {query_id : [(doc_1, doc_1_score), (doc_2, doc_2_score)....]
    """

    # Create another dictionary that will hold the doc_id and their BM25 score
    # Note: We will maintain the bm_25scores dictionary in the form
    # {query_1 : {doc_id_1 : score_for_doc_id_1, doc_id_2: score_for_doc_id_2}
    # ...query_64 : {}}
    new_bm25_scores_dict = {}

    # Populate the dictionary with empty inner dictionaries
    for i in range(1, 65):
        new_bm25_scores_dict[i] = {}

    # Note: Indexed data is of the form
    # { term : { doc_id : count_in_doc } }

    # Now the json data is present in the dictionaries
    # Note: There is information given about relevance in file cacm.rel.txt
    # file. We need to get the relevance information
    # rel_docs_dict i sof the form:
    # {query_numb: [ < list of all docs relevant to query 1]}
    rel_docs_dict = get_relevance_information(relevant_docs_fname)

    # query_dict is of the form
    # {q_id: < Parsed Query >, q_id_2: < Parsed Query 2 >}

    # N -> Total number of collections in the data
    N = len(collection_data)

    # The constants
    k1 = 1.2
    b = 0.75
    k2 = 100

    avg_doc_length = get_avg_doc_length(collection_data)

    for q in query_dict:
        # R ->  Total number of relevant documents for this query

        if rel_info_enabled:
            # Accomodation prior( relevance information )
            # print("Query we are considering is ", q)
            R = len(rel_docs_dict[q])
        else:
            R = 0

        # Store the relevant documents in a list
        rel_docs_list = rel_docs_dict[q]

        # TODO: Calculate r_i -> Refer to the Piazza post( Required for Phase3)

        for term in query_dict[q].split():
            # If this query term is present in our index
            if term in indexed_data:

                # n_i -> The number of documents containing this query term
                # for each document containing this query term
                n_i = len(indexed_data[term])

                # q_i -> frequency of this term in the entire query
                q_fi = query_dict[q].split().count(term)

                # r_i -> number of relevant docs containing term i
                r_i = 0
                if rel_info_enabled:
                    r_i = calculate_r_i(rel_docs_list, indexed_data, term)

                for doc in indexed_data[term]:
                    # f_i -> frequency of this term in the document
                    # NOTE: In this way we are avoiding any
                    # document having f_i as 0
                    f_i = indexed_data[term][doc]
                    K = k1 * ((1 - b) + b * len(
                        collection_data[doc].split()) / avg_doc_length)
                    z = ((k1 + 1) * f_i / (K + f_i)) * ((k2 + 1) * q_fi) / (
                                k2 + q_fi)
                    numerator = ((r_i + 0.5) / (R - r_i + 0.5)) * z
                    denominator = (
                                (n_i - r_i + 0.5) / (N - n_i - R + r_i + 0.5))
                    temp_score = math.log(numerator / denominator)

                    if doc in new_bm25_scores_dict[q]:
                        new_bm25_scores_dict[q][doc] += temp_score
                    else:
                        new_bm25_scores_dict[q][doc] = temp_score

    sort_dict_according_to_scores(new_bm25_scores_dict)
    return new_bm25_scores_dict

# TODO: THE BELOW CODE IS REDUNDANT. The same code is present in task_1_main.py
# TODO: Need to fix this


# Get the user arguments
user_args = parse_user_arguments()
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

# NOTE: WE HAVE ALREADY CREATED THE INVERTED INDEX AND STORED IT IN A JSON FILE
# using the script(create_index.py)

# We will load the json file and read it into a dictionary
inverted_index_json_fname = Path(os.path.realpath(".") +
                             all_paths_dict[
                                 "indexer_output_json_file"])

with open(inverted_index_json_fname) as inv_fd:
    inverted_index = json.load(inv_fd)


# Get the non-OS dependent path to the query text file
query_text_file = convert_to_non_os_specific_path(all_paths_dict["test_data"]["query_text_file"])

# Get the non-OS dependent path to the query text file
relevance_text_file = convert_to_non_os_specific_path(all_paths_dict["test_data"]["relevance_text_file"])

new_queries_fname = convert_to_non_os_specific_path(all_paths_dict["new_expanded_queries"])

# Create the file if it doesn't exist
if not os.path.exists(os.path.dirname(new_queries_fname)):
    try:
        os.makedirs(os.path.dirname(new_queries_fname))
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
print("The new queries text file is ", new_queries_fname)

# Get the corpus collection path
corpus_collection_path = Path(os.path.realpath(".") +
                             all_paths_dict["test_data"]["test_collection_path"])

# Parse the query text file
query_dict = parse_query_text_file(query_text_file)
relevance_dict = get_relevance_information(relevance_text_file)

bm_25_scores_wit_rel = new_bm25_scores(url_text_dict, inverted_index,
                                       query_text_file, relevance_text_file,
                                       rel_info_enabled=True)

pseudo_rel_scores = pseudo_relevance_feedback(bm_25_scores_wit_rel,
                                              query_dict,
                                              inverted_index, new_queries_fname)

# # Writing the results to a text file
output_text_fname = Path(os.path.realpath(".") +
                             all_paths_dict[
                                 "pseudo_relevance_feedback_scores"])

write_top_100_scores_to_txt(pseudo_rel_scores, output_text_fname,
                            "pseudo_rel_feedback")


