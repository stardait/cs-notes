"""
================================================================================
第 9 章 · 面向对象
文件 02：属性与方法进阶
================================================================================

【学习目标】
    1. 分清「类属性」和「实例属性」，知道 Python 查属性的顺序
    2. 用 @property 把方法变成「看起来像属性」的东西，并能做校验
    3. 用 @staticmethod 定义不依赖 self / cls 的工具方法
    4. 用 @classmethod 定义以「类」为操作对象的方法，理解 cls 是什么

【怎么用这个文件】
    - 从上往下读，每个「知识点」是一小节
    - 「输出」块是运行后的实际结果，代码下面的注释说明「这行为什么这么写」
    - 直接运行：python 02_属性与方法进阶.py

【前置知识】
    - 01_类与对象.py（class、__init__、self、实例属性、实例方法）
    - 第 3 章：装饰器语法 @ 没见过也没关系，正文会解释
================================================================================
"""

# ==============================================================================
# 知识点 1：类属性 —— 写在类里、但不在 __init__ 里的属性
# ==============================================================================
#
# 【讲解】属性有两种：
#   实例属性：在 __init__ 里用 self.xxx 创建 —— 每个对象一份，像「每个人自己的手机」
#   类属性：  直接写在类体里 —— 所有对象共享一份，像「班级共用的饮水机」
#
# 【重点】查找顺序：先找对象自己的（实例属性），找不到再找类的（类属性）。

class Student:
    school = "第一中学"         # 类属性：全校共享
    total = 0                   # 类属性：用来数一共创建了多少个学生

    def __init__(self, name):
        self.name = name        # 实例属性：每个人独有
        Student.total += 1      # 每创建一个对象，类属性 +1

    def show(self):
        """注意：读 school 时没写 self.school，也能读到类属性。"""
        print(f"{self.name} 在 {self.school} 上学")


print("--- 类属性被所有对象共享 ---")
s1 = Student("张三")
s2 = Student("李四")
s1.show()
s2.show()
print(f"Student.school = {Student.school}")
print(f"s1.school = {s1.school}，s2.school = {s2.school}")
print(f"一共创建了 {Student.total} 个学生")

# 输出：
# --- 类属性被所有对象共享 ---
# 张三 在 第一中学 上学
# 李四 在 第一中学 上学
# Student.school = 第一中学
# s1.school = 第一中学，s2.school = 第一中学
# 一共创建了 2 个学生
#
# 【重点】上面三个地方读 school，读到的都是同一个值 —— 因为它压根没存在
#         对象里，而是存在类上。s1.school 只是「借」着类的属性来用。


# ==============================================================================
# 知识点 2：实例属性会「遮蔽」类属性 —— 最关键的一个坑
# ==============================================================================
#
# 【讲解】给某个对象单独赋值同名属性，并不会改类属性，
#         而是在这个对象身上「新建」一个实例属性，把类属性挡住（遮蔽）。

print("\n--- 修改类属性 vs 修改实例属性 ---")
s1.school = "实验中学"          # 这行并没有改类属性！
print(f"Student.school = {Student.school}，s2.school = {s2.school}")
print(f"s1.school = {s1.school}   ← 被自己的实例属性挡住了")
print(f"s1 自己的属性字典：{s1.__dict__}")

# 输出：
# --- 修改类属性 vs 修改实例属性 ---
# Student.school = 第一中学，s2.school = 第一中学
# s1.school = 实验中学   ← 被自己的实例属性挡住了
# s1 自己的属性字典：{'name': '张三', 'school': '实验中学'}
#
# 【为什么】s1.school = "实验中学" 这个动作，Python 的规则是：
#         先看 s1 自己有没有 school，没有就在 s1 身上新建一个，而不是去改类。
#
# 【常见错误】以为「通过对象改就等于改了类」，结果别的对象毫无变化。
#         想改类属性，必须直接写类名：Student.school = "第二中学"。

