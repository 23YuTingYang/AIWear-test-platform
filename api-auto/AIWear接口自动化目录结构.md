# AIWear 接口自动化目录结构

```text
aiwear_api_test/
├── pytest.ini                       # pytest 配置
├── requirements.txt                 # 依赖清单
├── conftest.py                      # 公共夹具，如登录、token、图片准备
├── README.md                        # 项目说明
├── common/                          # 通用方法
│   ├── __init__.py
│   ├── request_client.py            # requests 封装
│   ├── assertion.py                 # 普通断言 + jsonschema 断言
│   ├── yaml_utils.py                # YAML 读取
│   └── logger.py                    # 日志配置
├── config/                          # 配置
│   ├── __init__.py
│   ├── settings.py                  # 配置加载入口
│   ├── env.yaml                     # base_url、超时等
│   └── accounts.yaml                # 测试账号
├── data/                            # YAML 测试数据
│   ├── user.yaml                    # 用户模块接口测试数据
│   ├── file.yaml                    # 文件模块接口测试数据
│   └── record.yaml                  # 记录模块接口测试数据
├── schema/                          # schema 定义
│   ├── common_result.json           # 通用 Result 结构
│   ├── user_schema.json             # 用户模块返回结构
│   ├── file_schema.json             # 文件模块返回结构
│   └── record_schema.json           # 记录模块返回结构
├── testcases/                       # 测试用例
│   ├── test_user.py                 # 用户模块接口测试
│   ├── test_file.py                 # 文件模块接口测试
│   └── test_record.py               # 记录模块接口测试
├── testdata/                        # 测试素材
│   └── images/                      # 上传、搜索等场景使用的图片资源
├── reports/                         # Allure 报告
│   ├── allure-results/              # Allure 原始结果
│   └── allure-report/               # Allure 可视化报告
└── logs/                            # 分级日志目录，日志文件按天按时间切分
    ├── info/                        # info 级别日志，如 info_2026-05-05_18-30-00.log
    └── error/                       # error 级别日志，如 error_2026-05-05_18-30-00.log
```
