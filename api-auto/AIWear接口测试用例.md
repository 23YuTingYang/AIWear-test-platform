# AIWear 系统接口自动化测试用例

BaseURL: `http://139.199.222.234`

当前 `pytest --collect-only` 收集接口自动化用例共 `75` 条。

## 1. 执行顺序

1. `/api/user/send-code`
2. `/api/user/auth`
3. `/api/file/upload/image`
4. `/api/file/my-images`
5. `/api/file/search`
6. `/api/file/edit`
7. `/api/file/merge`
8. `/api/record/my`
9. `/api/user/logout`

## 2. 测试账号与素材

固定测试账号：

1. `Yang / Yyt1112`
2. `Xiao / Xxj1112`
3. 新用户账号由测试运行时动态生成，格式为 `NewUser_<随机后缀> / NewPass123`

当前代码实际使用的本地素材：

1. `接口自动化测试/api_auto_test/testdata/images/人物女人.jpg`
2. `接口自动化测试/api_auto_test/testdata/images/人物男人.jpg`
3. `接口自动化测试/api_auto_test/testdata/images/蓝色短袖.png`
4. `接口自动化测试/api_auto_test/testdata/images/红色短袖.jpg`
5. `接口自动化测试/api_auto_test/testdata/images/动物.jpg`

运行时临时构造的异常文件：

1. `empty.jpg`：空文件，用于空文件上传、空文件搜索。
2. `fake.jpg`：非图片内容伪装为 jpg，用于图片审核失败场景。

## 3. 接口1：发送验证码 `/api/user/send-code`（POST）

| 用例 ID                     | 用例名称    | 输入                        | 请求头 | 预期结果                                |
| ------------------------- | ------- | ------------------------- | --- | ----------------------------------- |
| `send_code_success`       | 正常发送验证码 | `email=2447005837@qq.com` | 无   | `code=200`，返回 `sendTo/expireTime`   |
| `send_code_empty_email`   | 邮箱为空    | `email=""`                | 无   | `code=400`，`message=邮箱不能为空`         |
| `send_code_missing_email` | 邮箱字段缺失  | `{}`                      | 无   | `code=400`，`message=邮箱不能为空`         |
| `send_code_invalid_email` | 邮箱格式错误  | `email=2447005837qq.com`  | 无   | `code=400`，`message=邮箱格式错误`         |
| `send_code_repeat`        | 重复发送验证码 | `email=2447005837@qq.com` | 无   | `code=400`，`message=验证码还没过期，请勿重复发送` |

说明：成功发送验证码前，测试代码会先删除 Redis 中旧验证码，避免历史验证码未过期影响首次发送成功场景。

## 4. 接口2：统一认证 `/api/user/auth`（POST）

| 用例 ID                          | 用例名称      | 输入                                                          | 请求头 | 预期结果                                        |
| ------------------------------ | --------- | ----------------------------------------------------------- | --- | ------------------------------------------- |
| `auth_password_success`        | 账号密码正常登录  | `account=Yang`，`password=Yyt1112`                           | 无   | `code=200`，返回 `userId/username/email/token` |
| `auth_password_wrong`          | 用户名或密码错误  | `account=Yang`，`password=wrong123`                          | 无   | `code=400`，`message=用户名或密码错误`               |
| `auth_empty_account`           | 账号为空      | `account=""`，`password=Yyt1112`                             | 无   | `code=400`，`message=账号不能为空`                 |
| `auth_missing_account`         | 账号字段缺失    | `password=Yyt1112`                                          | 无   | `code=400`，`message=账号不能为空`                 |
| `auth_empty_password`          | 密码为空      | `account=Yang`，`password=""`                                | 无   | `code=400`，`message=密码不能为空`                 |
| `auth_missing_password`        | 密码字段缺失    | `account=Yang`                                              | 无   | `code=400`，`message=密码不能为空`                 |
| `auth_email_success_manual`    | 邮箱验证码正常登录 | `account=2447005837@qq.com`，`verificationCode=Redis中的真实验证码` | 无   | `code=200`，返回 `userId/username/email/token` |
| `auth_email_wrong_code`        | 验证码错误     | `account=2447005837@qq.com`，`verificationCode=000000`       | 无   | `code=400`，`message=验证码不存在或已过期`             |
| `auth_email_empty_code`        | 验证码为空     | `account=2447005837@qq.com`，`verificationCode=""`           | 无   | `code=400`，`message=验证码不能为空`                |
| `auth_email_missing_code`      | 验证码字段缺失   | `account=2447005837@qq.com`                                 | 无   | `code=400`，`message=验证码不能为空`                |
| `auth_new_account_auto_create` | 新账号自动创建   | `account=NewUser_<随机后缀>`，`password=NewPass123`              | 无   | `code=200`，返回 `userId/username/email/token` |

