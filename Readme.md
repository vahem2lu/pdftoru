# PDFToru
PDFToru is a simple containerized service you can use to parse PDFs over REST API and receive a response (depends on the endpoint).

Container consists of:

- base image: python:3.11-slim
- PDF parser: [pdfplumber](https://pypi.org/project/pdfplumber/) Python module to parse PDFs
- ASGI server: `uvicorn` to run the API

# Docker installation

Docker image is available from Github Docker Registry: `ghcr.io/vahem2lu/pdftoru:latest`

Available tags:

- `v1.x` - version tags
- `latest` - latest build

# Facts

- All parsing endpoints require a **POST request**
- Responses are always in **JSON** format.

# Configuration

Configure via environment variables when running the container.

`MAX_UPLOAD_SIZE_MB` can be changed via environment values. Default is `50`. Unit is `MB`.

`APP_VERSION` is set by git tag on every build.

# API Ports and Endpoints

This API has one public port necessary and has several endpoints.

## Inside container
The API listens on port 8000 inside the container. Forward it to a suitable port on the Docker host (e.g., 3002).

## Health check
- GET `/health` - check if the service is running

Example health response:
```json
{
    "status": "ok",
    "version": "v1.0.0",
    "uptime_seconds": 100,
    "max_upload_MB": 5,
    "free_disk_MB": 10000 // (1024*1024)
}

```

## Endpoints 
- POST `/extract/text` - extract full text from PDF
- POST `/extract/words` - extract individual words with coordinates
- POST `/extract/tables` - extract tables and their text
- POST `/extract/layout` - extract all layout objects with coordinates

# Examples

Run container via CLI:

`docker run -p 3002:8000 -e MAX_UPLOAD_SIZE_MB=50 ghcr.io/vahem2lu/pdftoru:latest`

Test with `curl`:
```bash
curl -X POST "http://localhost:3002/extract/text" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@yourResume.pdf"
```

# Build and development process

After some developing you may want to try it out. This can be done either way.

## Localhost build

After necessary changes, build local container. You need to have docker desktop environment set up!

`docker build --build-arg APP_VERSION="dev-local" -t pdftoru:dev-local .`

and for run:

`docker run -p 3002:8000 -e MAX_UPLOAD_SIZE_MB=5 pdftoru:dev-local`

## Github build

Make some necessary changes, commit your changes, add tag with v-prefix and push code with tag to your repository.

```bash
git add *
git commit -m "Changes"
git tag v1.1
git push
```

# LICENSE
See LICENSE file.