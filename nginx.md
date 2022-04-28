http://www.nginx.cn/doc/standard/httpcore.html

try_files
语法: try_files file ... uri 或 try_files file ... = code
rewrite
语法：rewrite regex replacement [flag]
https://segmentfault.com/a/1190000002797606
执行顺序：
执行server块的rewrite指令
执行location匹配
执行选定的location中的rewrite指令

upstream backend {
    server s1.barretlee.com;
    server s2.barretlee.com;
}
server {
        listen       80;
        server_name  localhost;
        
        root   /workspace/dist;

        #access_log  logs/host.access.log  main;

        location / {
            try_files $uri $uri/ @router;
            index  index.html index.htm;
        }
        
        location /analysis {
              root   /workspace/analysis/dist;
            index  index.php index.html index.htm;
              try_files $uri $uri/ /analysis/index.php;
        }

            location /manage {
              root   /workspace/manage/dist;
            index  index.php index.html index.htm;
              try_files $uri $uri/ =502; #tryfile最后选项为重定向地址或返回异常状态
        }


        location @router {
            rewrite ^.*$ /index.html last;
        }


        error_page  404              /404.html;


        # redirect server error pages to the static page /50x.html
        #
        error_page   500 502 503 504  /50x.html;
        location = /50x.html {
            root   html;
        }

            location /blog {
                prox_pass http://backend;
                ### 下面都是次要关注项
                proxy_set_header Host $host;
                proxy_method POST;
                # 指定不转发的头部字段
                proxy_hide_header Cache-Control;
                proxy_hide_header Other-Header;
                # 指定转发的头部字段
                proxy_pass_header Server-IP;
                proxy_pass_header Server-Name;
                # 是否转发包体
                proxy_pass_request_body on | off;
                # 是否转发头部
                proxy_pass_request_headers on | off;
                # 显形/隐形 URI，上游发生重定向时，Nginx 是否同步更改 uri
                proxy_redirect on | off;
            }
 }
 
jupyter
```markdown
# top-level http config for websocket headers
# If Upgrade is defined, Connection = upgrade
# If Upgrade is empty, Connection = close
map $http_upgrade $connection_upgrade {
    default upgrade;
    ''      close;
}

# HTTP server to redirect all 80 traffic to SSL/HTTPS
server {
    listen 80;
    server_name HUB.DOMAIN.TLD;

    # Tell all requests to port 80 to be 302 redirected to HTTPS
    return 302 https://$host$request_uri;
}

# HTTPS server to handle JupyterHub
server {
    listen 443;
    ssl on;

    server_name HUB.DOMAIN.TLD;

    ssl_certificate /etc/letsencrypt/live/HUB.DOMAIN.TLD/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/HUB.DOMAIN.TLD/privkey.pem;

    ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
    ssl_prefer_server_ciphers on;
    ssl_dhparam /etc/ssl/certs/dhparam.pem;
    ssl_ciphers 'ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-DSS-AES128-GCM-SHA256:kEDH+AESGCM:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES128-SHA:DHE-DSS-AES128-SHA256:DHE-RSA-AES256-SHA256:DHE-DSS-AES256-SHA:DHE-RSA-AES256-SHA:AES128-GCM-SHA256:AES256-GCM-SHA384:AES128-SHA256:AES256-SHA256:AES128-SHA:AES256-SHA:AES:CAMELLIA:DES-CBC3-SHA:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!aECDH:!EDH-DSS-DES-CBC3-SHA:!EDH-RSA-DES-CBC3-SHA:!KRB5-DES-CBC3-SHA';
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_stapling on;
    ssl_stapling_verify on;
    add_header Strict-Transport-Security max-age=15768000;

    # Managing literal requests to the JupyterHub front end
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # websocket headers
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        proxy_set_header X-Scheme $scheme;

        proxy_buffering off;
    }

    # Managing requests to verify letsencrypt host
    location ~ /.well-known {
        allow all;
    }
}

## 非jupyterhub项目
server {
    listen 80;
    server_name NO_HUB.DOMAIN.TLD;

    # Tell all requests to port 80 to be 302 redirected to HTTPS
    return 302 https://$host$request_uri;
}
server {
    listen 443;
    ssl on;

    # INSERT OTHER SSL PARAMETERS HERE AS ABOVE
    # SSL cert may differ

    # Set the appropriate root directory
    root /var/www/html

    # Set URI handling
    location / {
        try_files $uri $uri/ =404;
    }

    # Managing requests to verify letsencrypt host
    location ~ /.well-known {
        allow all;
    }

}

server {
   listen 80;
   server_name auth-applet-pre.100credit.cn;
   rewrite ^/(.*)$ https://auth-applet-pre.100credit.cn/$1 permanent;
}

server {
    listen      443 ssl;
    server_name auth-applet-pre.100credit.cn;
    root   /opt/web_html/auth.insight.100credit.cn;
    index  index.html;

    ssl_certificate      /opt/nginx-1.4.7/conf/ssl/100credit.cn.crt;
    ssl_certificate_key  /opt/nginx-1.4.7/conf/ssl/100credit.cn.key;

    ssl_prefer_server_ciphers   on;

    ssl_protocols  SSLv3 TLSv1 TLSv1.2;
    ssl_ciphers  ALL:!ADH:!EXPORT56:RC4+RSA:+HIGH:+MEDIUM:+LOW:+SSLv2:+EXP;

    access_log logs/auth-applet-pre.100credit.cn_access.log;
    error_log  logs/auth-applet-pre.100credit.cn_error.log;

    location ~* \.(?:manifest|appcache|html?|xml|json)$ {
      expires -1;
    }

    location ~* \.(?:css|js)$ {
      try_files $uri =404;
      expires 1y;
      access_log off;
      add_header Cache-Control "public";
    }

        location ~ ^.+\..+$ {
      try_files $uri =404;
    }

    location /
    {
        root   /opt/web_html/auth.insight.100credit.cn;
        index  index.html index.htm;
        try_files $uri $uri/ /index.html;
                if ($request_uri ~* ^/index.html) {
                add_header Cache-Control 'no-cache, no-store';
        }
    }

    location ^~ /auth/
    {
        client_max_body_size    100m;
        proxy_set_header        Host  auth-insight-api.100credit.cn;
                proxy_set_header        Remote_Host  $host;
        proxy_set_header        X-Real-IP  $remote_addr;
        proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
        #rewrite_log             on;
        proxy_pass              http://auth-insight-api.100credit.cn;
    }

 }

```