import random
import networkx as nx
import numpy as np

from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence
from util.concept_map.common import get_latest_hyper_concept_map
from util.config import NODE2VEC_RANDOM_WALK_STORE_PATH, NODE2VEC_MODEL_STORE_PATH


class Node2VecGraph():
    def __init__(self, nx_G, is_directed, p, q):
        self.G = nx_G
        self.is_directed = is_directed
        self.p = p
        self.q = q

    def node2vec_walk(self, walk_length, start_node):
        """
        Simulate a random walk starting from start node.
        """
        G = self.G
        alias_nodes = self.alias_nodes
        alias_edges = self.alias_edges
        walk = [start_node]

        while len(walk) < walk_length:
            cur = walk[-1]
            cur_nbrs = sorted(G.neighbors(cur))
            if len(cur_nbrs) > 0:
                if len(walk) == 1:
                    walk.append(
                        cur_nbrs[alias_draw(alias_nodes[cur][0], alias_nodes[cur][1])])
                else:
                    prev = walk[-2]
                    next = cur_nbrs[alias_draw(alias_edges[(prev, cur)][0],
                                               alias_edges[(prev, cur)][1])]
                    walk.append(next)
            else:
                break

        return walk

    def simulate_walks(self, num_walks, walk_length):
        """
        Repeatedly simulate random walks from each node.
        """
        G = self.G
        walks = []
        nodes = list(G.nodes())
        print('Walk iteration:')
        for walk_iter in range(num_walks):
            print(str(walk_iter + 1), '/', str(num_walks))
            random.shuffle(nodes)
            for node in nodes:
                walks.append(self.node2vec_walk(
                    walk_length=walk_length, start_node=node))

        return walks

    def get_alias_edge(self, src, dst):
        """
        Get the alias edge setup lists for a given edge.
        """
        G = self.G
        p = self.p
        q = self.q

        unnormalized_probs = []
        for dst_nbr in sorted(G.neighbors(dst)):
            if dst_nbr == src:
                unnormalized_probs.append(G[dst][dst_nbr]['weight'] / p)
            elif G.has_edge(dst_nbr, src):
                unnormalized_probs.append(G[dst][dst_nbr]['weight'])
            else:
                unnormalized_probs.append(G[dst][dst_nbr]['weight'] / q)
        norm_const = sum(unnormalized_probs)
        normalized_probs = [
            float(u_prob) / norm_const for u_prob in unnormalized_probs]

        return alias_setup(normalized_probs)

    def preprocess_transition_probs(self):
        """
        Preprocessing of transition probabilities for guiding the random walks.
        """
        G = self.G
        is_directed = self.is_directed

        alias_nodes = {}
        for node in G.nodes():
            unnormalized_probs = [G[node][nbr]['weight']
                                  for nbr in sorted(G.neighbors(node))]
            norm_const = sum(unnormalized_probs)
            normalized_probs = [
                float(u_prob) / norm_const for u_prob in unnormalized_probs]
            alias_nodes[node] = alias_setup(normalized_probs)

        alias_edges = {}
        triads = {}

        if is_directed:
            for edge in G.edges():
                alias_edges[edge] = self.get_alias_edge(edge[0], edge[1])
        else:
            for edge in G.edges():
                alias_edges[edge] = self.get_alias_edge(edge[0], edge[1])
                alias_edges[(edge[1], edge[0])] = self.get_alias_edge(
                    edge[1], edge[0])

        self.alias_nodes = alias_nodes
        self.alias_edges = alias_edges

        return


def alias_setup(probs):
    """
    Compute utility lists for non-uniform sampling from discrete distributions.
    Refer to https://hips.seas.harvard.edu/blog/2013/03/03/the-alias-method-efficient-sampling-with-many-discrete-outcomes/
    for details
    """
    K = len(probs)
    q = np.zeros(K)
    J = np.zeros(K, dtype=np.int)

    smaller = []
    larger = []
    for kk, prob in enumerate(probs):
        q[kk] = K * prob
        if q[kk] < 1.0:
            smaller.append(kk)
        else:
            larger.append(kk)

    while len(smaller) > 0 and len(larger) > 0:
        small = smaller.pop()
        large = larger.pop()

        J[small] = large
        q[large] = q[large] + q[small] - 1.0
        if q[large] < 1.0:
            smaller.append(large)
        else:
            larger.append(large)

    return J, q

    
def alias_draw(J, q):
    """
    Draw sample from a non-uniform discrete distribution using alias sampling.
    """
    K = len(J)

    kk = int(np.floor(np.random.rand() * K))
    if np.random.rand() < q[kk]:
        return kk
    else:
        return J[kk]


class Node2VecTrainer:
    def __init__(self, doc_name):
        self.doc_name = doc_name
        self.g = get_latest_hyper_concept_map(doc_name)
        self.nx_G_instance = None
        self.node_num = len(list(self.g.nodes))
        self.init_unweight_graph()
            

    def init_unweight_graph(self):
        node_ids = [str(node) for node in self.g.nodes]
        relation_pairs = [(str(src), str(tgt))
                          for src, tgt in list(self.g.edges())]
        print("node num=%d" % self.node_num)
        print("relation num=%d" % len(relation_pairs))
        G = nx.DiGraph()
        G.add_nodes_from(node_ids)
        G.add_edges_from(relation_pairs, weight=1.0)
        # todo: a relation weight support
        self.nx_G_instance = G
        print("init graph trainer by unweight relations")

    def generate_random_path(self, directed=False, p=1, q=1, num_walks=10, walk_length=80):
        print("start generate graph random path")

        G = Node2VecGraph(self.nx_G_instance, directed, p, q)
        G.preprocess_transition_probs()
        walks = G.simulate_walks(num_walks, walk_length)
        # todo: may be load all into memory has problem?
        with open(NODE2VEC_RANDOM_WALK_STORE_PATH[self.doc_name], 'w') as write_f:
            for walk in walks:
                path_str = " ".join([str(item) for item in walk])
                write_f.writelines('%s\n' % (path_str))

        print("complete generate graph random path")

    def train(self, dimensions=100, workers=12):
        """
        train the graph vector from rw_path
        :param rw_path_store_path: the random walk for one graph
        :param model_path: the output word2vec model path
        :param dimensions: the dimensions of word2vec
        :param workers: the num of pipeline training
        :return:
        """
        print("save graph2vec training")

        # Learn embeddings by optimizing the Skipgram objective using SGD.
        w2v = Word2Vec(LineSentence(NODE2VEC_RANDOM_WALK_STORE_PATH[self.doc_name]),
                       size=dimensions, min_count=0, sg=1, workers=workers)
        w2v.save(NODE2VEC_MODEL_STORE_PATH[self.doc_name])
        print("save graph2vec to %s" %
              NODE2VEC_MODEL_STORE_PATH[self.doc_name])
        return w2v
