import errno
import os
import pathlib
from collections import defaultdict

from reader import ReadFile
from configuration import ConfigClass
from parser_module import Parse
from indexer import Indexer
from searcher import Searcher
import utils

letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
           'u', 'v', 'w', 'x', 'y', 'z', 'num', '#', '@']
def run_engine(corpus_path, output_path, stemming, queries, num_docs_to_retrieve):
    """

    :return:
    """
    number_of_documents = 0
    num_of_writes = 1
    config = ConfigClass(corpus_path)
    r = ReadFile(corpus_path=config.get__corpusPath())
    p = Parse(stemming)
    indexer = Indexer(config)

    # documents_list = r.read_file(file_name='covid19_07-30.snappy.parquet')  # TODO - handel all files ~50 (can do with from multiprocessing.pool import ThreadPool)
    # documents_list = r.read_file(file_name='covid19_07-08.snappy.parquet')
    # documents_list = r.read_file(file_name='covid19_07-09.snappy.parquet')
    # Iterate over every document in the file
    counter = 0
    names = r.get_files_names_in_dir()
    for name in names:
        documents_list = r.read_file(file_name=str(name))
        for idx, document in enumerate(documents_list):
            parsed_document = p.parse_doc(document)  # parse the document
            number_of_documents += 1
            indexer.add_new_doc(parsed_document)  # index the document data

            counter += 1
            if counter >= 500:
                write_and_clean_buffer(indexer, num_of_writes)
                num_of_writes += 1
                counter = 0
        print('Finished parsing and indexing. Starting to export files')
    write_and_clean_buffer(indexer, num_of_writes)
    num_of_writes += 1
    return num_of_writes




    # utils.save_obj(indexer.inverted_idx, "inverted_idx")
    # utils.save_obj(indexer.postingDict, "post/posting")


def load_index():
    print('Load inverted index')
    inverted_index = utils.load_obj("inverted_idx")
    return inverted_index


def search_and_rank_query(query, inverted_index, k, stemming):
    p = Parse(stemming)
    query_as_list = p.parse_sentence(query)
    searcher = Searcher(inverted_index)
    relevant_docs = searcher.relevant_docs_from_posting(query_as_list)
    ranked_docs = searcher.ranker.rank_relevant_doc(relevant_docs)
    return searcher.ranker.retrieve_top_k(ranked_docs, k)


def write_and_clean_buffer(indexer, write_number):
    # after 500000 docs --> write the postingDict to the Disk

    path = pathlib.Path().absolute()
    save_path = str(path) + '\\posting\\'
    if not os.path.exists(os.path.dirname(save_path)):
        os.makedirs(os.path.dirname(save_path))

    for l in letters:
        filename = str(save_path + l + str(int(write_number)))
        utils.save_obj(indexer.postingDict, filename)

    indexer.postingDict = {}
    indexer.postingDict = defaultdict(list)


def union_posting_files(num_of_writes):
    # inverted_index = utils.load_obj("inverted_idx")
    path = pathlib.Path().absolute()
    save_path = str(path) + '\\posting\\'

    letter_dict = defaultdict(list)
    counter = 1
    for l in letters:
        filename = str(save_path + l + str(counter))
        dict1 = utils.load_obj(filename)
        while counter <= num_of_writes:
            counter += 1
            filename = str(save_path + l + str(counter))
            dict2 = utils.load_obj(filename)
            dict1 = union_2_files(dict1, dict2)
        counter = 1
        filename = str(save_path + l)
        utils.save_obj(dict1, filename)


def union_2_files(dict1, dict2):
    dd = defaultdict(list)
    for d in (dict1, dict2):
        for key, value in d.items():
            dd[key].append(value)
    return dd


def main(corpus_path, output_path, stemming, queries, num_docs_to_retrieve):
    num_of_writes = run_engine(corpus_path, output_path, stemming, queries, num_docs_to_retrieve)
    union_posting_files(num_of_writes)
    query = input("Please enter a query: ")
    k = int(input("Please enter number of docs to retrieve: "))
    inverted_index = load_index()
    for doc_tuple in search_and_rank_query(query, inverted_index, k, stemming):
        print('tweet id: {}, score (unique common words with query): {}'.format(doc_tuple[0], doc_tuple[1]))
