#coding:utf-8

d = {'name': 'jason', 'dob': '2000-01-01', 'gender': 'male'}

# 遍历字典的键
print("----keys:")
for k in d:
    print(k)
#name
#dob
#gender

# 遍历字典的值
print("----values:")
for v in d.values():
    print(v)
#jason
#2000-01-01
#male

# 遍历字典的键值对
print("----key:value:")
for k, v in d.items():
    print('key: {}, value: {}'.format(k, v))
#key: name, value: jason
#key: dob, value: 2000-01-01
#key: gender, value: male



