from typing import Union, Annotated
from botocore.client import Config
import boto3
from functools import lru_cache

from datetime import datetime
from fastapi import FastAPI, Header, Form, UploadFile, Request, File


app = FastAPI()
StrForm = Annotated[str, Form()]
StrHeader = Annotated[str, Header(convert_underscores=False)]


@lru_cache(maxsize=100)
def get_s3agent(account_id, access_key_id, secret_access_key, region='auto'):
    s3 = boto3.client('s3',
                    endpoint_url=f'https://{account_id}.r2.cloudflarestorage.com',
                    aws_access_key_id=access_key_id,
                    aws_secret_access_key=secret_access_key,
                    config=Config(signature_version='s3v4'),
                    region_name=region)
    return s3

def upload_r2(s3, content: bytes, bucket: str, key: str):
    res = s3.put_object(Body=content, Bucket=bucket, Key=key)
    return res

@app.post("/upload")
async def upload(account_id: StrForm, access_key_id: StrForm, secret_access_key: StrForm,
           bucket: StrForm, host: Annotated[str, Header()],
           file: UploadFile = File(...), key_pattern: StrForm = '', url_prefix: StrForm = '',
           ):
    if not key_pattern:
        key_pattern = 'mweb/{year:0>4}-{mon:0>2}-{day:0>2}---{filename}'

    now = datetime.now()
    args = dict(
        year=now.year,
        mon=now.month,
        day=now.day,
        hour=now.hour,
        filename=file.filename,
    )
    key = key_pattern.format(**{k: v for k, v in args.items() if '{'+k in key_pattern})
    if not url_prefix:
        url_prefix = f'https://{host}'

    content = file.file.read()
    errmsg = ''
    try:
        s3 = get_s3agent(account_id, access_key_id, secret_access_key)
        resp = upload_r2(s3, content, bucket, key)
    except Exception as e:
        errmsg = str(e)
    if resp['ResponseMetadata']['HTTPStatusCode'] != 200:
        return {'code': -1, 'msg': errmsg, 'data': resp}

    res = {
        "code": 0,
        "data": {
            "size": file.size,
            "path": key,
            "url": f'{url_prefix}/{key}',
        }
    }
    return res

