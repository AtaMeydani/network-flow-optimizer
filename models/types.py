from enum import Enum, unique

@unique
class ModelType(Enum):
    CAPACITY_EXPANSION = "capacity_expansion"
    NODE_LINK = "node_link"
    LINK_PATH = "link_path"