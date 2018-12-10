Environment:
OS : Windows
Python version : 3.6
Lucene version : 4.7


-------------------

General Note: Unzip the given folder. A new folder called IR_Project will be extracted.
This is our root folder.

General Note: For all the outputs that will be generated we have stored the output filenames in the json file
"all_paths.json". We read the path for the filenames from this .json file

General Note:
-> Instead of cleaning the corpus, generating queries by parsing the cacm.query.txt file, generating inverted index, generating positional inverted index for
each run, we have created .json files for eachof the above tasks.
Wheneever required, we load these json files

Note: Some of the tasks require the inverted indices and cleaned corpus to be loaded first.
We will mention the prior requirements in the Readme below.

General Note: All the CACM collection( 3204 documents, cacm.query.txt, cacm.rel.txt, common_words, cacm_stem.query.txt, cacm_stem.txt) are stored in a folder called
as test_collection under the IR_Project directory ( IR_Project\test_collection)

-------------------

Phase 1:
Task 1:
	- (PRE-REQUISITE) Cleaning the corpus( punctuation handling, case-folding etc..)
	>>> python create_collection_data_dict.py -j all_paths.json
	
	OUTPUT -> This will create a file called "cleaned_corpus.json" in the folder IR_Project\Outputs\Cleaned_Corpus\
	This file represents the cleaned corpus and is of the form
	{doc_id : cleaned_contents}
	
	- (PRE-REQUISITE) Creating inverted index
	>>> python create_index.py -j all_paths.json
	
	OUTPUT -> Will create a .json file IR_Project\Outputs\Inverted_Index\inverted_index_corpus.json
	The format of the inverted index is {term: { doc : freq_of_term}}
	
	
	1.1 GENERATING BM25 SCORES
	>>> python task_1_main.py -j all_paths.json -m bm25
	
	OUTPUT -> This will generate a text file in the path IR_Project\Outputs\Phase1\Task1\bm_25_scores.txt
	
	1.2 GENERATING TF-IDF SCORES
	>>> python task_1_main.py -j all_paths.json -m tf_idf
	
	OUTPUT -> This will generate a text file in the path IR_Project\Outputs\Phase1\Task1\tf_idf_scores.txt
	
	1.3 GENERATING JM-QLM SCORES
	NOTE: This will take around 5-7 minutes to complete
	>>> python task_1_main.py -j all_paths.json -m jm_qlm
	
	OUTPUT -> Will generate a .txt file in the path IR_Project\Outputs\Phase1\Task1\jm_qlm_scores.txt
	
	
	1.4 LUCENE
	- (PRE-REQUISITE) Lucene expects the corpus to be in .txt foramt and also the a query to index and rank documents
	- Note: Run this python file from the IR_Project Directory
	- Note: Before running this python file, the cleaned_corpus.json should be created( Created initially in Task1, steps above)
	
	>>> python pre_lucene.py -c Outputs\Cleaned_Corpus\cleaned_corpus.json -q test_collection\cacm.query.txt -co Outputs\Phase1\Task1\Lucene\ -qo all_queries.txt
	
	OUTPUT -> Will create 3204 text documents in the folder IR_Project\Outputs\Phase1\Task1\Lucene\ and also a text file called as all_queries.txt
	( this is a text file conatining all the queries written into a file line by line)
	
	
	- Create a new Java Project
	    Add the three following jars into your project's list of referenced libraries:
		a. lucene-core-VERSION.jar
		b. lucene-queryparser-VERSION.jar
		c. lucene-analyzers-common-VERSION.jar
		
	- Run HW4 .java
		-> The command prompt will ask for path to the folder where Lucene index will be created. Give any valid path in the system.
		-> NOTE: All the index files in this folder should be deleted for the subsequent run of HW4.java
		-> The command prompt will ten ask to enter the ptah to text documents that you want to index
		   ( Enter the path system_path + IR_Project\Outputs\Phase1\Task1\Lucene\ ). All 3204 documents will be indexed.
		   - NOTE: THE system_path is the path where the IR_Project folder is stored.
		   For instance, in my system the IR_project was stored under:
		   E:\All_NEU_Stuff\NEU_Courses\IR\IR_Project\Outputs\Phase1\Task1\Lucene\ to this
		   
		  
		   Therefore I will enter the above path
		   
		-> press q to stop indexing
		-> The command prompt will then ask for path to the text file where all the queries are stored
		( Enter the system path to the all_queries.txt file)
		
		For instance, in my sytem the all_queries.txt file was stored under:
		E:\All_NEU_Stuff\NEU_Courses\IR\IR_Project\all_queries.txt
		
		Therefore, I will enter the aboved path on my command prompt
		
	- OUTPUT
	-> A Lucene_Score_Outputs.txt will be create from the directory in whih the Java project was created
	NOTE: We have included the same in the Outputs folder(E:\All_NEU_Stuff\NEU_Courses\IR\IR_Project\Outputs\Phase1\Task1\Lucene_Score_Outputs.txt)
	
	
		

