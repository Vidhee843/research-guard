import re
from os import environ
from types import SimpleNamespace

import joblib
from sanic_security.utils import str_to_bool
from transformers import pipeline


class Config(SimpleNamespace):
    DEBUG: bool
    DATABASE_URL: str
    GENERATE_SCHEMAS: bool

    def __init__(self, default_config: dict = None):
        super().__init__(**default_config)
        self.load_environment_variables()

    def load_environment_variables(self, env_prefix: str = "RESEARCH_"):
        for key, value in environ.items():
            if not key.startswith(env_prefix):
                continue

            _, config_key = key.split(env_prefix, 1)

            for converter in (int, float, str_to_bool, str):
                try:
                    setattr(self, config_key, converter(value))
                    break
                except ValueError:
                    pass
