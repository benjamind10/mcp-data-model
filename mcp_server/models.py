from dataclasses import dataclass
from typing import Literal


@dataclass
class OPCUATag:
    server_url: str
    node_id: str
    browse_path: str
    display_name: str
    data_type: str


@dataclass
class TagSample:
    tag: OPCUATag
    timestamp: str
    value: any


TagType = Literal["analog", "boolean", "status", "enum", "string"]
