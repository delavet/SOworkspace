import networkx as nx
import os
import re
import time
import logging

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .common import get_relative_path_from_href
from ..config import *
from ..constant import *

browser = webdriver.Chrome()


def __pass_if_exist(cm: nx.DiGraph, node_type, mode='new_generate'):
    if mode == 'new_generate':
        return False
    Ntype_attributes = nx.get_node_attributes(cm, 'Ntype')
    for node in cm.nodes:
        if Ntype_attributes[node] == node_type:
            return True
    return False


def __add_meta_node_javadoc(concept_map: nx.DiGraph):
    if __pass_if_exist(concept_map, NodeType.SCOPE):
        return
    concept_map.add_node(
        'javase',
        Ntype=NodeType.SCOPE,
        description='The Java Platform, Standard Edition (Java SE) APIs define the core Java platform for general-purpose computing. These APIs are in modules whose names start with java.'
    )
    concept_map.add_node(
        'jdk',
        Ntype=NodeType.SCOPE,
        description='The Java Development Kit (JDK) APIs are specific to the JDK and will not necessarily be available in all implementations of the Java SE Platform. These APIs are in modules whose names start with jdk.'
    )
    #concept_map.add_edge('javase', 'jdk', Etype = EdgeType.RELATED)
    #concept_map.add_edge('jdk', 'javase', Etype = EdgeType.RELATED)


def __add_module_node_javadoc(concept_map: nx.DiGraph):
    if __pass_if_exist(concept_map, NodeType.MODULE):
        return
    global browser
    javadoc_index_path = os.path.join(JAVADOC_PATH, 'api/index.html')
    browser.get(javadoc_index_path)
    overview_tabpanel = browser.find_element(By.ID, 'overviewSummary_tabpanel')
    module_table = overview_tabpanel.find_element(By.XPATH, './table')
    trs = module_table.find_elements(By.XPATH, './tbody/tr')
    modules = []
    for tr in trs:
        th_a = tr.find_element(By.XPATH, './th/a')
        td_div = tr.find_element(By.XPATH, './td/div')
        modules.append(
            (
                th_a.text,
                th_a.get_attribute('href'),
                td_div.text
            )
        )
    for module_name, module_href, module_description in modules:
        concept_map.add_node(module_name)
        concept_map.nodes[module_name]['name'] = module_name
        concept_map.nodes[module_name]['Ntype'] = NodeType.MODULE
        concept_map.nodes[module_name]['local_href'] = module_href
        concept_map.nodes[module_name]['description'] = module_description
        relative_path = get_relative_path_from_href(module_href)
        concept_map.nodes[module_name]['path'] = relative_path
        if re.match('^java', module_name):
            concept_map.add_edge(
                'javase', module_name,
                Etype=EdgeType.INCLUDE
            )
        elif re.match('^jdk', module_name):
            concept_map.add_edge(
                'jdk', module_name,
                Etype=EdgeType.INCLUDE
            )


def __add_package_node_javadoc(concept_map: nx.DiGraph):
    if __pass_if_exist(concept_map, NodeType.PACKAGE):
        return
    global browser
    Ntype_attributes = nx.get_node_attributes(concept_map, 'Ntype')
    for node in concept_map.nodes:
        if Ntype_attributes[node] == NodeType.PACKAGE:
            return
    module_nodes = [
        node for node in concept_map.nodes if Ntype_attributes[node] == NodeType.MODULE]
    for node in module_nodes:
        local_href = concept_map.nodes[node]['local_href']
        browser.get(local_href)
        time.sleep(0.05)
        packages = []
        block_sections = browser.find_elements(
            By.XPATH, r'//li[@class="blockList"]/section')
        for block_section in block_sections:
            block_title = block_section.find_element(By.XPATH, './h2')
            if block_title.text != 'Packages':
                continue
            package_groups = block_section.find_elements(
                By.XPATH, './div/table')
            for package_group in package_groups:
                relation_name = package_group.find_element(
                    By.XPATH, './caption/span[1]').text
                if relation_name != 'Exports':
                    continue
                trs = package_group.find_elements(By.XPATH, './tbody/tr')
                for tr in trs:
                    th_a = tr.find_element(By.XPATH, './/a')
                    td_div = tr.find_element(By.XPATH, './td')
                    packages.append(
                        (
                            th_a.text,
                            th_a.get_attribute('href'),
                            td_div.text
                        )
                    )
        for package_name, package_href, package_description in packages:
            concept_map.add_node(package_name)
            concept_map.nodes[package_name]['name'] = package_name
            concept_map.nodes[package_name]['Ntype'] = NodeType.PACKAGE
            concept_map.nodes[package_name]['local_href'] = package_href
            concept_map.nodes[package_name]['description'] = package_description
            relative_path = get_relative_path_from_href(package_href)
            concept_map.nodes[package_name]['path'] = relative_path
            concept_map.add_edge(
                node, package_name,
                Etype=EdgeType.EXPORT
            )
        pass


