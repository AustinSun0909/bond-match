# Bond Match - 债券匹配系统

一个基于 Django 和 React 的债券匹配系统，帮助用户快速找到潜在的债券买家。

## 功能特点

- 🔍 债券代码搜索
- 📊 潜在买家匹配
- 👥 基金经理和交易员联系方式管理
- 📝 搜索历史记录
- 🔒 用户认证系统

## 技术栈

### 后端
- Python 3.x
- Django
- Django REST Framework
- PostgreSQL
- Django CORS Headers

### 前端
- React
- Axios
- Tailwind CSS

## 安装指南

### 前提条件
- Python 3.x
- Node.js
- PostgreSQL

### 后端设置

1. 创建并激活虚拟环境：
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置数据库：
- 创建 PostgreSQL 数据库
- 更新 `settings.py` 中的数据库配置

4. 运行迁移：
```bash
python manage.py makemigrations
python manage.py migrate
```

5. 创建超级用户：
```bash
python manage.py createsuperuser
```

6. 启动开发服务器：
```bash
python manage.py runserver
```

### 前端设置

1. 进入前端目录：
```bash
cd front-end
```

2. 安装依赖：
```bash
npm install
```

3. 启动开发服务器：
```bash
npm start
```

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

## API 端点

- `POST /api/bond/match/` - 债券匹配搜索
- `GET /api/search/history/` - 获取搜索历史
- `GET /api/issuers/` - 获取发行人列表

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