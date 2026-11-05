# 接口自动化测试 · 账号服务

> 用 pytest + requests 对一套 mock 账号服务做接口自动化测试。

## 这是什么

测试某电商 App 的「账号模块」，负责用户注册、登录、查看个人资料、修改密码。 共17条用例

## 快速开始

本文档位于 practice/python/diagnose/，下面的命令都在这个目录下执行。

### 1. 环境准备

在本文档所在目录（practice/python/diagnose/）执行：
uv sync

### 2. 启动被测服务

在本文档所在目录执行：
python mock_server/server.py
不启动会报 ConnectionRefusedError，启动后的窗口不能关闭

### 3. 跑测试

在 practice/python/diagnose/ 目录下开新终端
主命令：python -m pytest -q
常用变体：python -m pytest test_register.py -q     只跑一个文件
          python -m pytest -m smoke -q             只跑冒烟 5 条
          python -m pytest -v                      显示每条用例名

### 4. 看报告

终端：11 passed, 6 xfailed
Allure：(需要 Java 8+；没装的话把 JAVA_HOME 指向任意 JDK 目录)
        例：$env:JAVA_HOME = "D:\PyCharm 2026.2.1\jbr" 
        python -m pytest --alluredir=allure-results --clean-alluredir （--clean-alluredir 表示先清空上一次的结果，不加会累积）
        allure serve allure-results 起网页

## 测试范围

注册 8 条 / 登录 3 条 / 改密 4 条 / 资料 2 条，共 17 条。

## 发现的问题

5个缺陷：

| 缺陷                  | 级别 | 理由                                         |
|-----------------------|------|----------------------------------------------|
| 越权查看他人资料      | P1   | userId 自增可枚举，能批量拿到手机号          |
| 改密后旧 token 未失效 | P1   | 改密是账号被盗后的自救手段，失效等于自救失败 |
| 登录失败返 200        | P2   | 协议层错误，功能正常                         |
| 16 位密码被拒         | P2   | 触发概率低、可绕过                           |
| 密码组成漏校验字母    | P2   | 弱口令能注册，但不直接泄露数据               |

## 技术栈

Python 3.12 / requests / pytest / allure-pytest