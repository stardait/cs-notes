"""
================================================================================
环境验证脚本
================================================================================
用途：确认你的数据库学习环境全部就绪。

运行：python 01_环境验证.py

如果这个文件全部通过，说明你可以开始学数据库了。
================================================================================
"""

import sys
import sqlite3
import os


def check(title, fn):
    """执行一项检查，打印结果"""
    print(f"  {title:<32}", end="")
    try:
        result = fn()
        print(f"✅ {result}")
        return True
    except Exception as e:
        print(f"❌ {e}")
        return False


print()
print("=" * 70)
print("数据库环境验证")
print("=" * 70)
print()

results = []

# ---------- 1. Python 环境 ----------
print("【1】Python 环境")
results.append(check("Python 版本", lambda: f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"))
results.append(check("Python 路径", lambda: sys.executable))
print()

# ---------- 2. sqlite3 模块 ----------
print("【2】sqlite3 模块")


def check_sqlite_version():
    return sqlite3.sqlite_version


results.append(check("SQLite 版本", check_sqlite_version))
results.append(check("sqlite3 模块可用", lambda: "已导入"))
print()

# ---------- 3. 实际建库测试 ----------
print("【3】建库测试")

DB_FILE = "环境验证.db"

# 清理旧文件
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)
    print(f"  （已清理旧的 {DB_FILE}）")


def test_create():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, msg TEXT)")
    conn.commit()
    conn.close()
    return DB_FILE


results.append(check("创建数据库文件", test_create))


def test_insert():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("INSERT INTO test (msg) VALUES (?)", ("你好，数据库！",))
    conn.commit()
    conn.close()
    return "插入 1 条记录"


results.append(check("插入数据", test_insert))


def test_query():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT id, msg FROM test")
    rows = cur.fetchall()
    conn.close()
    if len(rows) == 1:
        return f"查到 {rows[0][1]}"
    raise ValueError(f"预期 1 行，实际 {len(rows)} 行")


results.append(check("查询数据", test_query))


def test_file_size():
    size = os.path.getsize(DB_FILE)
    return f"{size} 字节"


results.append(check("数据库文件大小", test_file_size))
print()

# ---------- 4. 可视化工具检查 ----------
print("【4】可视化工具")
print("  （这个脚本无法自动检测，请手动确认下面两项）")
print()
print("  □ DB Browser for SQLite 能打开")
print(f"      双击桌面「DB Browser for SQLite」→ 打开 → 选择 {os.path.abspath(DB_FILE)}")
print()
print("  □ VS Code 能查看 .db 文件")
print(f"      在 VS Code 里点开 {DB_FILE} → 应该能看到 test 表")
print()

# ---------- 5. 汇总 ----------
print("=" * 70)
passed = sum(1 for r in results if r)
total = len(results)
print(f"自动化检查：{passed}/{total} 通过")
print("=" * 70)
print()

if passed == total:
    print("🎉 环境全部就绪！")
    print()
    print("接下来：")
    print("  1. 用 DB Browser 打开这个 环境验证.db，看看里面的 test 表")
    print("  2. 打开教程第一个文件开始学")
    print()
    print(f"数据库文件位置：{os.path.abspath(DB_FILE)}")
else:
    print("⚠️  有检查未通过，请把上面的 ❌ 信息发给助手")

print()
print("─" * 70)
print("提示：这个 环境验证.db 可以留着，也可以删掉，不影响学习。")
print("─" * 70)
print()
