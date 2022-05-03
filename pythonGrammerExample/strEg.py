#coding:utf-8

#字符串声明
s1 = 'hello'
s2 = "hello"
s3 = """hello"""
print(s1 == s2 == s3)


#下标操作
name = 'jason'
print(name[0])
#'j'
print(name[1:3])
#'as'

#字符串拼接
#str1 += str2

#字符串trim
#string.strip(str)，表示去掉首尾的 str 字符串；
#string.lstrip(str)，表示只去掉开头的 str 字符串；
#string.rstrip(str)，表示只去掉尾部的 str 字符串。
s = ' my name is jason '
s.strip()
#'my name is jason'

id = 123
#字符串的格式化
print('no data available for person with id: {}, name: {}'.format(id, name))