说明：邮箱验证码成功登录不是手工填写验证码，测试代码会从 Redis 中读取 Java 服务写入的真实验证码。

## 5. 接口3：上传图片 `/api/file/upload/image`（POST）

| 用例 ID                   | 用例名称               | 输入                                                 | 请求头                               | 预期结果                                   |
| ----------------------- | ------------------ | -------------------------------------------------- | --------------------------------- | -------------------------------------- |
| `upload_person_success` | 上传人物图成功            | `人物女人.jpg`                                         | `Authorization=Bearer Yang-token` | `code=200`，返回 `url/fileName/fileSize`  |
| `upload_cloth_success`  | 上传服装图成功            | `蓝色短袖.png`                                         | `Authorization=Bearer Yang-token` | `code=200`，返回 `url/fileName/fileSize`  |
| `upload_empty_file`     | 空文件上传失败            | 运行时空文件 `empty.jpg`                                 | `Authorization=Bearer Yang-token` | `code=400`，`message=图片文件不能为空`          |
| `upload_missing_file`   | 缺少文件参数             | 不传 `file`                                          | `Authorization=Bearer Yang-token` | `code=400`，`message=图片文件不能为空`          |
| `upload_animal`         | 上传非人物非服装           | `动物.jpg`                                           | `Authorization=Bearer Yang-token` | `code=400`，`message=图片审核不通过,图片不是人物或服装` |
| `upload_missing_auth`   | 缺少 Authorization   | `人物女人.jpg`                                         | 无                                 | `code=400`，`message=缺少请求头令牌`           |
| `upload_invalid_auth`   | Authorization 格式错误 | `人物女人.jpg`                                         | `Authorization=token-x`           | `code=400`，`message=请求头令牌格式错误`         |
| `upload_repeat`         | 重复上传同一图片           | `人物女人.jpg`，先上传一次后再上传                               | `Authorization=Bearer Yang-token` | `code=200`，返回 `url/fileName/fileSize`  |
| `upload_octet_stream`   | MIME 异常但内容正常       | `人物女人.jpg`，`Content-Type=application/octet-stream` | `Authorization=Bearer Yang-token` | `code=200`，返回 `url/fileName/fileSize`  |
| `upload_fake_jpg`       | 非图片内容伪装上传          | 运行时伪图片 `fake.jpg`                                  | `Authorization=Bearer Yang-token` | `code=400`，`message=图片审核不通过,图片不是人物或服装` |

## 6. 接口4：我的图片列表 `/api/file/my-images`（GET）

| 用例 ID                      | 用例名称               | 输入  | 请求头                                  | 预期结果                                    |
| -------------------------- | ------------------ | --- | ------------------------------------ | --------------------------------------- |
| `my_images_yang`           | Yang 查询自己的图片列表     | 无   | `Authorization=Bearer Yang-token`    | `code=200`，包含 Yang 自己上传的图片，不包含 Xiao 的图片 |
| `my_images_xiao`           | Xiao 查询自己的图片列表     | 无   | `Authorization=Bearer Xiao-token`    | `code=200`，包含 Xiao 自己上传的图片，不包含 Yang 的图片 |
| `my_images_new_user_empty` | 首次用户无图片            | 无   | `Authorization=Bearer NewUser-token` | `code=200`，`data=[]`                    |
| `my_images_missing_auth`   | 缺少 Authorization   | 无   | 无                                    | `code=400`，`message=缺少请求头令牌`            |
| `my_images_invalid_auth`   | Authorization 格式错误 | 无   | `Authorization=token-x`              | `code=400`，`message=请求头令牌格式错误`          |

## 7. 接口5：搜索图片 `/api/file/search`（POST）

