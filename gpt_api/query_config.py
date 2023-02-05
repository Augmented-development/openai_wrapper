import getpass
from dataclasses import dataclass
from typing import Union, List


@dataclass
class QueryConfig:
    model: str = "text-davinci-003"
    max_tokens: int = 512
    temperature: float = 0.9
    top_p: float = 1.0
    n: int = 1
    stream: bool = False
    stop: Union[str, List[str]] = None
    user: str = getpass.getuser()

    def update(self, **kwargs):
        self.__dict__.update(kwargs)


DEFAULT_QUERY_CONFIG = QueryConfig()
