import numpy as np
from gensim import matutils
from numpy import dot, array
from ..config import APIDOC_WIKI_FASTTEXT_MODEL_STORE_PATH, JAVADOC_GLOBAL_NAME
from gensim.models import FastText

"""
The methods are copied from gensim.models.keyedvectors.Doc2VecKeyedVectors in gensim for compute the vector similarity
"""


class VectorUtil:

    def __init__(self, model) -> None:
        self.model = model

    @staticmethod
    def similarity(vector_1, vector_2):
        """Compute cosine similarities between one vector and another vector.

            Parameters
            ----------
            vector_1 : numpy.ndarray
                    Vector from which similarities are to be computed, expected shape (dim,).
            vector_2 : numpy.ndarray
                    Vector from which similarities are to be computed, expected shape (dim,).

            Returns
            -------
            numpy.ndarray
            Contains cosine distance between `vector_1` and `vector_2`

        """

        return dot(matutils.unitvec(vector_1), matutils.unitvec(vector_2))

    @staticmethod
    def cosine_similarities(vector_1, vectors_all):
        """Compute cosine similarities between one vector and a set of other vectors.

        Parameters
        ----------
        vector_1 : numpy.ndarray
            Vector from which similarities are to be computed, expected shape (dim,).
        vectors_all : list of numpy.ndarray
            For each row in vectors_all, distance from vector_1 is computed, expected shape (num_vectors, dim).

        Returns
        -------
        numpy.ndarray
            Contains cosine distance between `vector_1` and each row in `vectors_all`, shape (num_vectors,).

        """
        norm = np.linalg.norm(vector_1)
        all_norms = np.linalg.norm(vectors_all, axis=1)
        dot_products = dot(vectors_all, vector_1)
        similarities = dot_products / (norm * all_norms)
        return similarities

    @staticmethod
    def n_similarity(vector_list_1, vector_list_2):
        """Compute cosine similarity between two sets of vectors.

        Parameters
        ----------
        vector_list_1 : list of numpy vector
        vector_list_2: list of numpy vector

        Returns
        -------
        numpy.ndarray
            Similarities between vector_list_1 and vector_list_2.

        """
        if not (len(vector_list_1) and len(vector_list_1)):
            raise ZeroDivisionError(
                'At least one of the passed list is empty.')

        return dot(matutils.unitvec(array(vector_list_1).mean(axis=0)),
                   matutils.unitvec(array(vector_list_2).mean(axis=0)))

    @staticmethod
    def get_weight_mean_vec(vector_list, weight_list = None):
        """
        get the average word2vec for list of str
        :param weight_list:
        :param vector_list:
        :return: np.array()
        """
        # todo: add a empty zero vectors result.
        # weight_sum = np.sum(weight_list)
        # normal_weight_list = []
        # for w in weight_list:
        #     normal_weight_list.append(w / weight_sum)
        # weight_list=normal_weight_list
        
        x = np.matrix(vector_list)
        if weight_list is None:
            avg_vector = np.average(x, axis=0)
        else:
            avg_vector = np.average(x, axis=0, weights=weight_list)
        avg_vector = avg_vector.getA()[0]
        return avg_vector

    def get_sentence_avg_vector(self, sentence: str):
        tokens = sentence.split()
        vector_list = []
        for token in tokens:
            try:
                vector_list.append(self.model.wv[token])
            except KeyError:
                continue
        return VectorUtil.get_weight_mean_vec(vector_list)

    def get_word_similarity(self, word1, word2):
        return self.model.similarity(word1, word2)

    @staticmethod
    def compute_idf_weight_dict(total_num, number_dict):
        index_2_key_map = {}

        index = 0

        count_list = []
        for key, count in number_dict.items():
            index_2_key_map[index] = key
            count_list.append(count)
            index = index + 1

        a = np.array(count_list)
        ## smooth, in case the divide by zero error
        a = np.log((total_num + 1) / (a + 1))
        result = {}

        for index, w in enumerate(a):
            key = index_2_key_map[index]
            result[key] = w

        return result
