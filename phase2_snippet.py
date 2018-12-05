import json
import math
import traceback
from os.path import exists
import os
import operator
from bs4 import BeautifulSoup
from colorama import *


cwd = os.getcwd()
CACM = path = os.path.join(cwd,'cacm/cacm')
DOC_SCORE_PATH = path = os.path.join(cwd,'')
text_dict = {}

def getSigList(query_list, text_list):
    sig_list = []
    for term in text_list:
        if term in query_list:
            sig_list.append(1)
        else:
            sig_list.append(0)
    return sig_list

def generate_snippet(query,file_name):

    query_list = query.split()
    text_list = text_dict[file_name].split()
    window_len = min(20, len(text_list))
    num_win = len(text_list) / window_len
    significance_list = getSigList(query_list,text_list)

    maxSig = 0
    maxIndex = 0
    for i in range(math.floor(num_win)):
        sig = (sum(significance_list[i:(i+window_len)]))**2 / window_len
        if maxSig < sig:
            maxSig = sig
            maxIndex = i
    print(window_len,maxIndex,maxSig)
    # print(text_list)
    # print(significance_list)
    snippet_list = text_list[maxIndex:maxIndex+window_len]
    for term in snippet_list:
        if term in query_list:
            print("\033[45;30m"+term+"\033[m",end=' ')
        else:
            print(term,end=' ')
    print("\n")

def get_list_of_files(query_id):
        file_list = []
        doc_score_file = open(DOC_SCORE_PATH+"/bm_25_scores.txt")
        for line in doc_score_file.readlines():
            params = line.split()
            if params[0] == str(query_id):
                file_list.append(params[2])
        doc_score_file.close()
        return file_list


def snippet_generation():
    global text_dict

    query_file = open('parsed_query_dict.json', 'r')
    query_dict = json.load(query_file)

    parsed_tokenized_file = open("parsed_tokenized_json_output.json",'r')
    text_dict = json.load(parsed_tokenized_file)

    for query_id, query  in query_dict.items():
        list_of_files = get_list_of_files(query_id)
        for file_name in list_of_files:
            generate_snippet(query, file_name)

snippet_generation()
