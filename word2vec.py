import time
import gensim
import gzip
import shutil
import numpy


class Word2vec:
    def __init__(self):
        print("start: ", time.asctime(time.localtime(time.time())))
        self.model = gensim.models.KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True)
        # self.model = gensim.models.KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True, limit=2000000)
        print("end: ", time.asctime(time.localtime(time.time())))

    # def open_file(self):
    #     # with gzip.open('C:\\Users\\ASUS\\Desktop\\GoogleNews-vectors-negative300.bin.gz') as f_in:
    #     #     with open('GoogleNews-vectors-negative300.bin', 'wb') as f_out:
    #     #         shutil.copyfileobj(f_in, f_out)


    def get_most_similar_words(self, query_words, k):

        # dog = model['dog']
        # print(dog.shape)
        # print(dog[:10])

        # result = model.most_similar(positive=['woman', 'king'], negative=['man'], topn=1)
        query_words = []
        for word in query_words:
            if word in self.model.wv.vocab:
                query_words.append(word)

        result = self.model.most_similar(positive=query_words, topn=k)
        result = self.model.similar_by_word('home', topn=k)

        # result = model.most_similar(positive=words_list, topn=k)
        print(result)
        return result

    def similarity(self):
        cosine_similarity = numpy.dot(self.model['spain'], self.model['france']) / \
                            (numpy.linalg.norm(self.model['spain']) * numpy.linalg.norm(self.model['france']))
        print("start: ", time.asctime(time.localtime(time.time())))
        c=0
        for i in range(10000000):
            self.model.similarity('france', 'spain')
            c += 1
            if c == 1000000:
                print(i)
                print("c= ", c, time.asctime(time.localtime(time.time())))
                c = 0
        print("end: ", time.asctime(time.localtime(time.time())))

        # print(self.model.wv['computer'])

word2vec = Word2vec()
# word2vec.get_most_similar_words(['woman', 'home'], 3)
# w1 ='france'
# w2 ='spain'
word2vec.similarity()