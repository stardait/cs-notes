# 数据库学习环境

## MySQL 与 HeidiSQL

| 项目 | 本地值 |
|---|---|
| 服务器 | `127.0.0.1` |
| TCP 端口 | `3306` |
| 练习库 | `learn` |
| 账号 | 本机现有 MySQL 账号 |
| 字符集 | `utf8mb4` |

MySQL 未开机自启时，双击[启动MySQL.bat](启动MySQL.bat)，等服务启动后再连接。也可在 PowerShell 执行 `Get-Process mysqld -ErrorAction SilentlyContinue` 检查进程。用[停止MySQL.bat](停止MySQL.bat)时，按提示输入本机密码，由服务器正常关闭。无需为了每次学习而停止数据库。

打开 HeidiSQL，新会话选 MySQL TCP/IP，输入地址、端口和现用密码。课程文件及脚本不记录密码。通过 `Ctrl+T` 新建查询，运行下面一段。每条带结果的语句会显示一个结果集。

```sql
SELECT VERSION() AS mysql_version;
USE learn;
SELECT DATABASE() AS current_db;
SHOW TABLES;
```

第一个结果为服务端版本，本机是 `26.10.0`。第二个结果显示 `learn`。表列表可按[教材首页](../README_怎么用.md)核对。

### 常见问题

- 连接报 `2003`，先确认服务启动和端口。若 3306 被其他程序占用，查清使用者与本机配置，再决定如何处理。
- 报 `1045`，核对账号、当前密码和连接权限。
- 报 `1046`，新连接需要 `USE learn` 或使用完整表名。
- 服务器能连但找不到练习表，按教材首页核对表名和该章的配套 SQL。
- 本机路径变化时，在启动或停止脚本顶部更新对应的可执行文件路径。

## SQLite

SQLite 的练习是数据库文件，不经过 MySQL 服务。目录中的 `环境验证.db` 是原有环境样本，用 DB Browser for SQLite 或 VS Code 的 SQLite Viewer 打开，查看 `test` 表，应有一行「你好，数据库！」。也可以在 Python 标准库里 `import sqlite3`。从第 00–04 章跟练时使用 MySQL，后续章节会明确标注哪些语句可在 SQLite 执行。

## 无写入环境检查

在本目录打开 PowerShell。执行时可用现有 `python` 命令，或改成 Scoop 的 Python 完整路径。

```powershell
python .\01_环境验证.py
python .\02_MySQL验证.py
```

第一份检查 Python、SQLite 以及已有 SQLite 文件（只读）。第二份会提示本机账号和密码，只连接 `learn` 读取版本、设置及表清单。若提示缺少 `pymysql`，可从当前 Python 环境安装 `python -m pip install pymysql`。

数据库课程从[教材首页](../README_怎么用.md)进入。
