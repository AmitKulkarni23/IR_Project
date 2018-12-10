"""
Python file which conatins functions to perform baseline runs given the indexer
"""
from parse_queries import parse_query_text_file
import collections
import math
import os
import errno


def get_relevance_information(rel_info_fname):
    """
    Function that reads the cac.rel file and gets the relevance information that
    will be used for the BM25 model
    :param rel_info_fname: The path to the file containing the relevance information
    : Will return a dictionary of the form
    {query_numb : [ <list of all docs relevant to query 1] }
    """

    rel_docs_dict = collections.defaultdict(list)

    # How to read the cac.rel.txt file
    # 1 Q0 CACM - 1410 1
    # 1 - query number
    # Q0 - fixed literal
    # CACM-1410 - filename
    # 1 - which indicates that the file is relevant

    # We will read this file and convert it into a dictionary
    with open(rel_info_fname) as rel_fd:

        for line in rel_fd:
            # print("the line is ", line)
            items = line.split()

            # print("Split items = ", items)
            # So items will be ["1", "Q0", "CACM-1410", "1"]
            # Store this in a dictionary
            if int(items[0]) in rel_docs_dict:
                rel_docs_dict[int(items[0])].append(append_proper_zeros(items[2]))
            else:
                rel_docs_dict[int(items[0])] = [append_proper_zeros(items[2])]

    rel_fd.close()

    return rel_docs_dict


def append_proper_zeros(given_str):
    """
    This function appends proper zeros to doc_ids
    :param given_str: is the doc_id ( Example: CACM-74, CACM-1401, CACM-504)
    :return: string with proper zeros appended ( Example: CACM-0074, CACM-1410, CACM-0504)
    """
    temp_list = given_str.split("-")

    item = temp_list[1]
    if len(item) == 1:
        temp_list[1] = "000" + item
    elif len(item) == 2:
        temp_list[1] = "00" + item
    elif len(item) == 3:
        temp_list[1] = "0" + item

    return "-".join(temp_list)


