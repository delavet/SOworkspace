from util.apidoc_semantic.node2vec import Node2VecTrainer
from util.config import JAVADOC_GLOBAL_NAME
'''
为计算节点在结构上的相似度，训练node2vec
'''


def train_node2vec(doc_name: str = JAVADOC_GLOBAL_NAME):
    trainer = Node2VecTrainer(doc_name)
    trainer.generate_random_path()
    trainer.train()


if __name__ == "__main__":
    train_node2vec()