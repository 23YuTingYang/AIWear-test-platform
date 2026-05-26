# AIWear 接口自动化

基于 `pytest + requests + YAML + jsonschema + Allure` 的接口自动化项目。

## 运行方式

1. 安装依赖：`pip install -r requirements.txt`
2. 执行测试：`pytest`
3. 生成 Allure 报告：
   `pytest --alluredir=reports/allure-results`
   `allure generate reports/allure-results -o reports/allure-report --clean`

## 说明

1. 测试环境地址默认读取 `config/env.yaml`
2. 测试账号读取 `config/accounts.yaml`
3. JWT token 优先从 Redis 读取，Redis 配置同样在 `config/env.yaml`
4. 图片素材默认读取工作区根目录下已有文件
5. 邮箱验证码登录和部分依赖后端异常的场景默认跳过
