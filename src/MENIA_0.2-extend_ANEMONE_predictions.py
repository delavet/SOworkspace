from util.community_info.common import extend_thread2api_detection_result_with_ground_truth
from util.config import JAVADOC_GLOBAL_NAME


def extend_ANEMONE_predictions(doc_name = JAVADOC_GLOBAL_NAME):
    extend_thread2api_detection_result_with_ground_truth(doc_name)


if __name__ == "__main__":
    extend_ANEMONE_predictions(JAVADOC_GLOBAL_NAME)