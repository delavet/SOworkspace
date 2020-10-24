#给图中的类结点增加一个社区讨论热度的属性
import networkx as nx
from util.concept_map.common import get_latest_concept_map
from util.constant import class_level_node_types, NodeAttributes
from util.mysql_access.posts import DBPosts
from util.config import LATEST_CONCEPT_MAP_PATH


if __name__ == "__main__":
    concept_map = get_latest_concept_map('javadoc')
    Ntype_attributes = nx.get_node_attributes(concept_map, 'Ntype')
    class_nodes = [node for node in concept_map.nodes if node in Ntype_attributes and Ntype_attributes[node] in class_level_node_types]
    posts_db = DBPosts()
    for node in class_nodes:
        concept_name = concept_map[node][NodeAttributes.NAME]
        community_frequency = posts_db.statistic_concept_frequency_v0(concept_name, 'javaPosts')
        concept_map.nodes[relative_path][NodeAttributes.COMMUNITY_FREQ] = community_frequency
    nx.write_gexf(concept_map, LATEST_CONCEPT_MAP_PATH['javadoc'])
