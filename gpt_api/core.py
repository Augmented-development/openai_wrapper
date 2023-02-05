import os
from copy import copy
from enum import Enum

import openai

from query_config import QueryConfig, DEFAULT_QUERY_CONFIG
from utils import discover_api_key


class QueryType(Enum):
    COMPLETE = 1
    INSERT = 2
    EDIT = 3


DEV_MODE = os.environ.get("GPT_API_DEV_MODE", False)


class GPTApi:
    instances = {}

    # factory method
    @classmethod
    def create(cls, api_key: str = None):
        if api_key is None:
            if DEV_MODE or "OPENAI_API_KEY" in os.environ:
                api_key = discover_api_key()
            else:
                raise ValueError("api_key must be provided or set GPT_API_DEV_MODE=1 for automatic discovery")
        if api_key not in cls.instances:
            cls.instances[api_key] = cls(api_key)
        return cls.instances[api_key]

    def __init__(self, api_key: str = None):
        if api_key is None:
            if DEV_MODE or "OPENAI_API_KEY" in os.environ:
                api_key = discover_api_key()
            else:
                raise ValueError("api_key must be provided or set GPT_API_DEV_MODE=1 for automatic discovery")
        self.api_key = api_key
        self._stored_api_key = None

    # context manager
    def __enter__(self):
        if self._stored_api_key is not None:
            raise RuntimeError("OpenaiWrapper already in use")
        self._stored_api_key = openai.api_key
        openai.api_key = self.api_key
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        openai.api_key = self._stored_api_key
        self._stored_api_key = None

    # api

    INSERT_TOKEN = "[insert]"

    def insert(self, prompt: str, model="text-davinci-insert-002", config: QueryConfig = None, **kwargs) -> str:
        # INSERT_TOKEN has to be in the prompt exactly once
        if prompt.count(self.INSERT_TOKEN) != 1:
            raise ValueError(f"{self.INSERT_TOKEN} must be in the prompt exactly once")
        return self.complete(prompt, model=model, config=config, **kwargs)

    def complete(self, prompt, model="text-davinci-003", config: QueryConfig = DEFAULT_QUERY_CONFIG, **kwargs):
        with self:
            if config is None:
                config = DEFAULT_QUERY_CONFIG
            config = copy(config)
            config.update(**kwargs)
            response = openai.Completion.create(
                model=model,  # "text-davinci-003",
                prompt=prompt,
                temperature=config.temperature,
                n=config.n,
                top_p=config.top_p,
                max_tokens=config.max_tokens,
                stream=config.stream,
                stop=config.stop,
                user=config.user,
            )
            return response.data[0].text

    def edit(self, prompt, instruction, model="text-davinci-edit-001", config: QueryConfig = DEFAULT_QUERY_CONFIG,
             **kwargs):
        with self:
            if config is None:
                config = DEFAULT_QUERY_CONFIG
            config = copy(config)
            config.update(**kwargs)
            response = openai.Edit.create(
                model=model,
                input=prompt,  # todo: consider renaming prompt to input (and prompt goes to instruction)
                instruction=instruction,
                temperature=config.temperature,
                n=config.n,
                top_p=config.top_p,
                max_tokens=config.max_tokens,
                stream=config.stream,
                stop=config.stop,
                user=config.user,
            )
            return response.data[0].text

    # old
    def query(self, prompt: str, query_type: QueryType = QueryType.COMPLETE, config: QueryConfig = DEFAULT_QUERY_CONFIG,
              **kwargs) -> str:
        query_type = QueryType(query_type)
        if query_type == QueryType.COMPLETE:
            return self.complete(prompt, config=config, **kwargs)
        elif query_type == QueryType.INSERT:
            return self.insert(prompt, config=config, **kwargs)
        elif query_type == QueryType.EDIT:
            return self.edit(prompt, config=config, **kwargs)
        else:
            raise ValueError(f"Unknown query_type: {query_type}")

    # make a query to openai_wrapper that uses the cheaper - curie - model
    def query_cheap(self, prompt: str, query_type: QueryType = QueryType.COMPLETE,
                    config: QueryConfig = DEFAULT_QUERY_CONFIG, **kwargs) -> str:
        query_type = QueryType(query_type)
        if query_type == QueryType.COMPLETE:
            return self.complete(prompt, config=config, model="text-curie-001", **kwargs)
        elif query_type == QueryType.INSERT:
            return self.insert(prompt, config=config, model="text-davinci-insert-002", **kwargs)
        elif query_type == QueryType.EDIT:
            return self.edit(prompt, config=config, model="text-davinci-edit-001", **kwargs)
        else:
            raise ValueError(f"Unknown query_type: {query_type}")
