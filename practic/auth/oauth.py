from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
import json

config = Config('.env')
oauth = OAuth(config)


def apply_vk_compliance(data=None):
    if data and isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            pass

    if data is not None:
        return data


oauth.register(
    name='vk',
    client_id=config('VK_CLIENT_ID'),
    client_secret=config('VK_CLIENT_SECRET'),

    access_token_url='https://id.vk.ru/oauth2/auth',
    authorize_url='https://id.vk.ru/authorize',
    userinfo_endpoint='https://id.vk.ru/oauth2/user_info',

    # Параметры для PKCE
    client_kwargs={
        'scope': 'email phone',
        'response_type': 'code',
        'code_challenge_method': 'S256',
    },

    token_endpoint_auth_method='client_secret_post',

    compliance=apply_vk_compliance,
)
