from django.apps import AppConfig
from openai import OpenAI


class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'


# 🔑 Cliente global de OpenAI (API key quemada)
client = OpenAI(
    api_key="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"
)