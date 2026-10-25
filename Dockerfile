# Build the site first (./build.sh), then:
#   docker build -t peru-journal .
#   docker run --rm -p 8080:80 peru-journal
FROM nginx:alpine
COPY dist/ /usr/share/nginx/html/
EXPOSE 80
