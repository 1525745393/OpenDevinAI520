# 这是一个示例Python文件，用于测试代码格式化工具

import os,sys
import json
from pathlib import Path

def hello_world( ):
    print("Hello, World!")
    return "success"

class ExampleClass:
    def __init__(self,name,age):
        self.name=name
        self.age = age
    
    def get_info(self):
        return f"Name: {self.name}, Age: {self.age}"
    
    def update_age(self,new_age):
        if new_age>0:
            self.age=new_age
            return True
        else:
            return False

def process_data(data_list):
    result=[]
    for item in data_list:
        if isinstance(item,dict):
            processed_item={
                'id':item.get('id'),
                'name':item.get('name','Unknown'),
                'processed':True
            }
            result.append(processed_item)
    return result

if __name__=="__main__":
    # 创建示例对象
    person=ExampleClass("张三",25)
    print(person.get_info())
    
    # 处理数据
    sample_data=[
        {'id':1,'name':'Alice'},
        {'id':2,'name':'Bob'},
        {'id':3}
    ]
    
    processed=process_data(sample_data)
    print(json.dumps(processed,indent=2,ensure_ascii=False))