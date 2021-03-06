
"""
This is the Evaluator module and support the differents action to evaluate the content of the articles
"""
# Import libraries
import pickle
import yaml
from gensim import models, similarities
import os
# Import modules
from Modules.LDA.Cleaner import Cleaner
from Modules.data.manager import Manager

class Evaluator:

    def __init__(self):
        """
        Init function of the class Evaluator
        """
        project_folder = os.getcwd()
        # Load configuration
        with open(project_folder + '/config.yml') as fp:
            config = yaml.load(fp, Loader = yaml.FullLoader)
        fp.close()

        # Database and other resources
        self.DATABASE_PATH = config['paths']['database']
        self.LDA_PATH = config['paths']['lda']
        self.DICTIONARY_PATH = config['paths']['dictionary']
        self.CORPUS_PATH = config['paths']['corpus']

    def get_similarity(self, lda, query_vector):
        """
        Function that get the similarities between a text and the generate LDA model
        :param lda:             The LDA model that the similarities are based on
        :param query_vector:    The text we whant the similarities withe the LDA model
        """
        with open(self.CORPUS_PATH, 'rb') as fp:
            corpus = pickle.load(fp)
            fp.close()

        index = similarities.MatrixSimilarity(lda[corpus])
        sims = index[query_vector]
        return sims

    def get_recommendations(self, query):
        """
        Function that get the recommentations for an article's content based on a LDA model
        :param query:       The article's content from where we want the recommendations
        """
        # Load all respources
        with open(self.DICTIONARY_PATH, 'rb') as fp:
            dictionary = pickle.load(fp)
            fp.close()

        lda = models.LdaModel.load(self.LDA_PATH)

        #clean the query
        cleaner = Cleaner()
        words = dictionary.doc2bow(cleaner.clean_text(query).split())

        #get the top words of the query
        top_words = []
        for word in words:
            top_words.append({"place": word[0],  "word": dictionary[word[0]]})

        #get the similarities matrice between the query and the LDA model
        query_vector = lda[words]
        sims = self.get_similarity(lda, query_vector)
        sims = sorted(enumerate(sims), key=lambda item: -item[1])

        #get the top article that are similar to the query
        idx = 0
        pmids = []
        top = 10
        manager = Manager(self.DATABASE_PATH)
        article_pmid = manager.get_pmids()
        while top > 0:
            articlepmid = article_pmid[sims[idx][0]]
            if articlepmid[0] not in pmids:
                pmids.append(articlepmid[0])
                top -= 1
            idx += 1

        return pmids
