#FROM nginxinc/nginx-unprivileged:1-alpine
FROM nginx:1.23.0-alpine

#COPY ./erp.conf /etc/nginx/conf.d/default.conf
COPY ./nginx/* /etc/nginx/
COPY ./run.sh /run.sh

ENV APP_HOST=app
ENV APP_PORT=9000

RUN apk add --no-cache openssl bash
RUN chmod +x /run.sh

VOLUME /vol/static
VOLUME /vol/www

CMD ["/run.sh"]

