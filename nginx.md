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
        listen       80;
        server_name  localhost;
        
        root   /workspace/dist;

        #access_log  logs/host.access.log  main;

        location / {
            try_files $uri $uri/ @router;
            index  index.html index.htm;
        }
        
        location /analysis {
              root   /workspace/analysis/dist;
            index  index.php index.html index.htm;
              try_files $uri $uri/ /analysis/index.php;
        }

            location /manage {
              root   /workspace/manage/dist;
            index  index.php index.html index.htm;
              try_files $uri $uri/ =502; #tryfile最后选项为重定向地址或返回异常状态
        }


        location @router {
            rewrite ^.*$ /index.html last;
        }


        error_page  404              /404.html;


        # redirect server error pages to the static page /50x.html
        #
        error_page   500 502 503 504  /50x.html;
        location = /50x.html {
            root   html;
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