# ==============================================================================
# 知识点 3：类属性的经典陷阱 —— 可变对象被共享
# ==============================================================================
#
# 【讲解】如果类属性是列表、字典这类可变对象，所有对象操作的都是同一个！
#         这是新手最崩溃的 bug：明明只 append 了一次，怎么两个对象都有？

class BadCart:
    items = []                  # 【错误示范】类属性是列表 = 全员共用一个购物车

    def __init__(self, owner):
        self.owner = owner

    def add(self, item):
        self.items.append(item)  # 读的是类属性，改的也是那个共享列表


print("\n--- 错误示范：共享的可变类属性 ---")
cart1 = BadCart("张三")
cart2 = BadCart("李四")
cart1.add("苹果")
cart2.add("香蕉")
print(f"张三的购物车：{cart1.items}")
print(f"李四的购物车：{cart2.items}")

# 输出：
# --- 错误示范：共享的可变类属性 ---
# 张三的购物车：['苹果', '香蕉']
# 李四的购物车：['苹果', '香蕉']
#
# 【为什么】self.items.append() 是「读」self.items 再「修改它指向的列表」。
#         读的时候走的是类属性（对象自己没有），于是两人拿到同一个列表。
#         类属性适合放不可变的共享值：常量、计数器、默认配置。
#         凡是每个对象要各存一份的数据（尤其是 list / dict / set），
#         一定在 __init__ 里用 self.xxx = [] 创建。

class GoodCart:
    def __init__(self, owner):
        self.owner = owner
        self.items = []         # 【正确】每个对象在 __init__ 里新建自己的列表

    def add(self, item):
        self.items.append(item)


print("\n--- 正确示范：在 __init__ 里创建 ---")
gc1 = GoodCart("张三")
gc2 = GoodCart("李四")
gc1.add("苹果")
gc2.add("香蕉")
print(f"张三：{gc1.items}，李四：{gc2.items}")

# 输出：
# --- 正确示范：在 __init__ 里创建 ---
# 张三：['苹果']，李四：['香蕉']


# ==============================================================================
# 知识点 4：@property —— 让方法「长得像属性」
# ==============================================================================
#
# 【讲解】现实里常有这种需求：价格不能是负数。
#   用普通属性 self.price = price，别人随手 p.price = -100 你拦不住；
#   改用方法 p.set_price(100)，能拦住，但写起来不再像「设置属性」。
#
#   @property 就是折中方案：外面用起来像属性（不加括号），
#   里面其实是个方法，能塞校验逻辑。
#
# 【类比】酒店前台：你说「我要 301 房」，听着像直接拿钥匙（属性），
#         其实前台还要查一下你的订单（方法里的校验逻辑）。

class Product:
    def __init__(self, name, price):
        self.name = name
        self.price = price          # 注意：这里会走下面的 price.setter

    @property                       # 把 price 方法变成「只能读的属性」
    def price(self):
        """读取价格时调用。"""
        return self._price          # 真正的数据存在 _price 里

    @price.setter                   # 声明「给 price 赋值时」走这里
    def price(self, value):
        """设置价格时调用，顺便做校验。"""
        if value < 0:
            raise ValueError(f"价格不能是负数：{value}")
        self._price = value


print("\n--- @property 的读和写 ---")
p = Product("《Python 入门》", 59.9)
print(f"书名：{p.name}，价格：{p.price}   ← 不加括号，像属性一样读")
p.price = 49.9                      # 赋值不会报错，因为它有 setter
print(f"打折后：{p.price}，真正的数据存在 _price：{p._price}")

# 输出：
# --- @property 的读和写 ---
# 书名：《Python 入门》，价格：59.9   ← 不加括号，像属性一样读
# 打折后：49.9，真正的数据存在 _price：49.9
#
# 【注意】p.price 后面绝对不能加括号，否则报
#         TypeError: 'float' object is not callable —— 数字 49.9 不能调用。

print("\n--- setter 里的校验真的会生效 ---")
try:
    p.price = -10                   # 赋一个负数
