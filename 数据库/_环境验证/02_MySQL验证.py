from getpass import getpass
from importlib.metadata import version


def main() -> None:
    try:
        import pymysql
    except ImportError as error:
        raise SystemExit("当前 Python 缺少 PyMySQL。可执行 python -m pip install pymysql。") from error

    user = input("本机 MySQL 用户 [root]: ").strip() or "root"
    password = getpass("本机 MySQL 密码: ")
    try:
        with pymysql.connect(
            host="127.0.0.1",
            port=3306,
            user=user,
            password=password,
            database="learn",
            charset="utf8mb4",
            connect_timeout=5,
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT VERSION(), DATABASE(), @@character_set_connection")
                mysql_version, database, charset = cursor.fetchone()
                print(f"MySQL {mysql_version} · 库 {database} · 字符集 {charset}")
                print(f"PyMySQL {version('PyMySQL')}")
                cursor.execute("SHOW TABLES")
                for (table,) in cursor:
                    print(f"  {table}")
    except pymysql.MySQLError as error:
        raise SystemExit(f"MySQL 检查失败：{error}") from error


if __name__ == "__main__":
    main()
