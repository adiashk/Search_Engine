from collections import defaultdict

class Indexer:

    def __init__(self, config, word2vec):
        self.inverted_idx = defaultdict(int)
        self.postingDict = defaultdict(list)  # value = [(tweet_id, count_in_doc),...,(id, count)]
        self.named_entity_idx = defaultdict(list)
        self.config = config
        self.documents_dict = defaultdict(list)
        self.extra_stop_words = ['rt', 'www', 'http', 'https', 'tco', 'didnt', 'dont']
        self.word2vec = word2vec

    def add_new_doc(self, document, num_of_writes):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """

        document_dictionary = document.term_doc_dictionary
        # Go over each term in the doc
        for term in document_dictionary.keys():
            if term in self.extra_stop_words or term.lower() in self.extra_stop_words:
                continue
            try:
                # Update inverted index and posting
                if term not in self.inverted_idx.keys():
                    if term == '':
                        print(term)
                    if term[0].isupper():
                        if term.lower() in self .inverted_idx.keys():  # this is upper and there was lower before -> insert as lower
                            new_term = term.lower()
                            self.inverted_idx[new_term] += 1
                            self.postingDict[new_term].append((document.tweet_id, document_dictionary[term], num_of_writes))
                        else:   # this is upper and there wad noting before -> insert as upper
                            self.inverted_idx[term] = 1
                            self.postingDict[term].append((document.tweet_id, document_dictionary[term], num_of_writes))

                    elif term[0].islower(): # this is lower and there wad upper before -> insert as lower and move what was at upper
                        if term.capitalize() in self.inverted_idx.keys():
                            self.inverted_idx[term] = self.inverted_idx[term.capitalize()] + 1
                            self.postingDict[term] = self.postingDict[term.capitalize()]
                            del self.inverted_idx[term.capitalize()]
                            del self.postingDict[term.capitalize()]

                        else:  # this is lower and there wad noting before -> insert as lower
                            self.inverted_idx[term] = 1
                    else:
                        self.inverted_idx[term] = 1
                        self.postingDict[term].append((document.tweet_id, document_dictionary[term], num_of_writes))
                else:  # term was in before in the same way
                    self.inverted_idx[term] += 1
                    self.postingDict[term].append((document.tweet_id, document_dictionary[term], num_of_writes))
                    # TODO- save  details about doc

            except:
                print('problem with the following key {}'.format(term[0]))
        self.add_named_entity(document, num_of_writes)
        self.add_doc_to_dict(document)

    def add_named_entity(self, document, num_of_writes):
        document_named_entity = document.named_entity
        if document_named_entity is not None:
            for name in document_named_entity:
                if name in self.extra_stop_words or name.lower() in self.extra_stop_words:
                    continue
                if name in self.named_entity_idx.keys():  # recognize as named_entity before
                    self.inverted_idx[name] += 1
                    self.postingDict[name].append((document.tweet_id, document_named_entity[name],  num_of_writes))
                    self.postingDict[name].extend(self.named_entity_idx[name])

                else: # new possible entity
                    self.named_entity_idx[name].append((document.tweet_id, document_named_entity[name]))

    def add_doc_to_dict(self, document):
        # doc_words_list = self.get_doc_words(document, word2vec)
        get_doc_vector = self.get_doc_vector(document)
        self.documents_dict[document.tweet_id].append((document.amount_of_unique_words, document.max_tf, get_doc_vector))

    def get_doc_words(self, document):
        doc_words_list = []
        for term in document.term_doc_dictionary:
            doc_words_list.append(term)
        return doc_words_list


    def get_doc_vector(self, document):
        doc_vec = 0
        counter = 0
        avg_vec = []
        for term in document.term_doc_dictionary:
            if term in self.word2vec.model.wv.vocab:
                doc_vec += self.word2vec.model[str(term)]
                counter += 1
            if counter > 0:
                avg_vec = doc_vec / counter
        return avg_vec



    # def get_mean_vector(self,word2vec):
    #     # remove out-of-vocabulary words
    #     words = [word for word in self.term_doc_dictionary if word in word2vec.model.vocab]
    #     if len(words) >= 1:
    #         self.doc_dict[self.tweet_id] = numpy.mean(word2vec.model[words], axis=0)