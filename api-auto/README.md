# AIWear 接口自动化测试

本仓库用于维护 AIWear 系统接口自动化测试资产，核心项目位于 `api_auto_test/`，技术栈为 `pytest + requests + YAML + jsonschema + Allure`。

## 仓库内容

```text
.
├── api_auto_test/                     # 接口自动化测试工程
│   ├── common/                        # requests、断言、YAML、日志、Redis 等公共方法
│   ├── config/                        # 环境配置、账号配置
│   ├── data/                          # YAML 测试数据
│   ├── schema/                        # JSON Schema 定义
│   ├── testcases/                     # pytest 接口测试用例
│   ├── testdata/                      # 图片等测试素材
│   ├── report/                        # Allure 原始结果和静态报告
│   ├── conftest.py                    # 公共 fixture、登录态、测试素材准备
│   ├── pytest.ini                     # pytest 收集规则和默认运行参数
│   └── requirements.txt               # Python 依赖
├── AIWear接口测试用例.md               # 接口测试用例说明
├── AIWear接口自动化目录结构.md         # 项目目录结构说明
├── AIWear接口测试用例思维导图.xmind
└── 接口文档.md
```

## 环境准备

1. 进入测试工程目录：

   ```powershell
   cd D:\codes\ChangeClothes\接口自动化测试\api_auto_test
   ```

2. 安装依赖：

   ```powershell
   pip install -r requirements.txt
   ```

3. 确认配置文件：

   - `config/env.yaml`：测试环境地址、超时时间、Redis 配置、测试图片路径
   - `config/accounts.yaml`：测试账号信息

## 运行测试

在 `api_auto_test/` 目录下执行：

```powershell
pytest
```

`pytest.ini` 中已配置默认运行参数：

- 测试目录：`testcases`
- 用例文件：`test_*.py`
- 默认报告结果目录：`report/allure-results`
- 每次运行前清理旧的 Allure 结果：`--clean-alluredir`

## 查看报告

生成静态 Allure 报告：

```powershell
allure generate report/allure-results -o report/allure-report --clean
```

启动本地 Allure 报告服务：

```powershell
allure serve report/allure-results
```

## 配置说明

- `config/env.yaml`：维护 `base_url`、接口超时时间、Redis 配置和测试素材路径。
- `config/accounts.yaml`：维护测试账号信息，供登录和鉴权相关用例使用。
- `data/*.yaml`：维护接口级测试数据，测试脚本按模块读取对应数据文件。
- `schema/*.json`：维护返回结构的 JSON Schema，用于结构校验。
- `common/request_client.py`：封装接口请求发送逻辑。
- `common/assertion.py`：封装普通断言和 JSON Schema 断言逻辑。
- `testcases/*.py`：按模块组织接口用例，当前主要包括用户、文件、记录三类接口测试。

## 注意事项

1. 运行前需确认 `config/env.yaml` 中的 `base_url` 指向当前可用测试环境。
2. 部分登录态相关逻辑依赖 Redis 中的 token 或验证码数据，需确认 Redis 配置与测试环境一致。
3. 图片相关接口默认读取 `testdata/images/` 下的测试素材。
4. 测试结果会写入 `report/allure-results/`，静态 HTML 报告位于 `report/allure-report/index.html`。
