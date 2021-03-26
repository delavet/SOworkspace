import os

JAVADOC_GLOBAL_NAME = 'javadoc'
WINDOWS = 'WINDOWS'
MAC = 'MACINTOSH'
UBUNTU = 'UBUNTU'
CURRENT_PLATFORM = UBUNTU


# 判断当前运行的项目基础路径及运行平台
if os.path.exists('C:/workspace/SOworkspace'):
    base_dir = 'C:/workspace/SOworkspace'
    CURRENT_PLATFORM = WINDOWS
elif os.path.exists('/media/dell/disk/yinh/SOworkspace'):
    base_dir = '/media/dell/disk/yinh/SOworkspace'
    CURRENT_PLATFORM = UBUNTU
elif os.path.exists('/User/yinhang/workspace/SOworkspace'):
    base_dir = '/User/yinhang/workspace/SOworkspace'
    CURRENT_PLATFORM = MAC
else:
    base_dir = '/media/dell/disk/yinh/SOworkspace'

DOC_NAME_TO_SO_TAG = {
    JAVADOC_GLOBAL_NAME: '<java>'
}

# 分析用的APIdoc的路径
APIDOC_PATH = f'{base_dir}/apidocs/'
# 最后把最后成品concept map会放在这里，目前啥也没有
CONCEPT_MAP_STORE_PATH = f'{base_dir}/data/concept_map/'

JAVADOC_CONCEPT_MAP_FILE_NAME = 'concept_map_javadoc.gexf'
JAVADOC_PATH = os.path.join(APIDOC_PATH, 'javadocs')
TEMP_FILE_STORE_PATH = f'{base_dir}/data/cache/'
# 生成concept map后图数据存储的路径，在开发中会变化
LATEST_CONCEPT_MAP_PATH = {
    JAVADOC_GLOBAL_NAME: f'{base_dir}/backup/concept_map_javadoc20210312.gexf'
}

# API概念之间只包含社区共现关系的map，称为community map
LATEST_COMMUNITY_MAP_PATH = {
    JAVADOC_GLOBAL_NAME: f'{base_dir}/data/community_data/java/community_map_javadoc20210312.gexf'
}

# 带有domain term和wiki term拓展实体的concept map
LATEST_HYPER_CONCEPT_MAP_PATH = {
    JAVADOC_GLOBAL_NAME: f'{base_dir}/data/concept_map/hyper_concept_map_javaodc20210325.pkl'
}

# 复旦的API知识图谱

FUDAN_CONCEPT_MAP_PATH = {
    JAVADOC_GLOBAL_NAME: f'{base_dir}/data/concept_map/fudan_jdk_graph.pkl'
}

# 于2021年3月12日封存的concept map
SEALED_CONCEPT_MAP_20210312_PATH = {
    JAVADOC_GLOBAL_NAME: f'{base_dir}/backup/concept_map_javadoc20200801.gexf'
}

# 为实现HERMES mk1需要分析文档语义，因此将所有概念描述抽出并存放与此
# 2020.12.18 文档语义分析已经从HERMES剥离，代号将进行进一步考虑，HERMES专注于concept map抽取
APIDOC_DESCRIPTION_STORE_PATH = {
    JAVADOC_GLOBAL_NAME: f'{base_dir}/data/apidoc_description/javadoc_descriptions.json'
}

# 2021.2.5 重启将API实体与WIKI实体的链接工作，代号DEUS-X-MACHINA
# 存储初步的DOMAIN TERM抽取结果，为API和其描述文本中抽取的domain term的映射
INITIAL_API_DOMAIN_TERM_MAP_STORE_PATH = {
    JAVADOC_GLOBAL_NAME: f'{base_dir}/data/apidoc_description/javadoc_init_api_term_map.json'
}
INITIAL_API_DOMAIN_TERM__SENTENCE_MAP_STORE_PATH = {
    JAVADOC_GLOBAL_NAME: f'{base_dir}/data/apidoc_description/javadoc_init_api_term_sentence_map.json'
}
# 存储初步抽取后得到的所有的domain term列表
API_DOMAIN_TERM_STORE_PATH = {
    JAVADOC_GLOBAL_NAME: f'{base_dir}/data/apidoc_description/javadoc_domain_terms.json'
}
# 2021.2.6 目前的fuse方案是根据fudan的论文进行的纯基于近义词检测的fuse
# 存储清理与fuse之后API与fuse的domain term的对应关系
FUSED_API_DOMAIN_TERM_MAP_STORE_PATH = {
    JAVADOC_GLOBAL_NAME: f'{base_dir}/data/apidoc_description/javadoc_fused_api_term_map.json'
}
# 存储清理与fuse之后domain term与API的对应关系（即和上面这个是反过来的映射）
FUSED_DOMAIN_TERM_API_MAP_STORE_PATH = {
    JAVADOC_GLOBAL_NAME: f'{base_dir}/data/apidoc_description/javadoc_fused_term_api_map.json'
}
# 存储清理与fuse后所有的domain term以及其alias关系
FUSED_DOMAIN_TERM_STORE_PATH = {
    JAVADOC_GLOBAL_NAME: f'{base_dir}/data/apidoc_description/javadoc_fused_domain_terms.json'
}