| 用例 ID                     | 用例名称               | 输入                  | 请求头                               | 预期结果                           |
| ------------------------- | ------------------ | ------------------- | --------------------------------- | ------------------------------ |
| `search_by_text`          | 文搜图成功              | `query=红色短袖`        | `Authorization=Bearer Yang-token` | `code=200`                     |
| `search_by_image`         | 图搜图成功              | `file=红色短袖.jpg`     | `Authorization=Bearer Yang-token` | `code=200`                     |
| `search_no_query_no_file` | query 和 file 同时为空  | 不传 `query` 和 `file` | `Authorization=Bearer Yang-token` | `code=200`，`data=[]`           |
| `search_empty_query`      | query 为空字符串        | `query=""`          | `Authorization=Bearer Yang-token` | `code=200`，`data=[]`           |
| `search_long_query`       | 超长 query           | 长文本 `query`         | `Authorization=Bearer Yang-token` | `code=200`                     |
| `search_empty_file`       | file 为空文件          | 运行时空文件 `empty.jpg`  | `Authorization=Bearer Yang-token` | `code=200`，`data=[]`           |
| `search_missing_auth`     | 缺少 Authorization   | `query=红色短袖`        | 无                                 | `code=400`，`message=缺少请求头令牌`   |
| `search_invalid_auth`     | Authorization 格式错误 | `query=红色短袖`        | `Authorization=token-x`           | `code=400`，`message=请求头令牌格式错误` |
| `search_user_isolation`   | 用户隔离验证             | `query=红色短袖`        | `Authorization=Bearer Xiao-token` | `code=200`，结果不包含 Yang 上传的红色短袖图 |

## 8. 接口6：编辑图片 `/api/file/edit`（POST）

| 用例 ID                      | 用例名称              | 输入                                         | 请求头                               | 预期结果                                      |
| -------------------------- | ----------------- | ------------------------------------------ | --------------------------------- | ----------------------------------------- |
| `edit_success`             | 正常编辑自己的图片         | `image=Yang人物图URL`，`instruction=把上衣改成蓝色短袖` | `Authorization=Bearer Yang-token` | `code=200`，返回 `url/saveUrl`               |
| `edit_empty_image`         | image 为空          | `image=""`，`instruction=改蓝色`               | `Authorization=Bearer Yang-token` | `code=400`，`message=图片不能为空`               |
| `edit_empty_instruction`   | instruction 为空    | `image=Yang人物图URL`，`instruction=""`        | `Authorization=Bearer Yang-token` | `code=400`，`message=编辑图片的指令不能为空`          |
| `edit_missing_image`       | 缺少 image 字段       | 不传 `image`，`instruction=改蓝色`               | `Authorization=Bearer Yang-token` | `code=400`，`message=图片不能为空`               |
| `edit_missing_instruction` | 缺少 instruction 字段 | `image=Yang人物图URL`，不传 `instruction`        | `Authorization=Bearer Yang-token` | `code=400`，`message=编辑图片的指令不能为空`          |
| `edit_other_user_image`    | 编辑他人图片失败          | `image=Yang人物图URL`，`instruction=改红色`       | `Authorization=Bearer Xiao-token` | `code=400`，`message=无权限编辑此图片,只能编辑自己上传的图片` |
| `edit_invalid_url`         | 非法 URL            | `image=not-a-url`，`instruction=改蓝色`        | `Authorization=Bearer Yang-token` | `code=400`                                |
| `edit_long_instruction`    | 超长 instruction    | `image=Yang人物图URL`，长文本 `instruction`       | `Authorization=Bearer Yang-token` | `code=200`，返回 `url/saveUrl`               |
| `edit_missing_auth`        | 缺少 Authorization  | `image=Yang人物图URL`，`instruction=改蓝色`       | 无                                 | `code=400`，`message=缺少请求头令牌`              |

## 9. 接口7：合并图片 `/api/file/merge`（POST）

| 用例 ID                       | 用例名称              | 输入                                                                     | 请求头                               | 预期结果                             |
| --------------------------- | ----------------- | ---------------------------------------------------------------------- | --------------------------------- | -------------------------------- |
| `merge_success`             | 正常合并自己的图片         | `image1=Yang人物图URL`，`image2=Yang蓝色短袖URL`，`instruction=把第二张衣服穿到第一张人物身上` | `Authorization=Bearer Yang-token` | `code=200`，返回 `url/saveUrl`      |
| `merge_empty_image1`        | image1 为空         | `image1=""`，`image2=Yang蓝色短袖URL`，`instruction=merge`                   | `Authorization=Bearer Yang-token` | `code=400`，`message=图片1不能为空`     |
| `merge_empty_image2`        | image2 为空         | `image1=Yang人物图URL`，`image2=""`，`instruction=merge`                    | `Authorization=Bearer Yang-token` | `code=400`，`message=图片2不能为空`     |
| `merge_empty_instruction`   | instruction 为空    | `image1=Yang人物图URL`，`image2=Yang蓝色短袖URL`，`instruction=""`              | `Authorization=Bearer Yang-token` | `code=400`，`message=合并指令不能为空`    |
| `merge_missing_instruction` | 缺少 instruction 字段 | `image1=Yang人物图URL`，`image2=Yang蓝色短袖URL`                               | `Authorization=Bearer Yang-token` | `code=400`，`message=合并指令不能为空`    |
| `merge_missing_image1`      | 缺少 image1 字段      | `image2=Yang蓝色短袖URL`，`instruction=merge`                               | `Authorization=Bearer Yang-token` | `code=400`，`message=图片1不能为空`     |
| `merge_missing_image2`      | 缺少 image2 字段      | `image1=Yang人物图URL`，`instruction=merge`                                | `Authorization=Bearer Yang-token` | `code=400`，`message=图片2不能为空`     |
| `merge_other_user_images`   | 合并他人图片失败          | `image1=Yang人物图URL`，`image2=Yang蓝色短袖URL`，`instruction=merge`           | `Authorization=Bearer Xiao-token` | `code=400`，`message=只能合并自己上传的图片` |
| `merge_cross_user_images`   | 混合两用户图片失败         | `image1=Yang人物图URL`，`image2=Xiao人物图URL`，`instruction=merge`            | `Authorization=Bearer Yang-token` | `code=400`，`message=只能合并自己上传的图片` |
| `merge_missing_auth`        | 缺少 Authorization  | `image1=Yang人物图URL`，`image2=Yang蓝色短袖URL`，`instruction=merge`           | 无                                 | `code=400`，`message=缺少请求头令牌`     |

