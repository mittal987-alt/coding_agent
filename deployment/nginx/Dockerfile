##############################################################
# Production NGINX Image
##############################################################

FROM nginx:1.28-alpine

##############################################################
# Metadata
##############################################################

LABEL maintainer="AI Software Engineer Team"

LABEL description="Production NGINX Reverse Proxy"

LABEL version="1.0.0"

##############################################################
# Install Packages
##############################################################

RUN apk add --no-cache \
    bash \
    curl \
    ca-certificates \
    openssl \
    tzdata

##############################################################
# Create Required Directories
##############################################################

RUN mkdir -p \
    /etc/nginx/ssl \
    /etc/nginx/conf.d \
    /var/cache/nginx \
    /var/log/nginx \
    /var/www/certbot \
    /usr/share/nginx/html

##############################################################
# Copy Configuration
##############################################################

COPY nginx.conf /etc/nginx/nginx.conf

COPY default.conf /etc/nginx/conf.d/default.conf

COPY ssl.conf /etc/nginx/conf.d/ssl.conf

COPY security.conf /etc/nginx/conf.d/security.conf

##############################################################
# Remove Default Site
##############################################################

RUN rm -f /etc/nginx/conf.d/default.conf.default || true

##############################################################
# Permissions
##############################################################

RUN chown -R nginx:nginx \
    /etc/nginx \
    /var/cache/nginx \
    /var/log/nginx \
    /usr/share/nginx/html \
    /var/www/certbot

##############################################################
# Switch to Non-Root User
##############################################################

USER nginx

##############################################################
# Health Check
##############################################################

HEALTHCHECK --interval=30s \
            --timeout=5s \
            --start-period=20s \
            --retries=3 \
CMD curl -f http://127.0.0.1/health || exit 1

##############################################################
# Expose Ports
##############################################################

EXPOSE 80

EXPOSE 443

##############################################################
# Stop Signal
##############################################################

STOPSIGNAL SIGQUIT

##############################################################
# Start NGINX
##############################################################

CMD ["nginx", "-g", "daemon off;"]