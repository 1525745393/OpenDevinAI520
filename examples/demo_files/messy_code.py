# 这是一个格式混乱的Python文件，用于演示代码格式化工具

import os,sys
import json
from typing import Dict,List

def hello_world():
    print("Hello, World!")

class   MyClass:
    def __init__(self,name:str,age:int):
        self.name=name
        self.age=age
    
    def get_info(self)->Dict[str,str]:
        return {"name":self.name,"age":str(self.age)}

def process_data(data:List[Dict]):
    result=[]
    for item in data:
        if item.get("active")==True:
            result.append(item)
    return result

if __name__=="__main__":
    obj=MyClass("Alice",25)
    print(obj.get_info())
    
    data=[
        {"name":"John","active":True},
        {"name":"Jane","active":False},
        {"name":"Bob","active":True}
    ]
    
    active_users=process_data(data)
    print(f"Active users: {len(active_users)}")