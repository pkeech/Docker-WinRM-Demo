## BASE IMAGE
FROM nginx:1.18 AS BUILDER

## IMAGE METADATA
LABEL Maintainer="Peter Keech <pkeech@ngds.com>"

## IMAGE DEPENDENCIES
FROM Builder AS Dependencies
RUN apt-get update && apt-get upgrade -y
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/

## DEV IMAGE
FROM Dependencies AS Development

## TEST IMAGE
FROM Dependencies AS Test

## PRODUCTION IMAGE
FROM Dependencies AS Production
EXPOSE 8080