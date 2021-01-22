import os
from util.config import ANEMONE_DATASET_STORE_PATH, ANEMONE_XGBOOST_DATASET_FILE_NAME, ANEMONE_XGBOOST_TRAIN_SET_FILE_NAME, ANEMONE_XGBOOST_TEST_SET_FILE_NAME, JAVADOC_GLOBAL_NAME, TEMP_FILE_STORE_PATH
from util.nel.basic_ml.feature_extraction import feature_extract__edit_distance, feature_extract__context_cooccur
from util.concept_map.common import get_latest_concept_map
from bs4 import BeautifulSoup
from tqdm import tqdm

import networkx as nx
import json


concept_map = get_latest_concept_map()
Ntype_attributes = nx.get_node_attributes(concept_map, 'Ntype')
href_attributes = nx.get_node_attributes(concept_map, 'local_href')
description_attributes = nx.get_node_attributes(concept_map, 'description')
api_entities = [
    node for node in concept_map if node in Ntype_attributes and node in href_attributes]


def __get_html_text_execept_code(html: str) -> str:
    soup = BeautifulSoup(html, 'lxml')
    for pre in soup.find_all('pre'):
        pre.extract()
    return soup.text


def process_general_case(case: dict):
    '''
    将一个general的NEL case处理成xgboost的数据集格式
    general数据样例：
    ```json
    {
      "mention": "Class.getDeclaredConstructor()",
      "entity": "api/java.base/java/io/ObjectInputStream.GetField.html",
      "label": 0,
      "context": {
        "Id": 3036777,
        "Body": "<p>In java, can I use a class object to dynamically instantiate classes of that type?</p>&#xA;&#xA;<p>i.e. I want some function like this.</p>&#xA;&#xA;<pre><code>Object foo(Class type) {&#xA;    // return new object of type 'type'&#xA;}&#xA;</code></pre>&#xA;",
        "Tags": "<java><class><new-operator>",
        "Title": "instantiate class from class object",
        "Score": 19,
        "ViewCount": 23679,
        "FavoriteCount": 1,
        "Answers": [
            {
            "Body": "<p>In Java 9 and afterward, if there's a declared zero-parameter (\"nullary\") constructor, you'd use <a href=\"https://docs.oracle.com/en/java/javase/12/docs/api/java.base/java/lang/Class.html#getDeclaredConstructor(java.lang.Class...)\" rel=\"nofollow noreferrer\"><code>Class.getDeclaredConstructor()</code></a> to get it, then call <a href=\"https://docs.oracle.com/en/java/javase/12/docs/api/java.base/java/lang/reflect/Constructor.html#newInstance(java.lang.Object...)\" rel=\"nofollow noreferrer\"><code>newInstance()</code></a> on it:</p>&#xA;&#xA;<pre><code>Object foo(Class type) throws InstantiationException, IllegalAccessException, InvocationTargetException {&#xA;    return type.getDeclaredConstructor().newInstance();&#xA;}&#xA;</code></pre>&#xA;&#xA;<p>Prior to Java 9, you would have used <a href=\"https://docs.oracle.com/en/java/javase/12/docs/api/java.base/java/lang/Class.html#newInstance()\" rel=\"nofollow noreferrer\"><code>Class.newInstance</code></a>:</p>&#xA;&#xA;<pre><code>Object foo(Class type) throws InstantiationException, IllegalAccessException {&#xA;    return type.newInstance();&#xA;}&#xA;</code></pre>&#xA;&#xA;<p>...but it was deprecated as of Java 9 because it threw any exception thrown by the constructor, even checked exceptions, but didn't (of course) declare those checked exceptions, effectively bypassing compile-time checked exception handling. <code>Constructor.newInstance</code> wraps exceptions from the constructor in <code>InvocationTargetException</code> instead.</p>&#xA;&#xA;<p>Both of the above assume there's a zero-parameter constructor. A more robust route is to go through <a href=\"https://docs.oracle.com/en/java/javase/12/docs/api/java.base/java/lang/Class.html#getDeclaredConstructors()\" rel=\"nofollow noreferrer\"><code>Class.getDeclaredConstructors</code></a> or <a href=\"https://docs.oracle.com/en/java/javase/12/docs/api/java.base/java/lang/Class.html#getConstructors()\" rel=\"nofollow noreferrer\"><code>Class.getConstructors</code></a>, which takes you into using the Reflection stuff in the <a href=\"https://docs.oracle.com/en/java/javase/12/docs/api/java.base/java/lang/reflect/package-summary.html\" rel=\"nofollow noreferrer\"><code>java.lang.reflect</code></a> package, to find a constructor with the parameter types matching the arguments you intend to give it.</p>&#xA;",
            "Score": 30,
            "Accepted": true
            },
            {
            "Body": "<p>Use:</p>&#xA;&#xA;<pre><code>type.newInstance()&#xA;</code></pre>&#xA;&#xA;<p>For creating an instance using the empty costructor, or use the method type.getConstructor(..) to get the relevant constructor and then invoke it.</p>&#xA;",
            "Score": 2,
            "Accepted": false
            },
            {
            "Body": "<p>Yes, it is called Reflection.  you can use the Class <a href=\"http://java.sun.com/javase/6/docs/api/java/lang/Class.html#newInstance%28%29\" rel=\"nofollow noreferrer\"><code>newInstance()</code></a> method for this.</p>&#xA;",
            "Score": 1,
            "Accepted": false
            },
            {
            "Body": "<p>use newInstance() method.</p>&#xA;",
            "Score": -1,
            "Accepted": false
            }
        ],
        "Links": [
            "https://docs.oracle.com/en/java/javase/12/docs/api/java.base/java/lang/Class.html#getDeclaredConstructor(java.lang.Class...)",
            "https://docs.oracle.com/en/java/javase/12/docs/api/java.base/java/lang/reflect/Constructor.html#newInstance(java.lang.Object...)",
            "https://docs.oracle.com/en/java/javase/12/docs/api/java.base/java/lang/Class.html#newInstance()",
            "https://docs.oracle.com/en/java/javase/12/docs/api/java.base/java/lang/Class.html#getDeclaredConstructors()",
            "https://docs.oracle.com/en/java/javase/12/docs/api/java.base/java/lang/Class.html#getConstructors()",
            "https://docs.oracle.com/en/java/javase/12/docs/api/java.base/java/lang/reflect/package-summary.html",
            "http://java.sun.com/javase/6/docs/api/java/lang/Class.html#newInstance%28%29"
        ]
      }
    },
    ```
    '''
    global api_entities
    global description_attributes
    feature_edit_distance = feature_extract__edit_distance(
        case['mention'], case['entity'])
    try:
        entity_context = description_attributes[case['entity']]
    except KeyError:
        entity_context = ''
    mention_context = case['context']['Title']
    question = case['context']['Body']
    answers = [ans['Body'] for ans in case['context']['Answers']]
    mention_context += '. ' + __get_html_text_execept_code(question)
    for answer in answers:
        mention_context += '. ' + __get_html_text_execept_code(answer)
    feature_context_cooccur = feature_extract__context_cooccur(
        mention_context, entity_context)
    return feature_edit_distance, feature_context_cooccur, case['label']


def generate_xgboost_dataset_from_general_dataset(general_dataset_file_path, target_doc=JAVADOC_GLOBAL_NAME):
    xgboost_dataset = []
    with open(general_dataset_file_path, "r", encoding="utf-8") as rf, open(os.path.join(ANEMONE_DATASET_STORE_PATH[target_doc], ANEMONE_XGBOOST_DATASET_FILE_NAME), 'w', encoding="utf-8") as wf:
        general_dataset = json.load(rf)
        for case in tqdm(general_dataset):
            feature_ed, feature_co, label = process_general_case(case)
            xgboost_dataset.append([feature_ed, feature_co, label])
        json.dump(xgboost_dataset, wf)


if __name__ == "__main__":
    # general数据集还没生成完成，完成后替换成完成版本，目前使用cache的部分数据集
    generate_xgboost_dataset_from_general_dataset(os.path.join(
        TEMP_FILE_STORE_PATH, 'general_nel_dataset_from_post_0_to_posts_1.pkl.json'))
