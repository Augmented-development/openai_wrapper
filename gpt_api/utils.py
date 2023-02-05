import getpass
import json
import os

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
