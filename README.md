# Usage
## Run Server
uvicorn uploader:app

## Nginx Config (Optional)
```
server {
    location /upload {
        proxy_pass         http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }
}
```

## Upload Image
args:
- account_id: required
- access_key_id: required
- secret_access_key: required
- bucket: required
- file: required
- key_pattern: optional
- url_prefix: optional

key_pattern virable
- year
- mon
- day
- hour
- minute
- second
- timestamp
- stem
- ext
- filename

curl example
```shell
curl -X POST 'https://image.your.domain/upload' \
  --header 'Content-Type: multipart/form-data' \
  --form 'account_id=<account_id>' \
  --form 'access_key_id=<account_id>' \
  --form 'secret_access_key=<secret_access_key>' \
  --form 'bucket=<bucket-name>' \
  --form file=@<file-path> \
  --form 'key_pattern=files/{year:0>4}-{mon:0>2}-{day:0>2}/{stem}_{timestamp}{ext}'
```

## MWeb Config
![](mweb-config.jpg)
