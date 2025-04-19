# 债券匹配系统 (Bond Matching System)

一个全栈应用，用于债券信息搜索、匹配和分析。

## 技术栈

### 后端
- Django + Django REST Framework
- PostgreSQL 数据库
- JWT 认证

### 前端
- React
- React Router
- Axios

## 安装说明

### 后端设置

1. 确保您已安装 Python 3.8+ 和 PostgreSQL

2. 创建并激活虚拟环境（可选）
   ```
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. 安装依赖
   ```
   pip install -r requirements.txt
   ```

4. 创建 PostgreSQL 数据库
   ```
   # 登录 PostgreSQL
   psql -U postgres
   
   # 创建数据库
   CREATE DATABASE bond_match;
   
   # 退出
   \q
   ```

5. 配置数据库
   编辑 `bond_match/settings.py` 中的 `DATABASES` 配置，确保用户名和密码正确。

6. 应用数据库迁移
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

7. 创建超级用户
   ```
   python manage.py createsuperuser
   ```

### 前端设置

1. 确保已安装 Node.js 和 npm

2. 进入前端目录
   ```
   cd front-end
   ```

3. 安装依赖
   ```
   npm install
   ```

## 运行应用

### 开发模式

1. 启动后端服务器
   ```
   python manage.py runserver
   ```

2. 启动前端开发服务器
   ```
   cd front-end
   npm start
   ```

### 使用脚本启动（Windows）

```
# PowerShell
.\start_dev.ps1
```

## 系统功能

- 用户注册和登录
- 密码重置
- 债券搜索
- 债券详情查看
- 债券匹配推荐
- 搜索历史记录

## API 端点

### 认证
- `/api/signup/` - 用户注册
- `/api/login/` - 用户登录
- `/api/token/` - 获取 JWT 令牌
- `/api/token/refresh/` - 刷新 JWT 令牌
- `/api/forgot-password/` - 请求密码重置
- `/api/reset-password/` - 重置密码

### 债券功能
- `/api/bonds/search/` - 搜索债券
- `/api/bonds/<bond_code>/` - 获取债券详情
- `/api/bonds/match/` - 匹配债券
- `/api/issuers/` - 获取发行人列表
- `/api/search-history/` - 获取用户搜索历史

## 项目结构

```
bond-match/
├── bond_match/          # Django 项目配置
├── securities/          # 债券应用
│   ├── models.py        # 数据模型
│   ├── views.py         # API 视图
│   └── urls.py          # URL 配置
├── front-end/           # React 前端
│   ├── src/
│   │   ├── components/  # React 组件
│   │   └── App.js       # 主应用组件
│   └── package.json     # 前端依赖
└── requirements.txt     # Python 依赖
```

## 使用示例

1. 登录系统
2. 输入债券代码进行搜索
3. 查看匹配的潜在买家
4. 查看基金经理和交易员联系方式

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件

## 联系方式

如有问题或建议，请通过以下方式联系我们：
- 项目 Issues
- 电子邮件：[your-email@example.com](mailto:your-email@example.com)

## 致谢

- Django 团队
- React 团队
- 所有贡献者 