def __add_class_level_node_javadoc(concept_map: nx.DiGraph):
    if __pass_if_exist(concept_map, NodeType.CLASS):
        return
    '''
    添加所有的类级结点：接口、类、异常、错误、注解
    '''
    global browser
    Ntype_attributes = nx.get_node_attributes(concept_map, 'Ntype')
    package_nodes = [
        node for node in concept_map.nodes if node in Ntype_attributes and Ntype_attributes[node] == NodeType.PACKAGE]
    for package_node in package_nodes:
        local_href = concept_map.nodes[package_node]['local_href']
        browser.get(local_href)
        time.sleep(0.05)
        blocks = browser.find_elements(By.XPATH, r'//li[@class="blockList"]')
        for block in blocks:
            content_table = block.find_element(By.XPATH, r'.//table')
            if content_table is None:
                continue
            block_title = content_table.find_element(
                By.XPATH, r'./caption').text.lower()
            temps = []
            trs = content_table.find_elements(By.XPATH, r'./tbody/tr')
            for tr in trs:
                th_a = tr.find_element(By.XPATH, './/a')
                td_div = tr.find_element(By.XPATH, './td')
                temps.append(
                    (
                        th_a.text,
                        th_a.get_attribute('href'),
                        td_div.text
                    )
                )
            for name, href, description in temps:
                relative_path = get_relative_path_from_href(href)
                concept_map.add_node(relative_path)
                concept_map.nodes[relative_path]['name'] = name
                if 'interface' in block_title:
                    concept_map.nodes[relative_path]['Ntype'] = NodeType.INTERFACE
                elif 'class' in block_title:
                    concept_map.nodes[relative_path]['Ntype'] = NodeType.CLASS
                elif 'enum' in block_title:
                    concept_map.nodes[relative_path]['Ntype'] = NodeType.ENUM
                elif 'exception' in block_title:
                    concept_map.nodes[relative_path]['Ntype'] = NodeType.EXCEPTION
                elif 'error' in block_title:
                    concept_map.nodes[relative_path]['Ntype'] = NodeType.ERROR
                elif 'annotation' in block_title:
                    concept_map.nodes[relative_path]['Ntype'] = NodeType.ANNOTATION
                concept_map.nodes[relative_path]['local_href'] = href
                concept_map.nodes[relative_path]['description'] = description
                concept_map.nodes[relative_path]['path'] = relative_path
                concept_map.add_edge(
                    package_node, relative_path,
                    Etype=EdgeType.INCLUDE
                )


