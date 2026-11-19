from pathlib import Path
import sqlite3
import sys


def main() -> None:
    sample = Path(__file__).with_name("环境验证.db")
    print(f"Python {sys.version.split()[0]} · {sys.executable}")
    print(f"SQLite {sqlite3.sqlite_version}")
    if not sample.is_file():
        raise SystemExit("SQLite 驱动可用。原有环境验证.db 未找到。")

    with sqlite3.connect(sample.as_uri() + "?mode=ro", uri=True) as connection:
        result = connection.execute("SELECT id, msg FROM test ORDER BY id").fetchall()
    print(f"{sample.name} · test 表 · {len(result)} 行")
    for record in result:
        print(record)


if __name__ == "__main__":
    main()
