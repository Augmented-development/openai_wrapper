import getpass
import json
import os
from enum import Enum

import openai

registry = {}
possible_filenames = [
    '.openai_api_key',
    'secrets.json',
    'secrets.txt',
]
possible_key_locations = [
    os.path.expanduser('~'),
    os.path.abspath(os.path.dirname(__file__)),
    os.path.abspath('')
]


def validate_api_key(api_key: str):
    old_key = openai.api_key
    try:
        openai.api_key = api_key
        openai.Engine.list()
        openai.api_key = old_key
        return True
    except:
        openai.api_key = old_key
        return False


def discover_api_key():
    api_key = os.environ.get("OPENAI_API_KEY")
    # if the object already exists, return it
    if api_key in registry:
        return registry[api_key]
    if api_key is None:
        for location in possible_key_locations:
            if api_key is not None:
                break
            for filename in possible_filenames:
                full_path = os.path.join(location, filename)
                if os.path.exists(full_path):
                    with open(full_path, 'r') as f:
                        data = f.read()
                        if filename.endswith('.json'):
                            data = json.loads(data)
                            if 'openai_api_key' in data:
                                api_key = data['openai_api_key']
                                break
                        elif filename.endswith('.txt'):
                            # noinspection PyTypeChecker
                            d = dict([line.split(':', 1) for line in data.splitlines()])
                            if 'openai_api_key' in d:
                                api_key = d['openai_api_key']
                                break
                        elif filename.startswith('.'):
                            # check it's only one line:
                            if len(data.strip().splitlines()) == 1:
                                api_key = data.strip()
                                break
        if api_key is None:
            while not validate_api_key(api_key):
                message = "Please enter your OpenAI API key. You can find it at https://beta.openai.com/account/api-keys: "
                api_key = getpass.getpass(message)
                if not validate_api_key(api_key):
                    print("Invalid API key. Please try again.")
            # save token to file, with user confirmation
            print("Key received")
            res = input("Save token to file? [y/n]")
            if res.lower() == 'y':
                default_path = os.path.join(os.path.expanduser('~'), '.openai_api_key')
                path = input(f"Enter path to save token to [{default_path}]: ")
                if path == '':
                    path = default_path
                with open(path, 'w') as f:
                    f.write(api_key)
    return api_key


class GptModels(Enum):
    TEXT_DAVINCI_003 = "text-davinci-003"
    # "text-curie-001"
    TEXT_CURIE_001 = "text-curie-001"

    # "text-davinci-insert-002"
    TEXT_DAVINCI_INSERT_002 = "text-davinci-insert-002"
    # "text-davinci-edit-001"
    TEXT_DAVINCI_EDIT_001 = "text-davinci-edit-001"
    # "code-davinci-edit-001"
    CODE_DAVINCI_EDIT_001 = "code-davinci-edit-001"
    # "code-davinci-002"
    CODE_DAVINCI_002 = "code-davinci-002"


TOKEN_BY_MODEL = {
    GptModels.TEXT_DAVINCI_003: 4000,
    GptModels.TEXT_CURIE_001: 2048,
    # GptModels.TEXT_DAVINCI_INSERT_002: 4000,
    # GptModels.TEXT_DAVINCI_EDIT_001: 4000,
    # GptModels.CODE_DAVINCI_EDIT_001: 4000,
    GptModels.CODE_DAVINCI_002: 8000,
}


def get_token_limit(model="text-davinci-003"):
    # get amount of tokens for each model
    if isinstance(model, Enum):
        # convert to str
        model = model.value
    if isinstance(model, str):
        model = GptModels(model)
    else:
        raise ValueError("model must be a string or GptModels enum")
    return TOKEN_BY_MODEL[model]


def get_token_count(text):
    # calculate amount of tokens in text
    import transformers
    tokenizer = transformers.GPT2TokenizerFast.from_pretrained("gpt2")
    return len(tokenizer.encode(text))

# max_response_length = get_token_limit(model) - get_token_count(prompt)
