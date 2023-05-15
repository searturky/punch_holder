FROM nginx:stable-alpine

ENV NGINX_ENVSUBST_OUTPUT_DIR='/etc/nginx'

# COPY build /usr/share/nginx/html
COPY nginx.conf.template /etc/nginx/templates/nginx.conf.template

CMD ["nginx", "-g", "daemon off;"]
