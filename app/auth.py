# auth.py
from fastapi.security.api_key import APIKeyHeader
from fastapi import Security, HTTPException
from starlette.status import HTTP_403_FORBIDDEN
from dotenv import load_dotenv
load_dotenv()
import os, pdb
from fastapi.security.api_key import APIKeyHeader
from cryptography.fernet import Fernet


api_key_header = APIKeyHeader(name="access_token", auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):

    try:
        c_key = Fernet(os.getenv('crypt-key'))
        decrypt_data = c_key.decrypt(api_key_header).decode()
        if os.getenv('crypt-plaintext') in decrypt_data:
            return api_key_header   
    except:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate API KEY"
        )
