##1. 变量的声明及定义  弱类型的语言
- python是弱类型语言
变量无须声明就可以直接赋值，对一个不存在的变量赋值就相当于定义了一个新变量。
变量的数据类型可以随时改变，比如，同一个变量可以一会儿被赋值为整数，一会儿被赋值为字符串。
python变量在赋值后，是有类型的，可以使用type(变量名) 查看变量类型

- 字符串
python中的字符串是不可变的，改变字符串内部的字符是错误的
变量的赋值，只是表示让变量指向了某个对象，并不表示拷贝对象给变量；
一个对象，可以被多个变量所指向；

- 可变对象
（列表，字典，集合等等）的改变，会影响所有指向该对象的变量。

- 不可变对象（字符串、整型、元组等等）
所有指向该对象的变量的值总是一样的，也不会改变。但是通过某些操作（+= 等等）更新不可变对象的值时，会返回一个新的对象。
变量可以被删除，但是对象无法被删除。

[python字符串代码示例](https://github.com/zzppp1990/python-example/blob/main/pythonGrammerExample/strEg.py)

##2. 条件分支判断及循环
###2.1 条件判断

>if condition_1:
    statement_1
elif condition_2:
    statement_2
...
elif condition_i:
    statement_i
else:
    statement_n

###2.2 循环
Python 中的数据结构只要是可迭代的（iterable），比如列表、集合等等，那么都可以通过下面这种方式遍历
for item in <iterable>:
    ...

[循环代码示例](https://github.com/zzppp1990/python-example/blob/main/pythonGrammerExample/loopForEg.py)

##3. 输入与输出
文件输入输出 example
[输入与输出示例代码](https://github.com/zzppp1990/python-example/tree/main/pythonGrammerExample/inputOutputEg)

##4. 函数
###4.1 自定义函数
函数的定义：
def name(param1, param2, ..., paramN):
    statements
    return/yield value # optional
def 是可执行语句，这意味着函数直到被调用前，都是不存在的。当程序调用函数时，def 语句才会创建一个新的函数对象，并赋予其名字
函数的参数可以设置默认值
注意：
1. 主程序调用函数时，必须保证这个函数此前已经定义过，不然就会报错
2. 如果我们在函数内部调用其他函数，函数间哪个声明在前、哪个在后就无所谓，因为 def 是可执行语句，函数在调用之前都不存在
3. Python 和其他语言相比的一大特点是，Python 是 dynamically typed 的，可以接受任何数据类型（整型，浮点，字符串等等）

函数的嵌套：
在函数里面可以定义函数
好处：
1. 函数的嵌套能够保证内部函数的隐私。内部函数只能被外部函数所调用和访问，不会暴露在全局作用域
2. 合理的使用函数嵌套，能够提高程序的运行效率

函数变量的作用域：
局部变量：变量是在函数内部定义的
全局变量：可以在文件内的任何地方被访问，如果我们一定要在函数内部改变全局变量的值，就必须加上 global 这个声明
nonlocal变量：对于嵌套函数来说，内部函数可以访问外部函数定义的变量，但是无法修改，若要修改，必须加上 nonlocal 这个关键字

函数闭包：
闭包其实和刚刚讲的嵌套函数类似，不同的是，这里外部函数返回的是一个函数，而不是一个具体的值。
返回的函数通常赋于一个变量，这个变量可以在后面被继续执行调用。

###4.2 匿名函数
匿名函数的关键字是 lambda，之后是一系列的参数，然后用冒号隔开，最后则是由这些参数组成的表达式
lambda argument1, argument2,... argumentN : expression
lambda 是一个表达式（expression），并不是一个语句（statement）

函数要点：
tips1: 如果你想通过一个函数来改变某个变量的值，通常有两种方法。一种是直接将可变数据类型（比如列表，字典，集合）当作参数传入，直接在其上修改；第二种则是创建一个新变量，来保存修改后的值，然后将其返回给原变量。在实际工作中，我们更倾向于使用后者，因为其表达清晰明了，不易出错！

##5. 类
类的声明： class nameTest():
类的属性：如果一个属性以 __ （注意，此处有两个 _） 开头，我们就默认这个属性是私有属性
构造函数　：def \_\_init\_\_():
成员函数：成员函数则是我们最正常的类的函数，它不需要任何装饰器声明，第一个参数 self 代表当前对象的引用，可以通过此函数，来实现想要的查询 / 修改类的属性等功能
静态成员函数则与类没有什么关联，最明显的特征便是，静态函数的第一个参数没有任何特殊性

继承：
声明：class Document(Entity):
必须在 init() 函数中显式调用父类的构造函数。它们的执行顺序是 子类的构造函数 -> 父类的构造函数。
##6. 库及模块化
同一个文件夹下函数或类的导入：
from your_file import function_name, class_name

项目中如何设置模块的路径：
Python 解释器在遇到 import 的时候，它会在一个特定的列表中寻找模块。这个特定的列表，可以用下面的方式拿到：

import sys  
print(sys.path)
输出如下：
['', '/usr/lib/python36.zip', '/usr/lib/python3.6', '/usr/lib/python3.6/lib-dynload', '/usr/local/lib/python3.6/dist-packages', '/usr/lib/python3/dist-packages']
在Python 的 Virtual Environment（虚拟运行环境）修改PYTHONHOME环境变量
export PYTHONPATH="/home/ubuntu/workspace/your_projects"

>import 在导入文件的时候，会自动把所有暴露在外面的代码全都执行一遍。
if __name__ == '__main__'的意思是：
当.py文件被直接运行时，if __name__ == '__main__'之下的代码块将被运行；
当.py文件以模块形式被导入时，if __name__ == '__main__'之下的代码块不被运行。


##7. 数据结构
###7.1 列表和元组
定义：都是一个可以放置任意数据类型的有序集合。
l = [1, 2, 'hello', 'world'] # 列表中同时含有int和string类型的元素
l
[1, 2, 'hello', 'world']

tup = ('jason', 22) # 元组中同时含有int和string类型的元素
tup
('jason', 22)

tip1:
列表是动态的，长度大小不固定，可以随意地增加、删减或者改变元素（mutable）。
元组是静态的，长度大小固定，无法增加删减或者改变（immutable）。
tip2:
Python 中的列表和元组都支持负数索引，-1 表示最后一个元素，-2 表示倒数第二个元素；并且列表和元组都支持切片操作。
tip3:
列表和元组都可以随意嵌套
tip4:
列表和元组都可以相互转换
tip5:
需熟练使用列表和元组的内置函数
tip6:
列表是动态的，长度可变，可以随意的增加、删减或改变元素。列表的存储空间略大于元组，性能略逊于元组。
元组是静态的，长度大小固定，不可以对元素进行增加、删减或者改变操作。元组相对于列表更加轻量级，性能稍优。
tip7:
二维数组存在浅拷贝问题，尽量使用一维数组进行赋值，再转二维



###7.2 字典和集合
定义：
字典是一系列由键（key）和值（value）配对组成的元素的集合，字典是有序的；
相对于列表和元组字典的性能更优；
集合和字典基本相同，唯一的区别，就是集合没有键和值的配对，是一系列无序的、唯一的元素组合。

##8. 装饰器

##9. 其他语法点
- python添加中文注释
在代码首行添加：
\#coding:gbk    
或#coding:utf-8
或##-\*- coding : gbk -\*-

- 运行Python脚本：
a). 使用命令python test.py，执行test.py脚本
b). 在test.py文件第一行加上#！/usr/bin/env python; 不加这句话，系统会自动默认使用shell解释器
chmod u+x test.py
 ./test.py
