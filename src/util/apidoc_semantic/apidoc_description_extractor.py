from collections import OrderedDict
from typing import Text
import networkx as nx
import os
import re
import time
import logging
import pickle

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from ..config import *
from ..constant import *
from ..concept_map.common import get_relative_path_from_href

browser = webdriver.Chrome()


def __collect_concept_description_javadoc():
    """
    收集javadoc中的所有module、package、class级别概念、method、field的描述文本，并存储在一个dict中进行序列化
    """
    global browser
    concept_map = nx.read_gexf(LATEST_CONCEPT_MAP_PATH['javadoc'])
    Ntype_attributes = nx.get_node_attributes(concept_map, 'Ntype')

    descriptions = OrderedDict()

    # 抽取module结点的描述
    module_nodes = [node for node in concept_map.nodes if node in Ntype_attributes and Ntype_attributes[node] == 'MODULE']
    for module_node in module_nodes:
        local_href = concept_map.nodes[module_node]['local_href']
        browser.get(local_href)
        time.sleep(0.04)
        content_container = browser.find_element(By.XPATH, r'//div[@class="contentContainer"]')
        try:
            description_block = content_container.find_element(By.XPATH, r'.//section[@class="moduleDescription"]/div[@class="block"]')
            description_text = description_block.text
            try:
                appendation_title = description_block.find_element(By.XPATH, r'./h2').text
                description_text = description_text[0:description_text.find(appendation_title)]
            except:
                pass
            descriptions[module_node] = description_text
        except NoSuchElementException:
            pass

    logging.info('=== module description collected ===')
    with open(os.path.join(TEMP_FILE_STORE_PATH, "javadoc_description_module.pkl"), 'wb') as wf:
        pickle.dump(descriptions, wf)
    
    # 抽取package结点描述
    package_nodes = [node for node in concept_map.nodes if node in Ntype_attributes and Ntype_attributes[node] == 'PACKAGE']
    for package_node in package_nodes:
        local_href = concept_map.nodes[package_node]['local_href']
        browser.get(local_href)
        time.sleep(0.04)
        content_container = browser.find_element(By.XPATH, r'//div[@class="contentContainer"]')
        try:
            description_block = content_container.find_element(By.XPATH, r'.//section[@class="packageDescription"]/div[@class="block"]')
            description_text = description_block.text
            try:
                appendation_title = description_block.find_element(By.XPATH, r'./h2').text
                description_text = description_text[0:description_text.find(appendation_title)]
            except:
                pass
            descriptions[package_node] = description_text
        except NoSuchElementException:
            pass
    
    logging.info('=== package description collected ===')
    with open(os.path.join(TEMP_FILE_STORE_PATH, "javadoc_description_module_package.pkl"), 'wb') as wf:
        pickle.dump(descriptions, wf)

    #抽取class level结点描述
    class_level_nodes = [node for node in concept_map.nodes if node in Ntype_attributes and Ntype_attributes[node] in class_level_node_types]
    for class_level_node in class_level_nodes:
        local_href = concept_map.nodes[class_level_node]['local_href']
        browser.get(local_href)
        time.sleep(0.04)
        content_container = browser.find_element(By.XPATH, r'//div[@class="contentContainer"]')
        try:
            description_block = content_container.find_element(By.XPATH, r'.//section[@class="description"]/div[@class="block"]')
            description_text = description_block.text
            try:
                appendation_title = description_block.find_element(By.XPATH, r'./h2').text
                description_text = description_text[0:description_text.find(appendation_title)]
            except:
                pass
            descriptions[class_level_node] = description_text
        except NoSuchElementException:
            pass
        
        #为所有成员添加描述
        class_successors = concept_map.succ[class_level_node]
        class_members = [node for node in class_successors if concept_map[class_level_node][node]['Etype'] == EdgeType.INCLUDE]
        for class_member in class_members:
            try:
                member_id = re.search(r'(?<=#).+$', get_relative_path_from_href(concept_map.nodes[class_member]['local_href'])).group()
                member_section = content_container.find_element(By.XPATH, f'.//a[@id="{member_id}"]/../..')
                member_description_block = member_section.find_element(By.XPATH, r'./div[@class="block"]')
                member_description = member_description_block.text
                descriptions[class_member] = member_description
            except:
                print(class_member)
    return descriptions


def collect_concept_description(doc_name = JAVADOC_GLOBAL_NAME):
    switch = {
        JAVADOC_GLOBAL_NAME : __collect_concept_description_javadoc
    }
    return switch[doc_name]()