Task 2: PSEUDO RELEVANCE FEEDBACK
	- >>> python pseudo_relevance_feedback.py -m bm25 -j all_paths.json
	
	OUTPUT -> Will create .txt file at IR_Project\Outputs\Phase1\Task2\pseudo_relevance_feedback_scores.txt
		  


Task 3:
	2.1 STOPPING
	- (PRE-REQUISITE) Creating inverted index with out considering words present in the commoin_words file
	>>> python create_index.py -j all_paths.json -c True
	The format of the inverted index is {term: { doc : freq_of_term}}
	
	
	OUTPUT -> Will generate a .json at the path IR_Project\Outputs\Phase1\Task3A\stopped_queries_output.json
	
	3.1.1 GENERATING BM25 SCORES USING STOPPING
	>>> python task_3_a.py -j all_paths.json -m bm25
	
	OUTPUT -> Will generate a text file at the path \Outputs\Phase1\Task3A\bm25_stopped_queries.txt
	
	3.1.2 GENERATING TF-IDF SCORES USING STOPPING
	>>> python task_3_a.py -j all_paths.json -m tf_idf
	
	OUTPUT -> Will generate a text file at the path \Outputs\Phase1\Task3A\tf_idf_stopped_queries.txt
	
	3.1.3 GENERATING JM-QLM SCORES USING STOPPING
	>>> python task_3_a.py -j all_paths.json -m jm_qlm
	
	OUTPUT -> Will generate a text file at the path \Outputs\Phase1\Task3A\jm_qlm_stopped_queries.txt
	
	
	
	3.2 STEMMING
	
	- (PRE-REQUISITE) Need to parse the stemmed collection of the corpus and create an inverted index out of the stemmed corpus
	>>> python stemming_task_clean_corpus.py -j all_paths.json
	
	OUTPUT -> Will create a cleaned version of the stemmed corpus at IR_Project\Outputs\Phase1\\Task3B\\stemmed_corpus_collection.json
	       -> Will create an inverted index out the stemmed corpus at IR_Project\Outputs\Phase1\Task3B\stemmed_inverted_index.json 
	
	
	3.2.1 GENERATING BM25 SCORES FOR STEMMED COLLECTION
	>>> python task_3_b.py -m bm25 -j all_paths.json
	
	OUTPUT -> Will generate a text file at IR_Project\Outputs\Phase1\Task3B\bm25_stem_queries.txt
	
	3.2.2 GENERATING TF-IDF SCORES FOR STEMMED COLLECTION
	>>> python task_3_b.py -m tf_idf -j all_paths.json
	
	OUTPUT -> Will generate a text file at IR_Project\Outputs\Phase1\Task3B\tf_idf_stem_queries.txt
	
	
	3.2.3 GENERATING JM-QLM SCORES FOR STEMMED COLLECTION
	
	>>> python task_3_b.py -j all_paths.json -m jm_qlm
	
	OUTPUT -> Will generate a text file at IR_Project\Outputs\Phase1\Task3B\jm_qlm_stem_queries.txt
	

	

-------------------------------------------------------------------------------------------

EXTRA CREDITS

BEST MATCH
>>> python best_match.py -j all_paths.json -m best_match

OUTPUT -> Will generate a .txt file at the path IR_Project\Outputs\Extra_Credits\best_match_scores.txt


EXACT MATCH
(PRE-REQUISITE) -> Exact match and Ordered_Proximity_Match use Positional inverted index
Therefore we need to generate such an index before calling exact_match.py or ordered_proximity_match.py


>>> python generate_position_based_index.py -j all_paths.json

OUTPUT -> Will generate a .json file at the IR_Project\Outputs\Extra_Credits\positional_index.json


EXACT MATCH
>>> python exact_match.py -j all_paths.json -m exact_match

OUTPUT -> Will generate a .txt file at the path IR_Project\Outputs\Extra_Credits\exact_match_scores.txt


ORDERED PROXIMITY MATCH
>>> python ordered_proximity_match.py -j all_paths.json -N 5 -m ordered_proxmimity_match

Here N is the window size
OUTPUT -> Will generate a .txt file at the path IR_Project\Outputs\Extra_Credits\extra_credit_output_ordered_match.txt


-------------------------------------------------------------------------------------------
