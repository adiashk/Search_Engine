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

from word2vec import Word2vec

letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
           'u', 'v', 'w', 'x', 'y', 'z', 'num', '#', '@']


def run_engine(corpus_path, output_path, stemming, queries, num_docs_to_retrieve, word2vec):
    """

    :return:
    """
    print("start: ", time.asctime(time.localtime(time.time())))
    number_of_documents = 0
    num_of_writes = 1
    config = ConfigClass(corpus_path)
    r = ReadFile(corpus_path=config.get__corpusPath())
    p = Parse(stemming)
    indexer = Indexer(config, word2vec)
    # documents_list = r.read_file(file_name='covid19_07-30.snappy.parquet')  # TODO - handel all files ~50 (can do with from multiprocessing.pool import ThreadPool)

    # Iterate over every document in the file
    counter = 0
    names = r.get_files_names_in_dir()
    for name in names:
        documents_list = r.read_file(file_name=str(name))
        for idx, document in enumerate(documents_list):
            parsed_document = p.parse_doc(document)  # parse the document
            if parsed_document == {}:
                continue
            # parsed_document.add_doc_vector(word2vec)
            # parsed_document.get_mean_vector(word2vec)
            number_of_documents += 1

            indexer.add_new_doc(parsed_document, num_of_writes)  # index the document data
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
        if l == 'num':
            dic_letters = {key: indexer.postingDict[key] for key in indexer.postingDict.keys() if key[0].isdigit()}
        else:
            dic_letters = {key: indexer.postingDict[key] for key in indexer.postingDict.keys() if key[0].lower() == l}
        utils.save_obj(dic_letters, filename)

    indexer.postingDict = {}
    indexer.postingDict = defaultdict(list)

    save_path = str(path) + '\\documents\\'
    if not os.path.exists(os.path.dirname(save_path)):
        os.makedirs(os.path.dirname(save_path))
    filename = str(save_path + str(int(write_number)))
    utils.save_obj(indexer.documents_dict, filename)

    indexer.documents_dict = {}
    indexer.documents_dict = defaultdict(list)

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


# def union_2_files(dict1, dict2):
#     dd = defaultdict(list)
#     for d in (dict1, dict2):
#         for key, value in d.items():
#             dd[key].extend(value)
#     return dd

def union_2_files(dict1, dict2):
    dd = defaultdict(list)
    for d in (dict1, dict2):
        for key, value in d.items():
            if key[0].isupper(): #key is uppercase
                if key.lower() in dd: #there is uppercase in dict so add value to lower
                    dd[key.lower()].extend(value)
                else: #add uppercase to dict, there is no lower
                    dd[key].extend(value)
            elif key[0].upper() in dd: #key is lowercase and there is uppercase in dict
                dd[key] = value #add new lower key to dict
                if key.capitalize() in dd: #if lowercase
                    dd[key].extend(dd[key.capitalize()]) #add value capital to lower
                    del dd[key.capitalize()]
                else: #add value upper to lower
                    dd[key].extend(dd[key.upper()])
                    del dd[key.upper()]
            else: #new key
                dd[key].extend(value)
    return dd


def load_index():
    print('Load inverted index')
    inverted_index = utils.load_obj("inverted_idx")
    return inverted_index


def search_and_rank_query(queries_list, inverted_index, num_docs_to_retrieve, stemming, word2vec):
    p = Parse(stemming)
    answers = []
    for q in queries_list:
        query = p.parse_query(q)
        searcher = Searcher(inverted_index, stemming, word2vec)
        relevant_docs = searcher.relevant_docs_from_posting(query, word2vec)
        ranked_docs = searcher.ranker.rank_relevant_doc(relevant_docs, query, word2vec)
        answers.extend(searcher.ranker.retrieve_top_k(ranked_docs, num_docs_to_retrieve))
    return answers


def read_queries(queries):
    with open(queries) as f:
        content = f.readlines()
    # you may also want to remove whitespace characters like `\n` at the end of each line
    content = [x.strip() for x in content]
    return content



def main(corpus_path, output_path, stemming, queries, num_docs_to_retrieve):
    word2vec = Word2vec()
    # word2vec.model.wv.vector_size = 100

    # word2vec.save("word2vec.model")
    # word2vec.model.vectors.shape[1] = 100
    # num_of_writes = run_engine(corpus_path, output_path, stemming, queries, num_docs_to_retrieve, word2vec)
    num_of_writes =6
    union_posting_files(num_of_writes)
    print("finish union posting files: ", time.asctime(time.localtime(time.time())))
    if type(queries) != list:
        queries = read_queries(queries)

    # query = input("Please enter a query: ")
    # k = int(input("Please enter number of docs to retrieve: "))
    inverted_index = load_index()
    rank_query = search_and_rank_query(queries, inverted_index, num_docs_to_retrieve, stemming, word2vec)
    for doc_tuple in rank_query:
        print('tweet id: {}, score (unique common words with query): {}'.format(doc_tuple[0], doc_tuple[1]))
