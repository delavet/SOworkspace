from pickle import NONE


class NodeType:
    SCOPE = 'SCOPE'
    MODULE = 'MODULE'
    PACKAGE = 'PACKAGE'
    CLASS = 'CLASS'
    INTERFACE = 'INTERFACE'
    ENUM = 'ENUM'
    EXCEPTION = 'EXCEPTION'
    ERROR = 'ERROR'
    ANNOTATION = 'ANNOTATION'
    FIELD = 'FIELD'
    METHOD = 'METHOD'
    ENUM_CONSTANT = 'ENUM_CONSTANT'
    OPTIONAL_ELEMENT = 'OPTIONAL_ELEMENT'
    CONSTRUCTOR = 'CONSTRUCTOR'
    # only occur in the hyper concept map
    DOMAIN_TERM = 'DOMAIN_TERM'
    WIKI_TERM = 'WIKI_TERM'
    OTHER = 'OTHER'


class EdgeType:
    INCLUDE = 'INCLUDE'
    EXPORT = 'EXPORT'
    REQUIRE = 'REQUIRE'
    INHERIT = 'INHERIT'
    IMPLEMENT = 'IMPLEMENT'
    # reference when talking about the description
    REFERENCE_IN_DESCRIPTION = 'REFERENCE_IN_DESCRIPTION'
    PARAMETER = 'PARAMETER'  # this function use an object of this class as parameter
    RETURN_TYPE = 'RETURN_TYPE'  # this function return an object of this class
    FIELD_IS_TYPE = 'FIELD_IS_TYPE'  # the field's type is this class
    # the class is a nested class of another class, can be identified with Enclosing class
    NESTED_CLASS = 'NESTED_CLASS'
    # method or field or class is attached with an annotation
    ATTACH_ANNOTATION = 'ATTACH_ANNOTATION'
    THROWS = 'THROWS'  # a method throw an exception or an error
    ALSO_SEE = 'ALSO_SEE'  # two related concepts, marked as also see in the doc
    COOCCUR = 'COOCCUR' # only occur in the community map
    # only occur in hyper concept map
    MENTION = 'MENTION'
    RELATED_TO = 'RELATED_TO' # a domain term is related to a wikipedia concepts
    WIKI_RELATED = 'WIKI_RELATED' # the relationship between wikipedia concepts


class NodeAttributes:
    NAME = 'name'
    Ntype = 'Ntype'
    LOCAL_HREF = 'local_href'
    DESCRIPTION = 'description'
    PATH = 'path'
    # only occur in community map
    COMMUNITY_FREQ = 'community_freq'
    # only occur in hyper_concept_map
    API_QUALIFIED_NAME = 'qualified_name'
    ALIAS = 'alias' # the alias of the node name
    ADDITIONAL_PROPERTIES = 'addtional_properties'
    

class EdgeAttrbutes:
    Etype = 'Etype'
    COOCCUR_FREQUENCY = 'cooccur_freq'  # only enabled while Etype is COOCCUR in COMMUNITY MAP
    COOCCUR_THREADS = 'cooccur_threads'  # only enabled while Etype is COOCCUR in COMMUNITY MAP
    WIKI_LABEL = 'wikipedia_label' # only enabled in wikipedia relationships, indicate what kind of the wikipedia relationship is


class_level_node_types = [
    NodeType.ANNOTATION,
    NodeType.CLASS,
    NodeType.ENUM,
    NodeType.ERROR,
    NodeType.EXCEPTION,
    NodeType.INTERFACE
]

field_level_node_types = [
    NodeType.FIELD,
    NodeType.METHOD,
    NodeType.ENUM_CONSTANT,
    NodeType.CONSTRUCTOR
]

high_level_node_types = [
    NodeType.SCOPE,
    NodeType.PACKAGE,
    NodeType.MODULE
]

term_level_node_types = [
    NodeType.DOMAIN_TERM,
    NodeType.WIKI_TERM
]


SO_POST_STOP_WORDS = ['here', 'this', 'javadoc', 'javadocs', 'docs', 'documentation', 'the documentation',
                      'doc', 'the javadoc', 'java docs', 'java doc', 'java documentation', 'the docs ']
