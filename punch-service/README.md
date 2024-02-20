# Service

This project was generated via [manage-fastapi](https://ycd.github.io/manage-fastapi/)! :tada:

---

## License

This project is licensed under the terms of the MIT license.

---

### 目录结构描述
```
.
├── punch-service              # 后端服务
│   ├── Dockerfile
│   ├── LICENSE
│   ├── Makefile
│   ├── README.md
│   ├── app
│   │   ├── api             # 接口的路由入口
│   │   ├── core            # Setting文件夹
│   │   ├── crud            # 涉及数据库操作的函数
│   │   ├── database.py     # SqlAlchemy初始化文件
│   │   ├── http_client.py  # http客户端初始化文件
│   │   ├── main.py         # 启动文件
│   │   ├── middleware      # 路由中间件
│   │   ├── models          # FastApi定义的模型
│   │   │   ├── api         # 本地接口的模型
│   │   │   └── holder      # 第三方接口的模型
│   │   ├── scheduler.py    # 调度器初始化文件
│   │   ├── schemas         # ORM模型
│   │   │   ├── api         # 本地ORM模型
│   │   └── utils           # 工具集合
│   ├── docker              # docker相关
├── punch-web                  # 前端服务      
```