def __add_member_node_to_class_level_node_javadoc(concept_map: nx.DiGraph, node_type: str):
    '''
    add memeber nodes to node type : class, error, exception, interface, enum
    method, field, constructor
    '''

    global browser
    Ntype_attributes = nx.get_node_attributes(concept_map, 'Ntype')
    class_nodes = [
        node for node in concept_map.nodes if node in Ntype_attributes and Ntype_attributes[node] == node_type]
    for class_node in class_nodes:
        try:
            local_href = concept_map.nodes[class_node]['local_href']
            browser.get(local_href)
            time.sleep(0.05)
            content_container = browser.find_element(
                By.XPATH, r'//div[@class="contentContainer"]')
            try:
                summary_section = content_container.find_element(
                    By.XPATH, r'.//section[@class="summary"]')
                blocks = summary_section.find_elements(
                    By.XPATH, r'.//li[@class="blockList"]')
            except Exception as e:
                print('node ', class_node, ': nothing found')
                continue
            for block in blocks:
                block_title = block.find_element(
                    By.XPATH, r'.//h2').text.lower()
                try:
                    member_summary_div = block.find_element(
                        By.XPATH, r'.//div[@class="memberSummary"]')
                except NoSuchElementException as no_element:
                    continue
                member_summary_table = member_summary_div.find_element(
                    By.XPATH, r'.//table')
                trs = member_summary_table.find_elements(
                    By.XPATH, r'./tbody/tr')
                temps = []
                for tr in trs:
                    th_span = tr.find_element(
                        By.XPATH, r'.//span[@class="memberNameLink"]')
                    th_a = th_span.find_element(By.XPATH, r'.//a')
                    td_div = tr.find_element(By.XPATH, r'./td[last()]')
                    temps.append(
                        (
                            th_a.text,
                            th_a.get_attribute('href'),
                            td_div.text
                        )
                    )
                for name, href, description in temps:
                    relative_path = get_relative_path_from_href(href)
                    concept_map.add_node(relative_path)
                    concept_map.nodes[relative_path]['name'] = name
                    if 'field' in block_title:
                        concept_map.nodes[relative_path]['Ntype'] = NodeType.FIELD
                    elif 'constructor' in block_title:
                        concept_map.nodes[relative_path]['Ntype'] = NodeType.CONSTRUCTOR
                    elif 'method' in block_title:
                        concept_map.nodes[relative_path]['Ntype'] = NodeType.METHOD
                    elif 'enum constant' in block_title:
                        concept_map.nodes[relative_path]['Ntype'] = NodeType.ENUM_CONSTANT
                    elif 'element' in block_title:
                        concept_map.nodes[relative_path]['Ntype'] = NodeType.OPTIONAL_ELEMENT
                    elif 'nested' in block_title:
                        concept_map.nodes[relative_path]['Ntype'] = NodeType.CLASS
                    else:
                        #print('undetected tile type: ', block_title, ' in ', class_node)
                        pass
                    concept_map.nodes[relative_path]['local_href'] = href
                    concept_map.nodes[relative_path]['description'] = description
                    concept_map.nodes[relative_path]['path'] = relative_path
                    concept_map.add_edge(
                        class_node, relative_path,
                        Etype=EdgeType.INCLUDE
                    )
        except Exception as e:
            logging.exception(e)


def __add_member_node_to_class_level_nodes_javadoc(concept_map: nx.DiGraph):

    if __pass_if_exist(concept_map, NodeType.FIELD):
        return

    __add_member_node_to_class_level_node_javadoc(
        concept_map, NodeType.ANNOTATION)
    __add_member_node_to_class_level_node_javadoc(concept_map, NodeType.CLASS)
    __add_member_node_to_class_level_node_javadoc(concept_map, NodeType.ENUM)
    __add_member_node_to_class_level_node_javadoc(concept_map, NodeType.ERROR)
    __add_member_node_to_class_level_node_javadoc(
        concept_map, NodeType.EXCEPTION)
    __add_member_node_to_class_level_node_javadoc(
        concept_map, NodeType.INTERFACE)


