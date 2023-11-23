# Python SFTP-Server

References:

- [pip - pyftpdlib](https://pypi.org/project/pyftpdlib/)
- [Github - pyftpdlib](https://github.com/giampaolo/pyftpdlib/)
- [Documentation - pyftpdlib - ssl](https://pyftpdlib.readthedocs.io/en/latest/tutorial.html#ftps-ftp-over-tls-ssl-server)

## Build docker image

To build the docker image run the following command in the directory of the docker file:

```sh
docker build -t pysftpserver:1.0.0 -f dockerfile .
```

## Start container

```sh
docker run -p 2121:2121 -e CERT_CN=host.domain.com -ti pysftpserver:1.0.0
```

## Docker Compose

Example:

```yml
services:
  sftp.server:
    image: pysftpserver:1.0.0
    volumes:
      - "./conf:/conf"
      - "./data:/data"
    environment:
      - CERT_CN=host.domain.com
      - USER_NAME=ftp_user
      - USER_PASSWORD=ftp_password
    ports:
      - "2121:2121"
```
