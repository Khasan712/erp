FROM nginx:latest
COPY ./conf/default.conf /etc/nginx/conf.d/
COPY ./conf/proxy_params /etc/nginx/proxy_params

RUN mkdir -p /home/app/staticfiles
RUN mkdir -p /home/app/media