def __add_Parameter_ReturnType_relation(concept_map: nx.DiGraph):
    global browser
    Ntype_attributes = nx.get_node_attributes(concept_map, 'Ntype')
    #a = 'api/jdk.jshell/jdk/jshell/JShell.Subscription.html' in concept_map
    for node_type in class_level_node_types:
        class_nodes = [
            node for node in concept_map.nodes if node in Ntype_attributes and Ntype_attributes[node] == node_type]
        for class_node in class_nodes:
            local_href = concept_map.nodes[class_node]['local_href']
            browser.get(local_href)
            time.sleep(0.05)
            content_container = browser.find_element(
                By.XPATH, r'//div[@class="contentContainer"]')
            method_exist = True
            try:
                method_detail_section = content_container.find_element(
                    By.XPATH, r'.//section[@class="methodDetails"]')
                method_blocks = method_detail_section.find_elements(
                    By.XPATH, r'.//li[@class="blockList"]')
            except:
                method_exist = False
            if method_exist:
                for method_block in method_blocks:
                    try:
                        method_detail = method_block.find_element(
                            By.XPATH, r'./section[@class="detail"]')
                        a_with_id = method_detail.find_element(
                            By.XPATH, r'./h3/a[last()]')
                        method_id = a_with_id.get_attribute("id")
                        method_node = class_node + '#' + method_id
                        method_signature = method_detail.find_element(
                            By.XPATH, r'.//div[@class="memberSignature"]')
                        try:
                            return_type = method_signature.find_element(
                                By.XPATH, r'./span[@class="returnType"]/a')
                            return_type_node = get_relative_path_from_href(
                                return_type.get_attribute('href'))
                            concept_map.add_edge(
                                method_node,
                                return_type_node,
                                Etype=EdgeType.RETURN_TYPE
                            )
                        except NoSuchElementException:
                            pass
                        try:
                            parameters = method_signature.find_elements(
                                By.XPATH, r'./span[@class="arguments"]/a')
                            for parameter in parameters:
                                parameter_node = get_relative_path_from_href(
                                    parameter.get_attribute('href'))
                                concept_map.add_edge(
                                    method_node, parameter_node, Etype=EdgeType.PARAMETER)
                        except NoSuchElementException:
                            pass
                    except:
                        continue
            # add constructor parameter
            constructor_exist = True
            try:
                constructor_detail_section = content_container.find_element(
                    By.XPATH, r'.//section[@class="constructorDetails"]')
                constructor_blocks = constructor_detail_section.find_elements(
                    By.XPATH, r'.//li[@class="blockList"]')
            except:
                constructor_exist = False
            if constructor_exist:
                for method_block in constructor_blocks:
                    try:
                        method_detail = method_block.find_element(
                            By.XPATH, r'./section[@class="detail"]')
                        a_with_id = method_detail.find_element(
                            By.XPATH, r'./h3/a[last()]')
                        method_id = a_with_id.get_attribute("id")
                        method_node = class_node + '#' + method_id
                        method_signature = method_detail.find_element(
                            By.XPATH, r'.//div[@class="memberSignature"]')
                        try:
                            parameters = method_signature.find_elements(
                                By.XPATH, r'./span[@class="arguments"]/a')
                            for parameter in parameters:
                                parameter_node = get_relative_path_from_href(
                                    parameter.get_attribute('href'))
                                concept_map.add_edge(
                                    method_node,
                                    parameter_node,
                                    Etype=EdgeType.PARAMETER
                                )
                        except NoSuchElementException:
                            pass
                    except:
                        continue

            # add field type relation
            field_exist = True
            try:
                field_detail_section = content_container.find_element(
                    By.XPATH, r'.//section[@class="fieldDetails"]')
                field_blocks = field_detail_section.find_elements(
                    By.XPATH, r'.//li[@class="blockList"]')
            except:
                field_exist = False
            if field_exist:
                for field_block in field_blocks:
                    try:
                        field_detail = field_block.find_element(
                            By.XPATH, r'./section[@class="detail"]')
                        a_with_id = field_detail.find_element(
                            By.XPATH, r'./h3/a[last()]')
                        field_id = a_with_id.get_attribute("id")
                        field_node = class_node + '#' + field_id
                        field_signature = field_detail.find_element(
                            By.XPATH, r'.//div[@class="memberSignature"]')
                        try:
                            return_type = field_signature.find_element(
                                By.XPATH, r'./span[@class="returnType"]/a')
                            return_type_node = get_relative_path_from_href(
                                return_type.get_attribute('href'))
                            concept_map.add_edge(
                                field_node,
                                return_type_node,
                                Etype=EdgeType.FIELD_IS_TYPE
                            )
                        except NoSuchElementException:
                            pass
                    except:
                        continue


