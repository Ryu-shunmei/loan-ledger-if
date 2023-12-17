from jose import jwt
from datetime import datetime, timedelta
from configs.auth_config import auth_settings


def gen_access_token(
    payload: dict, expires_delta: int = auth_settings.ACCESS_TOKEN_EXP_HOURS
) -> str:
    exp = datetime.utcnow() + timedelta(hours=expires_delta)
    return jwt.encode(
        claims={**payload, "exp": exp},
        key=auth_settings.SECRETS_KEY,
        algorithm=auth_settings.ALGORITHM,
        headers={"alg": auth_settings.ALGORITHM, "type": "JWT"},
    )
