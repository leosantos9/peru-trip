FROM python:3.12-alpine AS builder
WORKDIR /site
COPY content/ content/
COPY src/ src/
COPY scripts/ scripts/
RUN python scripts/build.py && python scripts/validate.py

FROM nginx:alpine
COPY --from=builder /site/dist/ /usr/share/nginx/html/
EXPOSE 80
