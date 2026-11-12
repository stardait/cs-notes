"""简易计算器 —— Git 学习练习项目

这个程序故意写得很简单，方便你在学习 Git 的过程中逐步扩展它。
每加一个功能就提交一次，你就能看到项目是如何一步步成长起来的。

用法：
    python calculator.py
"""


def add(a, b):
    """加法"""
    return a + b


def subtract(a, b):
    """减法"""
    return a - b

def multiply(a, b):
    """乘法"""
    return a * b

def divide(a, b):
    """除法"""
    if b == 0:
        print("错误：除数不能为零")
        return None
    return a / b

def show_menu():
    """显示菜单"""
    print("=" * 30)
    print("      简易计算器 v1.0")
    print("=" * 30)
    print("  1. 加法")
    print("  2. 减法")
    print("  3. 乘法")
    print("  4. 除法")
    print("  0. 退出")
    print("=" * 30)


def main():
    """主程序"""
    while True:
        show_menu()
        choice = input("请选择操作：").strip()

        if choice == "0":
            print("再见！")
            break

        if choice not in ("1", "2", "3", "4"):
            print("无效选项，请重新选择\n")
            continue

        try:
            a = float(input("请输入第一个数："))
            b = float(input("请输入第二个数："))
        except ValueError:
            print("输入的不是数字，请重试\n")
            continue

        if choice == "1":
            result = add(a, b)
            symbol = "+"
        elif choice == "2":
            result = subtract(a, b)
            symbol = "-"
        elif choice == "3":
            result = multiply(a, b)
            symbol = "*"
        else:
            result = divide(a, b)
            symbol = "/"

        print(f"\n>>> {a} {symbol} {b} = {result}\n")


if __name__ == "__main__":
    main()
