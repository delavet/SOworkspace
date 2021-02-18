import os
import json

from util.config import SO_POSTS_STORE_PATH, EUREKA_DATASET_STORE_PATH, EUREKA_FULL_DATASET_FILE_NAME, JAVADOC_GLOBAL_NAME, APIDOC_ROOT_URL, APIDOC_API_URL_REGEX_PATTERN, EUREKA_REFINED_LABEL_STORE_PATH


def generate_NER_dataset_from_refined_label_javadoc():
    label_file_names = os.listdir(
        EUREKA_REFINED_LABEL_STORE_PATH[JAVADOC_GLOBAL_NAME])
    refined_dataset = []
    for filename in label_file_names:
        if not str(filename).startswith('ner_data'):
            continue
        with open(os.path.join(EUREKA_REFINED_LABEL_STORE_PATH[JAVADOC_GLOBAL_NAME], filename), 'r', encoding='utf-8') as rf:
            partial_refined_dataset = json.load(rf)
        refined_dataset.extend(partial_refined_dataset)
    with open(os.path.join(EUREKA_DATASET_STORE_PATH[JAVADOC_GLOBAL_NAME], EUREKA_FULL_DATASET_FILE_NAME), 'w', encoding='utf-8') as wf:
        wf.writelines([json.dumps(d) + '\n' for d in refined_dataset])


if __name__ == "__main__":
    # 之后可以改成其他的文档
    generate_NER_dataset_from_refined_label_javadoc()