except ValueError as e:
    print(f"被拦住了：ValueError: {e}")
print(f"价格还是原来的：{p.price}")

# 输出：
# --- setter 里的校验真的会生效 ---
# 被拦住了：ValueError: 价格不能是负数：-10
# 价格还是原来的：49.9
#
# 【重点】校验逻辑写在 setter 里，所有赋值路径都会经过它，
#         这就保证了对象「永远处于合法状态」。这是 property 最大的价值。

print("\n--- 只有 getter 没有 setter：只读属性 ---")


class Circle:
    def __init__(self, radius):
        self.radius = radius

    @property
    def area(self):
        """面积是算出来的，不该被赋值。"""
        return 3.14159 * self.radius ** 2


c = Circle(2)
print(f"半径 2 的圆面积：{c.area}")
try:
    c.area = 100                    # 没有 setter，赋值会被拒绝
except AttributeError as e:
    print(f"想改面积？AttributeError: {e}")

# 输出：
# --- 只有 getter 没有 setter：只读属性 ---
# 半径 2 的圆面积：12.56636
# 想改面积？AttributeError: property 'area' of 'Circle' object has no setter
#
# 【重点】「算出来的属性」只提供 getter，就等于声明了它是只读的。


# ==============================================================================
# 知识点 5：@staticmethod 与 @classmethod —— 不靠对象的方法
# ==============================================================================
#
# 【讲解】有些方法逻辑上属于这个类，但压根不需要碰对象的数据，
#   比如「判断字符串是不是手机号」——它跟具体哪个用户没关系。
#   这种就叫静态方法：没有 self，也没有 cls，就是个普通函数，
#   只是为了「归类清晰」，被放进类里。
#   类方法则第一个参数是 cls（class 的缩写），代表「这个类本身」，
#   最典型的用途是做「替代构造函数」：__init__ 只有一种调用方式，
#   但你可能还需要「从字符串创建对象」这第二个入口。

class Validator:
    """校验工具类。方法都不依赖对象状态。"""

    @staticmethod
    def is_phone(text):
        """判断是否是 11 位数字的手机号。"""
        return len(text) == 11 and text.isdigit()


class Student2:
    school = "第一中学"

    def __init__(self, name, age):
        self.name = name
        self.age = age

    @classmethod
    def from_string(cls, text):
        """替代构造函数：从 '姓名,年龄' 这样的字符串创建对象。"""
        name, age_text = text.split(",")
        return cls(name, int(age_text))     # cls(...) 等价于 Student2(...)

    @classmethod
    def school_info(cls):
        """读类属性时用 cls，而不是写死类名。"""
        return f"{cls.__name__} 的校名是 {cls.school}"

    def show(self):
        print(f"{self.name}，{self.age} 岁，在 {self.school}")


print("\n--- 静态方法：用类名直接调用 ---")
print(f"13800138000 是手机号？{Validator.is_phone('13800138000')}")
print(f"12345 是手机号？{Validator.is_phone('12345')}")

# 输出：
# --- 静态方法：用类名直接调用 ---
# 13800138000 是手机号？True
# 12345 是手机号？False
#
# 【注意】静态方法用类名调、用对象调都行，但两种方式都不会自动传 self 或 cls。

print("\n--- 类方法：替代构造函数 ---")
a = Student2("张三", 18)                    # 常规方式
b = Student2.from_string("李四,19")          # 从字符串创建
a.show()
b.show()
print(f"两种方式造出来的类型一样：{type(a) is type(b)}")
print(f"类方法读类属性：{Student2.school_info()}")

# 输出：
# --- 类方法：替代构造函数 ---
# 张三，18 岁，在 第一中学
# 李四，19 岁，在 第一中学
# 两种方式造出来的类型一样：True
# 类方法读类属性：Student2 的校名是 第一中学
#
# 【重点】类方法里要用 cls 而不是写死 Student2。因为 cls 会「跟着子类走」：
#         子类调用时 cls 就是子类，写死类名就永远只能操作父类。
#         这一点到 03_继承.py 会亲眼看到效果。


