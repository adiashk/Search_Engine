import pathlib
import re

from parser_module import Parse
from ranker import Ranker
import utils
from word2vec import Word2vec


class Searcher:

    def __init__(self, inverted_index, stemming, word2vec):
        """
        :param inverted_index: dictionary of inverted index
        """
        self.parser = Parse(stemming)
        self.ranker = Ranker()
        self.inverted_index = inverted_index
        self.word2vec = word2vec


    def relevant_docs_from_posting(self, query, word2vec):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query: query
        :return: dictionary of relevant documents.
        """
        # TODO - send only words from query, the rest of the word search alone
        # t = ' '
        # query_text = t.join(query)
        # query_words = re.compile(r"[a-zA-Z]+").findall(query_text)
        # query_words = []
        # for q in query:
        #     if all(x.isalpha() or x.isspace() for x in q):
        #         query_words.append(q)

        # similar_words = word2vec.get_most_similar_words(query, 3)
        # query_and_similar = []
        # query_and_similar.extend(query)
        # query_and_similar.extend(similar_words)
        # posting = utils.load_obj("posting")

        posting = {}
        relevant_docs = {}
        query_set = set(query)
        path = pathlib.Path().absolute()
        save_path = str(path) + '\\posting\\'
        temp_letter = ''
        for term in query_set:
            letter = term[0].lower()
            if temp_letter != letter:  # not load again
                temp_letter = letter
                if letter.isdigit():
                    filename = str(save_path + 'num')
                    posting = utils.load_obj(filename)
                else:
                    filename = str(save_path + letter)
                    posting = utils.load_obj(filename)

            try:  # an example of checks that you have to do
                docs_list = posting[term]  # [(tweet_id, amount_in_tweet, num_of_writes), ...()]
                for doc in docs_list:
                    #TODO- search term.lower & term.upper
                    tweet_id = doc[0]
                    if tweet_id not in relevant_docs.keys():
                        relevant_docs[tweet_id] = (1, doc[2])
                    else:
                        relevant_docs[tweet_id][0] += 1

            except:
                pass

        relevant_docs = sorted(relevant_docs.items(), key=lambda x: x[1], reverse=True)

        relevant_docs = dict(list(relevant_docs.items())[0: 2000])
        return relevant_docs




