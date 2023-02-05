"""

"""

# todo: add the ability to override specific config values
from core import GPTApi, QueryType


def get_gpt_api(api_key=None) -> GPTApi:
    return GPTApi.create(api_key)


def query_gpt(prompt, config, query_type=QueryType.COMPLETE, api_key=None, **kwargs):
    query_type = QueryType(query_type)
    if query_type == QueryType.COMPLETE:
        return gpt_complete(prompt, config, api_key, **kwargs)
    elif query_type == QueryType.INSERT:
        return gpt_insert(prompt, config, api_key, **kwargs)
    elif query_type == QueryType.EDIT:
        return gpt_edit(prompt, config, api_key, **kwargs)
    else:
        raise ValueError(f"query_type {query_type} not supported")


def gpt_complete(prompt, config, api_key=None, **kwargs):
    api = get_gpt_api(api_key)
    return api.complete(prompt, config, **kwargs)


def gpt_edit(prompt, instruction, config, api_key=None, **kwargs):
    api = get_gpt_api(api_key)
    return api.edit(prompt, instruction, config, **kwargs)


def gpt_insert(prompt, config, api_key=None, **kwargs):
    api = get_gpt_api(api_key)
    return api.insert(prompt, config, **kwargs)