# ==============================================================================
# 知识点 6：三种方法 + 两种属性，一张表分清
# ==============================================================================
#
#   写法                        第一个参数    能改对象状态     推荐调用方式
#   --------------------------  ------------  --------------  --------------
#   实例方法  def f(self)       self          ✅ 能改自己      obj.f()
#   类方法    @classmethod      cls           ✅ 能改类属性    类名.f()
#   静态方法  @staticmethod     无            ❌ 碰不到状态    类名.f()
#   实例属性  self.x = ...      无            每人一份          obj.x
#   类属性    x = ...           无            全体共享          类名.x
#
# 【判断口诀】
#   要读写「自己」的数据  → 实例方法
#   要读写「整个类」的数据 → 类方法
#   什么都不读写，纯工具   → 静态方法
# 【重点】用对象调用类方法时，传进去的 cls 依然是「类」，不是对象。
#         这就是 cls 和 self 的本质区别：一个指类，一个指实例。
#         把上面 Student2.school_info() 改成 b.school_info() 也一样。


# ==============================================================================
# 知识点 7：两个高频错误
# ==============================================================================

print("\n--- 错误 1：property 当成方法加括号调用 ---")


class Book:
    def __init__(self, title):
        self.title = title

    @property
    def info(self):
        return f"《{self.title}》"


try:
    print(Book("流畅的 Python").info())
except TypeError as e:
    print(f"报错：TypeError: {e}")

# 输出：
# --- 错误 1：property 当成方法加括号调用 ---
# 报错：TypeError: 'str' object is not callable
#
# 【为什么】Book(...).info 已经把字符串算出来了，后面再加 () 就变成
#         "《流畅的 Python》"()，字符串当然是「不可调用」的。
# 【常见错误】静态方法没有 self。在静态方法里写 self.value，会报
#         NameError: name 'self' is not defined ——注意是「名字没定义」。


# ==============================================================================
# 【本章小结】
# ==============================================================================
#
# 1. 类属性写在类体里，全体对象共享；实例属性写在 __init__ 里，每个对象一份
# 2. 查找顺序：先实例属性，再类属性 —— 所以实例属性会「遮蔽」同名类属性
# 3. obj.attr = x 只会在对象身上新建实例属性，不会修改类属性；
#    想改类属性必须写 类名.attr = x
# 4. 类属性若为 list / dict 会被所有对象共享，可变的就该在 __init__ 里新建
# 5. @property 让方法像属性一样访问（不加括号），getter 负责读，setter 负责写
# 6. setter 里做校验，保证对象状态永远合法；只写 getter 就是只读属性
# 7. @staticmethod 没有 self / cls，本质是放在类里的普通函数，用于工具方法
# 8. @classmethod 第一个参数是 cls，最适合做「替代构造函数」，且对子类有效
# 9. 口诀：读写自己用实例方法，读写类用类方法，纯工具用静态方法


# ==============================================================================
# 【动手练习】
# ==============================================================================
#
# 练习 1：写一个 Temperature 类，用 @property 提供 celsius 属性，
#         再加 fahrenheit 只读属性（华氏度 = 摄氏度 * 9/5 + 32）。
#         给 celsius 加 setter，要求低于 -273.15 时报 ValueError。
#
# 练习 2：写一个 User 类，类属性 total 记录用户总数，在 __init__ 里累加；
#         再加 @classmethod get_total() 返回总数。创建 3 个用户后，
#         分别用 User.get_total() 和 u1.get_total() 打印，比较结果。
#
# 练习 3：写一个 StringUtils 类，用静态方法实现 is_palindrome(s)
#         判断回文串（"abcba" 是，"abc" 不是），全程不创建对象。
#
# 练习 4：先按错误示范写一个共享列表的购物车，亲眼看到两个对象串数据；
#         再把 self.items = [] 补进 __init__，确认问题消失。
#
# 【下一步】03_继承.py
# ==============================================================================