## 10. 接口8：我的记录 `/api/record/my`（GET）

| 用例 ID                   | 用例名称               | 输入              | 请求头                               | 预期结果                             |
| ----------------------- | ------------------ | --------------- | --------------------------------- | -------------------------------- |
| `record_all`            | 查询全部记录             | 无               | `Authorization=Bearer Yang-token` | `code=200`                       |
| `record_edit`           | 按 edit 查询          | `action=edit`   | `Authorization=Bearer Yang-token` | `code=200`，所有返回记录 `action=edit`  |
| `record_merge`          | 按 merge 查询         | `action=merge`  | `Authorization=Bearer Yang-token` | `code=200`，所有返回记录 `action=merge` |
| `record_empty_action`   | action 为空字符串       | `action=""`     | `Authorization=Bearer Yang-token` | `code=200`，等价于查全部                |
| `record_unknown_action` | action 为未知值        | `action=delete` | `Authorization=Bearer Yang-token` | `code=200`，`data=[]`             |
| `record_missing_auth`   | 缺少 Authorization   | 无               | 无                                 | `code=400`，`message=缺少请求头令牌`     |
| `record_invalid_auth`   | Authorization 格式错误 | 无               | `Authorization=token-x`           | `code=400`，`message=请求头令牌格式错误`   |
| `record_user_isolation` | 用户记录隔离             | 无               | `Authorization=Bearer Xiao-token` | `code=200`，结果不包含 Yang 的图片上下文     |

说明：Yang 的正向记录查询会按需触发编辑和合并前置，以确保存在 `edit/merge` 记录。

## 11. 接口9：退出登录 `/api/user/logout`（POST）

| 用例 ID                   | 用例名称               | 输入  | 请求头                                | 预期结果                                |
| ----------------------- | ------------------ | --- | ---------------------------------- | ----------------------------------- |
| `logout_success`        | 正常登出               | 无   | `Authorization=Bearer Yang-token`  | `code=200`，`data=登出成功`              |
| `logout_missing_header` | 缺少 Authorization   | 无   | 无                                  | `code=400`，`message=缺少请求头令牌`        |
| `logout_empty_header`   | Authorization 为空   | 无   | `Authorization=""`                 | `code=400`，`message=缺少请求头令牌`        |
| `logout_invalid_header` | Authorization 格式错误 | 无   | `Authorization=token-x`            | `code=400`，`message=请求头令牌格式错误`      |
| `logout_fake_jwt`       | 非法 JWT             | 无   | `Authorization=Bearer abc.def.ghi` | `code=500`，该用例标记为 `unstable`        |
| `logout_old_token`      | token 已不存在         | 无   | 先登录并登出，再复用失效 token                 | `code=500`，`message=登出失败.请稍后重试`     |
| `logout_repeat`         | 重复登出               | 无   | 同一个 token 连续登出两次                   | 第二次 `code=500`，`message=登出失败.请稍后重试` |
| `logout_bearer_blank`   | Bearer 后只有空格       | 无   | `Authorization=Bearer `            | `code=400`，`message=请求头令牌格式错误`      |

## 12. 当前覆盖汇总

| 模块     | 用例数 |
| ------ | ---:|
| 发送验证码  | 5   |
| 统一认证   | 11  |
| 上传图片   | 10  |
| 我的图片列表 | 5   |
| 搜索图片   | 9   |
| 编辑图片   | 9   |
| 合并图片   | 10  |
| 我的记录   | 8   |
| 退出登录   | 8   |
| 合计     | 75  |