def __add_ref_in_desc_relation_javadoc(concept_map: nx.DiGraph):
    global browser
    Ntype_attributes = nx.get_node_attributes(concept_map, 'Ntype')
    for node_type in class_level_node_types:
        class_nodes = [
            node for node in concept_map.nodes if node in Ntype_attributes and Ntype_attributes[node] == node_type]
        for class_node in class_nodes:
            local_href = concept_map.nodes[class_node]['local_href']
            browser.get(local_href)
            time.sleep(0.05)
            content_container = browser.find_element(
                By.XPATH, r'//div[@class="contentContainer"]')
            # add ref_in_desc relation
            try:
                description_block = content_container.find_element(
                    By.XPATH, r'.//section[@class="description"]/div')
                ref_as = description_block.find_elements(By.XPATH, r'.//a')
                for ref_a in ref_as:
                    try:
                        local_href = ref_a.get_attribute("href")
                        relative_path = get_relative_path_from_href(local_href)
                        concept_map.add_edge(
                            class_node,
                            relative_path,
                            Etype=EdgeType.REFERENCE_IN_DESCRIPTION
                        )
                    except NoSuchElementException:
                        continue
            except NoSuchElementException:
                pass
            # add inheritance relation
            try:
                inheritance_tree = content_container.find_element(
                    By.XPATH, r'./div[@class="inheritance"]')
                parent = inheritance_tree.find_element(By.XPATH, r'./a')
                child = inheritance_tree.find_element(
                    By.XPATH, r'./div[@class="inheritance"]')
                terminited = False
                while not terminited:
                    try:
                        new_parent = child.find_element(By.XPATH, r'./a')
                        parent = new_parent
                        child = child.find_element(
                            By.XPATH, r'./div[@class="inheritance"]')
                    except NoSuchElementException:
                        terminited = True
                parent_href = parent.get_attribute("href")
                relative_path = get_relative_path_from_href(parent_href)
                concept_map.add_edge(
                    class_node,
                    relative_path,
                    Etype=EdgeType.INHERIT
                )
            except NoSuchElementException:
                pass
            # add implement relation
            try:
                description_block = content_container.find_element(
                    By.XPATH, r'.//section[@class="description"]')
                dls = description_block.find_elements(By.XPATH, r'.//dl')
                for dl in dls:
                    try:
                        dts = dl.find_elements(By.XPATH, r'./dt')
                        dds = dl.find_elements(By.XPATH, r'./dd')
                        for i in range(len(dts)):
                            dt = dts[i]
                            dd = dds[i]
                            if 'Implemented' in dt.text:
                                implement_as = dd.find_elements(
                                    By.XPATH, r'.//a')
                                for implement_a in implement_as:
                                    implement_href = implement_a.get_attribute(
                                        "href")
                                    relative_path = get_relative_path_from_href(
                                        implement_href)
                                    concept_map.add_edge(
                                        class_node,
                                        relative_path,
                                        Etype=EdgeType.IMPLEMENT
                                    )
                            if 'See' in dt.text or 'Note' in dt.text:
                                also_see_as = dd.find_elements(
                                    By.XPATH, r'.//a')
                                for also_see_a in also_see_as:
                                    also_see_href = also_see_a.get_attribute(
                                        "href")
                                    relative_path = get_relative_path_from_href(
                                        also_see_href)
                                    if relative_path not in concept_map:
                                        concept_map.add_node(relative_path)
                                        concept_map.nodes[relative_path]['Ntype'] = NodeType.OTHER
                                    concept_map.add_edge(
                                        class_node,
                                        relative_path,
                                        Etype=EdgeType.ALSO_SEE
                                    )
                    except:
                        continue
            except NoSuchElementException:
                pass


def generate_basic_concept_map_javadoc(mode='new_generate'):
    '''
    仅根据最明显的层级包含关系构建concept map
    '''
    graph_path = os.path.join(CONCEPT_MAP_STORE_PATH,
                              JAVADOC_CONCEPT_MAP_FILE_NAME)
    if os.path.exists(graph_path) and mode != 'new_generate':
        concept_map = nx.read_gexf(graph_path)
    else:
        concept_map = nx.DiGraph()
    __add_meta_node_javadoc(concept_map)
    #print('meta data added')
    __add_module_node_javadoc(concept_map)
    #print('module data added')
    try:
        __add_package_node_javadoc(concept_map)
        #print('package data added')
        __add_class_level_node_javadoc(concept_map)
        #print('class data added')
        __add_member_node_to_class_level_nodes_javadoc(concept_map)
        #print('member data added')
    except Exception as e:
        print(e)

    return concept_map


def add_complex_relations_javadoc(concept_map: nx.DiGraph):
    __add_Parameter_ReturnType_relation(concept_map)
    print('relation 1 added')
    __add_ref_in_desc_relation_javadoc(concept_map)
    print('relation 2 added')
    # TODO: add ATTACH_ANNOTATION, THROWS, NESTED_CLASS relations and ALSO_SEE for methods and fields
    # TODO: nested class has actually no Ntype, need to consider and generate whole concept map again


def generate_concept_map_javadoc():
    concept_map = generate_basic_concept_map_javadoc()
    add_complex_relations_javadoc(concept_map)
    return concept_map


def generate_concept_map(doc_name='javadoc'):
    switch = {
        'javadoc': generate_concept_map_javadoc
    }
    return switch[doc_name]()
