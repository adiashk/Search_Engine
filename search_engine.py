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
import time

letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
           'u', 'v', 'w', 'x', 'y', 'z', 'num', '#', '@']


def run_engine(corpus_path, output_path, stemming, queries, num_docs_to_retrieve):
    """

    :return:
    """
    print("start: ", time.asctime(time.localtime(time.time())))
    number_of_documents = 0
    num_of_writes = 1
    config = ConfigClass(corpus_path)
    r = ReadFile(corpus_path=config.get__corpusPath())
    p = Parse(stemming)
    indexer = Indexer(config)

    # documents_list = r.read_file(file_name='covid19_07-30.snappy.parquet')  # TODO - handel all files ~50 (can do with from multiprocessing.pool import ThreadPool)

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
            if counter >= 500000:
                write_and_clean_buffer(indexer, num_of_writes)
                counter = 0
                print("finish parser & index number: ",num_of_writes, " At: ", time.asctime(time.localtime(time.time())))
                num_of_writes += 1
        #print('Finished parsing and indexing. Starting to export files')
    write_and_clean_buffer(indexer, num_of_writes)
    print("finish parser & index: ", time.asctime(time.localtime(time.time())))
    utils.save_obj(indexer.inverted_idx, "inverted_idx")
    print("finish save index: ", time.asctime(time.localtime(time.time())))

    return num_of_writes


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

    counter = 1
    for l in letters:
        filename = str(save_path + l + str(counter))
        dict1 = utils.load_obj(filename)
        while counter < num_of_writes:
            counter += 1
            filename = str(save_path + l + str(counter))
            dict2 = utils.load_obj(filename)
            dict1 = union_2_files(dict1, dict2)
        counter = 1
        filename = str(save_path + l)
        utils.save_obj(dict1, filename)
        # TODO- check upper and lower letters in union


def union_2_files(dict1, dict2):
    dd = defaultdict(list)
    for d in (dict1, dict2):
        for key, value in d.items():
            dd[key].extend(value)
    return dd


def load_index():
    print('Load inverted index')
    inverted_index = utils.load_obj("inverted_idx")
    return inverted_index


def search_and_rank_query(query, inverted_index, num_docs_to_retrieve, stemming):
    p = Parse(stemming)
    query_list = []
    for q in query:
        query_list.append(p.parse_query(q))
    for q in query_list:
        searcher = Searcher(inverted_index, stemming)
        relevant_docs = searcher.relevant_docs_from_posting(q)
        ranked_docs = searcher.ranker.rank_relevant_doc(relevant_docs)
    return searcher.ranker.retrieve_top_k(ranked_docs, num_docs_to_retrieve)


def read_queries(queries):
    with open(queries) as f:
        content = f.readlines()
    # you may also want to remove whitespace characters like `\n` at the end of each line
    content = [x.strip() for x in content]
    return content


def main(corpus_path, output_path, stemming, queries, num_docs_to_retrieve):
    num_of_writes = run_engine(corpus_path, output_path, stemming, queries, num_docs_to_retrieve)
    union_posting_files(num_of_writes)
    print("finish union posting files: ", time.asctime(time.localtime(time.time())))
    if type(queries) != list:
        queries = read_queries(queries)
    # query = input("Please enter a query: ")
    # k = int(input("Please enter number of docs to retrieve: "))
    inverted_index = load_index()
    rank_query = search_and_rank_query(queries, inverted_index, num_docs_to_retrieve, stemming)
    for doc_tuple in rank_query:
        print('tweet id: {}, score (unique common words with query): {}'.format(doc_tuple[0], doc_tuple[1]))