# 为从侧面验证HERMES mk1的效果，将bing中对概念的描述进行了存储，可以用于后期对比
# 2020.12.18 基于bing的验证方案已经废弃
BING_API_CONCEPT_STORE_PATH = {
    JAVADOC_GLOBAL_NAME: {
        'sample': f'{base_dir}/data/bing_description/javadoc_bing_descriptions_sample.pkl',
        'large': f'{base_dir}/data/bing_description/javadoc_bing_descriptions.pkl'
    }
}

# 为实现HERMES mk1需要尝试在文档描述中抽取wiki中的常见concept，因此将wikipedia的内容存储路径纪录在此
# 2020.12.18 wikipedia链接可能尝试完全不同的方法与数据集（可能是wikidata），HERMES已不包含wiki部分，仅涉及concept map构建
WIKIPEDIA_CONCEPT_STORE_PATH = {
    'text': f'{base_dir}/data/wikipedia_concepts/text_content/'
}

# 为完成EUREKA，首先需要将数据库中与某个领域相关的post存储下来。为了效率将文件拆分成很多存储在一个目录下
SO_POSTS_STORE_PATH = {
    # java：使用<java>标签定位到的post
    # 注意只有SO_POSTS_STORE_PATH没有用JAVADOC_GLOBAL_NAME做key，因为为了更好表现是用的什么tag把相关post爬下来的
    '<java>': f'{base_dir}/data/so_posts/java/'
}

# SO的post因为太多，所以是以pkl形式分段存放的，这里保存一个文件存放关于每个thread在哪个文件第几个的信息，以方便快速找到一个thread
SO_POSTS_SEGMENT_INFO_STORE_PATH = {
    JAVADOC_GLOBAL_NAME: f'{base_dir}/data/so_posts/javadoc_so_segment_info.json'
}

# 不同SDK文档对应的官网根URL纪录
APIDOC_ROOT_URL = {
    JAVADOC_GLOBAL_NAME: 'docs.oracle.com'
}

# 不同SDK文档API URL的正则匹配表示，因为仅用根URL还会匹配到教程啥的很难搞
APIDOC_API_URL_REGEX_PATTERN = {
    JAVADOC_GLOBAL_NAME: r'^(http://|https://)?docs.oracle.com.+api.*$'
}

# EUREKA为post中的NER任务，此任务需要训练集，该项为训练集存储目录
EUREKA_DATASET_STORE_PATH = {
    JAVADOC_GLOBAL_NAME: f'{base_dir}/data/EUREKA_trainset/java'
}

# 2021.2.18：初版的EUREKA数据集不好，已经过人工重新标注，放在下面目录中，由EUREKA 2.1处理
EUREKA_REFINED_LABEL_STORE_PATH = {
    JAVADOC_GLOBAL_NAME: f'{base_dir}/data/EUREKA_refine_label'
}

# EUREKA使用的数据集文件名，之后会进一步分离成为训练集和测试集
EUREKA_FULL_DATASET_FILE_NAME = 'ner_dataset.json'
EUREKA_TRAIN_SET_FILE_NAME = 'ner_trainset.json'
EUREKA_TEST_SET_FILE_NAME = 'ner_testset.json'
#EUREKA_VALID_SET_FILE_NAME = 'ner_validset.json'

# ANEMONE为post中的NEL任务，此任务需要训练集，该项为训练集存储目录
ANEMONE_DATASET_STORE_PATH = {
    JAVADOC_GLOBAL_NAME: f'{base_dir}/data/ANEMONE_dataset/java'
}
# ANEMENE使用的数据集文件名，之后会进一步分离成训练集和测试集，ANEMONE使用的多个方法中，数据形式可能不同，因此还根据方法不同划分不同数据集

# general
ANEMONE_GENERAL_DATASET_FILE_NAME = 'general_nel_dataset.json'
# for xgboost
ANEMONE_XGBOOST_DATASET_FILE_NAME = 'xgboost_nel_dataset.json'
ANEMONE_XGBOOST_TRAIN_SET_FILE_NAME = 'xgboost_nel_trainset.json'
ANEMONE_XGBOOST_TEST_SET_FILE_NAME = 'xgboost_nel_testset.json'
# for basic BERT MATCH
ANEMONE_BERT_DATASET_FILE_NAME = 'bert_nel_dataset.json'
ANEMONE_BERT_TRAIN_SET_FILE_NAME = 'bert_nel_trainset.json'
ANEMONE_BERT_TEST_SET_FILE_NAME = 'bert_nel_testset.json'

