To copy:

Copy .env.example to a new '.env' file & fill out with actual values.

To run:
```
cd pe-org-air-platform
docker build -f docker/Dockerfile -t pe-org-air-platform .
docker run --rm -it -p 8000:8000 --env-file .env pe-org-air-platform
```