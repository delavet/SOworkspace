import os

JAVADOC_GLOBAL_NAME = 'javadoc'

# 判断当前运行的项目基础路径
if os.path.exists('C:/workspace/SOworkspace'):
    base_dir = 'C:/workspace/SOworkspace'
elif os.path.exists('/media/dell/disk/yinh/SOworkspace'):
    base_dir = '/media/dell/disk/yinh/SOworkspace'
elif os.path.exists('/User/yinhang/Desktop/workspace/SOworkspace'):
    base_dir = '/User/yinhang/Desktop/workspace/SOworkspace'
else:
    base_dir = '/media/dell/disk/yinh/SOworkspace'

# 分析用的APIdoc的路径
APIDOC_PATH = f'{base_dir}/apidocs/'
# 最后把最后成品concept map会放在这里，目前啥也没有
CONCEPT_MAP_STORE_PATH = f'{base_dir}/data/concept_map/'

JAVADOC_CONCEPT_MAP_FILE_NAME = 'concept_map_javadoc.gexf'
JAVADOC_PATH = os.path.join(APIDOC_PATH, 'javadocs')
TEMP_FILE_STORE_PATH = f'{base_dir}/data/cache/'
# 生成concept map后图数据存储的路径，在开发中会变化
LATEST_CONCEPT_MAP_PATH = {
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
# 存储所有的domain term列表
API_DOMAIN_TERM_STORE_PATH = {
    JAVADOC_GLOBAL_NAME: f'{base_dir}/data/apidoc_description/javadoc_domain_terms.json'
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

# MYSQL属性
Mysql_addr = "162.105.16.191"
Mysql_user = "root"
Mysql_password = "root"
Mysql_dbname_sotorrent = "sotorrent"

pre_generated_views_in_Mysql = {
    '<java>': 'JavaPosts'
}