EZA_PIPELINE_DATA_STORE_PATH = {
    JAVADOC_GLOBAL_NAME: f'{base_dir}/data/EZA_pipeline/java'
}
EZA_PIPELINE_INPUT_FILE_NAME = 'EZA_input.json'

API_ELASTIC_DOC_MAP_STORE_PATH = {
    JAVADOC_GLOBAL_NAME: f'{base_dir}/data/cache/api_elastic_doc_map.json'
}

# EZA PIPELINE的预测结果存储路径，用这个来分析社区关系
MENIA_WHOLE_PREDICTION_STORE_PATH = {
    # 只有windows和ubuntu平台的机器上保留了这个预测数据，每次ubuntu机器预测完成后要记得手动同步数据 windows上来
    JAVADOC_GLOBAL_NAME: '/media/dell/disk/yinh/torch/ANEMONE/whole_simple_prediction/filterd_predictions.json' if CURRENT_PLATFORM == UBUNTU else 'C:/workspace/SOworkspace/data/server_data/ANEMONE_prediction/filterd_predictions.json'
}

# 上边的预测数据是thread和API的字典，这个文件则是反过来的API和thread对应的字典，为了给HOMURA提供服务
API_THREAD_ID_MAP_STORE_PATH = {
    JAVADOC_GLOBAL_NAME: f'{base_dir}/data/community_data/java/API-thread_id_map.json'
}

COMMUNITY_FREQUENCY_STORE_PATH = {
    JAVADOC_GLOBAL_NAME: f'{base_dir}/data/community_data/java/community_frequency.json'
}

COMMUNITY_RECORD_STORE_PATH = {
    JAVADOC_GLOBAL_NAME: f'{base_dir}/data/community_data/java/community_record.json'
}

# MENIA初步推荐得到的作为每个社区的学习入口的帖子，将推荐结果储存在下面路径
COMMUNITY_RECOMMEND_ENTRY_THREADS_STORE_PATH = {
    JAVADOC_GLOBAL_NAME: f'{base_dir}/data/community_data/java/recommended_learning_entry_threads.json'
}

OPENKE_TRAIN2ID_STORE_PATH = {
    JAVADOC_GLOBAL_NAME: f'{base_dir}/data/community_data/java/openke/train2id.txt'
}

OPENKE_VALID2ID_STORE_PATH = {
    JAVADOC_GLOBAL_NAME: f'{base_dir}/data/community_data/java/openke/valid2id.txt'
}

OPENKE_TEST2ID_STORE_PATH = {
    JAVADOC_GLOBAL_NAME: f'{base_dir}/data/community_data/java/openke/test2id.txt'
}

OPENKE_ENTITY2ID_STORE_PATH = {
    JAVADOC_GLOBAL_NAME: f'{base_dir}/data/community_data/java/openke/entity2id.txt'
}

OPENKE_RELATION2ID_STORE_PATH = {
    JAVADOC_GLOBAL_NAME: f'{base_dir}/data/community_data/java/openke/relation2id.txt'
}

#专门为HOMURA提供服务的数据，存储每个社群中推荐先学习的API，基本就是一个重新排序的COMMUNITY_RECORD
HOMURA_COMMUNITY_API_RECOMMEND_STORE_PATH = {
    JAVADOC_GLOBAL_NAME: f'{base_dir}/data/community_data/java/homura_community_api_recommend.json'
}

HYBRID_WORD2VEC_CORPUS_STORE_PATH = {
    JAVADOC_GLOBAL_NAME: f'{base_dir}/data/MACHINA_dataset/hybrid_word2vec_corpus_javadoc.txt'
}

# 只有接入nirvash mk7时有效，在使用时务必接入硬盘
WIKIDUMP_PATH = {
    'title': 'G:/wikidump/article_titles.txt',
    'article': 'G:/wikidump/articles_in_plain_text.txt'
}

# 用apidoc和wiki联合训练出来的fasttext model，选fasttext是怕有词汇表里没有的单词
APIDOC_WIKI_FASTTEXT_MODEL_STORE_PATH = {
    JAVADOC_GLOBAL_NAME: f'{base_dir}/model/java/apidoc_wiki_fasttext.model'
}

API_SHORT_DESCRIPTION_FASTTEXT_VECTOR_STORE_PATH = {
    JAVADOC_GLOBAL_NAME: f'{base_dir}/data/apidoc_description/javadoc_api_desc_fasttext_vector.pkl'
}

# MYSQL属性
Mysql_addr = "162.105.16.191"
Mysql_user = "root"
Mysql_password = "root"
Mysql_dbname_sotorrent = "sotorrent"

pre_generated_views_in_Mysql = {
    '<java>': 'JavaPosts'
}

# Elasticsearch属性
Elasticsearch_host = 'localhost'
Elasticsearch_port = 9200
