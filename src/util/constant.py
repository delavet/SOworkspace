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
    OTHER = 'OTHER'


class EdgeType:
    INCLUDE = 'INCLUDE'
    EXPORT = 'EXPORT'
    REQUIRE = 'REQUIRE'
    INHERIT = 'INHERIT'
    IMPLEMENT = 'IMPLEMENT'
    REFERENCE_IN_DESCRIPTION = 'REFERENCE_IN_DESCRIPTION' #reference when talking about the description
    PARAMETER = 'PARAMETER' #this function use an object of this class as parameter
    RETURN_TYPE = 'RETURN_TYPE' #this function return an object of this class
    FIELD_IS_TYPE = 'FIELD_IS_TYPE' #the field's type is this class
    NESTED_CLASS = 'NESTED_CLASS' #the class is a nested class of another class, can be identified with Enclosing class
    ATTACH_ANNOTATION = 'ATTACH_ANNOTATION' #method or field or class is attached with an annotation
    THROWS = 'THROWS' #a method throw an exception or an error
    ALSO_SEE = 'ALSO_SEE' #two related concepts, marked as also see in the doc


class NodeAttributes:
    NAME = 'name'
    Ntype = 'Ntype'
    LOCAL_HREF = 'local_href'
    DESCRIPTION = 'description'
    PATH = 'path'
    COMMUNITY_FREQ = 'community_freq'


class_level_node_types = [
    NodeType.ANNOTATION, 
    NodeType.CLASS, 
    NodeType.ENUM, 
    NodeType.ERROR,
    NodeType.EXCEPTION,
    NodeType.INTERFACE
]