def new_bm25_scores(collection_data, indexed_data, query_text_file_name, relevant_docs_fname, rel_info_enabled=False, normal_query_file=False):
    """
    Function that performs BM25 ranking
    :param collection_data: A dictionary containing the parsed output of teh entire
    collection. This dictionary is of the form
    # {CACM_file_1 : parsed_tokenized_text_file_1,
    # CACM_file_2 : parsed_tokenized_text_file_2}
    :param indexed_data: The inverted index
    {term_1 : {doc_1 : term_1_freq_in_doc_1, doc_2 : term_1_freq_in_doc_2},
    term_2 : {doc_1 : term2_freq_in_doc_1, doc_2 : term2_freq_in_doc_2} .....}
    :param query_text_file_name: The path to the file coPath(ntaining all the queries
    :param relevant_docs_fname: The text file containing the relevance file
    i.e cacm.rel.txt
    :param rel_info_enabled: Default value is False
    If this param is True, then the relevance information is taken into account
    :param normal_query_file: If the query file input to this method contains
    <DOC></DOC> strings then this argument is False else if its a normal text
    file as in queries written line by line then this is TRUE
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
    # print("The rel docsc dict is ", rel_docs_dict)

    # query_dict is of the form
    # {q_id: < Parsed Query >, q_id_2: < Parsed Query 2 >}
    if not normal_query_file:
        query_dict = parse_query_text_file(query_text_file_name)
    else:
        query_dict = parse_normal_query_text_file(query_text_file_name)

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


def calculate_r_i(rel_docs_list, indexed_data, term):
    """
    Helper function which calculates the term r_i in the BM25 algorithm
    i.e the number of relevant documenst conating the term i
    :param rel_docs_list: is a list of relevant documents specific to a query
    :param indexed_data: is the inverted index
    :param term: is the query term
    :return: number of relevant docs conatining the query term "term"
    """
    r_i = 0
    total_docs = indexed_data[term]

    for item in total_docs:
        if item in rel_docs_list:
            r_i += 1

    return r_i


def sort_dict_according_to_scores(given_dict):
    """
    Helper function to sort the dictionary based on the scores
    :param given_dict: the bm25_scores dictionary which is of the form
    {query_1 : {doc_id_1 : score_1, doc_id_2: score_2..}, query_2 : {....}}
    :return: The sorted dictionary
    """

    for k, v in given_dict.items():
        given_dict[k] = sorted(v.items(), key=lambda x: x[1],reverse=True)


def get_avg_doc_length(col_data):
    """
    helper function which returns the average document length in the entire collection
    :param col_data: dictionary of the form
    {doc_id 1 : contnet_doc_id_1, doc_id_2 : content_doc_id_2 ....}
    :return: average document length in this collection
    """

    total_length = 0
    for doc in col_data:
        total_length += len(col_data[doc].split())

    return total_length / len(col_data)


def write_top_100_scores_to_txt(score_dict, fname, method_name):
    """
    Function that will write the top 100 scores of the baseline run to a .txt file
    :param score_dict: is a dictionary of the form
    {q_id : { doc_1: score_1....}, query_2 : { doc_2, .....}}
    Note: This dictionary is sorted
    :param: fname -> The txt file which will have all the information regarding
    the
    :return: Write this data into a text file ( only the top 100) in the format
    Query_ID Q0 doc_id rank score baseline_method
    """

    if not os.path.exists(os.path.dirname(fname)):
        try:
            os.makedirs(os.path.dirname(fname))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise

    fd = open(fname, "w+")
    for q in score_dict:
        inner_dict = score_dict[q]

        # Converting a dictionary to a list
        # The cinverted list will only contain the keys

        if not inner_dict:
            fd.write("No results found for query " + str(q))
            fd.write("\n")
            fd.write("--------------\n")
            continue
        for idx, item in enumerate(inner_dict[:100]):
            to_write = str(q) + " " + "Q0" + " " + item[0] + " " + str(idx + 1) + " " + str(item[1]) + " " + method_name + "\n"
            fd.write(to_write)

        fd.write("-----------------------\n")
    fd.close()


def tf_idf(collection_data_arg, indexed_data_arg, query_text_file_name, normal_query_file=False):
    """
    Function that calculates the tf_idf_scores for each document
    :param normal_query_file: Indicates whether the query file is text file
    with no <DOC></DOC> tags( if True)
    :return: a sorted list of documents in the form as below:
    [(doc_id_1, score_1),(doc_id_2, score_2)....]
    """

    tf_idf_scores = {}

    # Populate the dictionary with empty inner dictionaries
    for i in range(1, 65):
        tf_idf_scores[i] = {}

    # query_dict is of the form
    # {q_id: < Parsed Query >, q_id_2: < Parsed Query 2 >}
    if not normal_query_file:
        query_dict = parse_query_text_file(query_text_file_name)
    else:
        query_dict = parse_normal_query_text_file(query_text_file_name)

    # N -> Total number of collections in the data
    N = len(collection_data_arg)

    for q in query_dict:
        # Iterate through the entire collection
        for doc in collection_data_arg:
            score = 0
            # Iterate through all terms in the query
            for term in query_dict[q].split():
                # Initialize the term frequency and n_k
                # with respect to each term
                # in the query
                t_f, n_k = 0, 0

                if term in indexed_data_arg:
                    if doc in indexed_data_arg[term]:
                        t_f = indexed_data_arg[term][doc]

                    n_k = len(indexed_data_arg[term])

                if t_f > 0 and n_k > 0:
                    score += t_f * math.log(N / n_k)

            tf_idf_scores[q][doc] = score

    sort_dict_according_to_scores(tf_idf_scores)
    return tf_idf_scores


def parse_normal_query_text_file(query_fname):
    """
    Function that is used to parse queries given a text file
    :param query_fname: The name of the file which contains the queries
    :return: a dictionary of the form
    {q_id : <Parsed Query>, q_id_2 : <Parse Query 2>}
    """

    count = 1

    query_dict = {}
    with open(query_fname) as fd:
        for line in fd:
            query_dict[count] = line.rstrip()
            count += 1

    return query_dict


def get_total_number_of_terms_in_collection(collection_data):
    """
    Helper function which returns the total number of words in teh entire
    collection
    :param collection_data: is a dictionary of the form
    # {CACM_file_1 : parsed_tokenized_text_file_1,
    # CACM_file_2 : parsed_tokenized_text_file_2}
    :return: The total numnber of words in the collection
    """

    total_words = 0
    for v in collection_data.values():
        total_words += len(v.split())

    return total_words


def get_query_term_freq_in_collection(term, inverted_index):
    """
    Function which calculates and returns the query term frequency
    in the entire document
    :param term: the term for which we want to calculate the c_q_i for
    :param inverted_index: a dictionary of the form
    {term_1 : {doc_1 : term_1_freq_in_doc_1, doc_2 : term_1_freq_in_doc_2},
    term_2 : {doc_1 : term2_freq_in_doc_1, doc_2 : term2_freq_in_doc_2} .....}
    :return: c_q_i
    """

    # Initialize
    c_q_i = 0
    if term in inverted_index:
        for doc in inverted_index[term]:
            c_q_i += inverted_index[term][doc]

    return c_q_i


def jm_likelihood_scores(collection_data, indexed_data, query_text_file_name,
                         normal_query_file=False):
    """
    Function that calculates the likelihood scores for all the documents
    :param collection_data: A dictionary containing the parsed output of teh entire
    collection. This dictionary is of the form
    # {CACM_file_1 : parsed_tokenized_text_file_1,
    # CACM_file_2 : parsed_tokenized_text_file_2}
    :param indexed_data: The inverted index
    {term_1 : {doc_1 : term_1_freq_in_doc_1, doc_2 : term_1_freq_in_doc_2},
    term_2 : {doc_1 : term2_freq_in_doc_1, doc_2 : term2_freq_in_doc_2} .....}
    :param query_text_file_name: The path to the file containing all the queries
    :param normal_query_file: normal_query_file: Indicates whether the query file is text file
    with no <DOC></DOC> tags( if True) else
    :return: Will return a list made up tuples that are sorted
    [(doc_1, doc_1_score), (doc_2, doc_2_score)....]
    """

    # Given lam
    lam = 0.35

    C = get_total_number_of_terms_in_collection(collection_data)

    print("the total number of words in the collection is ", C)

    # We will maintain a dictionary for the jm scores
    # The format of thsi dictionary will be
    # {query_id : {doc_id, jm_score_doc_1...}...}
    jm_scores = {}

    # Populate the dictionary with empty inner dictionaries
    for i in range(1, 65):
        jm_scores[i] = {}

    # query_dict is of the form
    # {q_id: < Parsed Query >, q_id_2: < Parsed Query 2 >}
    if not normal_query_file:
        query_dict = parse_query_text_file(query_text_file_name)
    else:
        query_dict = parse_normal_query_text_file(query_text_file_name)

    # Maintain the length of all the documents in the dictionary'
    # Lenght of documents do not change
    # Therefore we will store it in a dictionary in the form
    # {doc_name : lenght_of_doc}

    D_dict = {}

    for document, text in collection_data.items():
        D_dict[document] = len(text.split())

    for q in query_dict:
        # Iterate through the entire collection
        for doc in collection_data:
            score = 0
            # Initialize document length as 0
            D = 0

            # Iterate through all terms in the query
            for term in query_dict[q].split():

                # Initialize the query term frequency
                # with respect to each document as 0
                f_qi_D = 0

                # Frequency of this query term in document D
                if term in indexed_data:
                    if doc in indexed_data[term]:
                        f_qi_D = indexed_data[term][doc]

                D = D_dict[doc]

                # Initialize c_qi -> The number of terms the query term occurs
                # in the entire collection
                c_qi = get_query_term_freq_in_collection(term, indexed_data)

                first_term = ((1 - lam) * f_qi_D / D)
                second_term = ((lam * c_qi) / C)
                if first_term + second_term != 0:
                    score += math.log(first_term + second_term)

            jm_scores[q][doc] = score

    sort_dict_according_to_scores(jm_scores)
    return jm_scores



