from utils.utils import ContentParser, output_to_txt
import json
import os

# 读取模板文件
template_filepath = r"template/bg.txt"
output_dir = r"output"
# 以utf-8编码读取文件,注意是否包含bom头
with open(template_filepath, 'r', encoding='utf-8') as f:
    content = f.read()
    # 检测是否包含bom头，如果有则去除
    if content.startswith('\ufeff'):
        content = content[1:]
parser = ContentParser(content)
result = parser.parse()
print(result)
import json
output_filepath = "test.json"
with open(output_filepath, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=4)
output_file = os.path.join(output_dir, "template.txt")
output_to_txt(output_file, result)

#根据模板生成dataframe列表
bg_temp = result['bg_temp']
#去除link_type_list
print(bg_temp)
import pandas as pd
#根据bg_temp的key生成dataframe,并以bg_temp的key为列名，以value为第一行值
columns = list(bg_temp.keys())
#添加名称列
columns.insert(0, '名称')
df = pd.DataFrame(columns=columns)
example = bg_temp
example['名称'] = 'example'
for key in example.keys():
    df.loc[0, key] = example[key]
#设置index为名称列
df.set_index('名称', inplace=True)

#从input\00_building_groups.txt读取并添加到df
input_filepath = r"input\00_building_groups.txt"

with open(input_filepath, 'r', encoding='utf-8') as f:
    content = f.read()
    # 检测是否包含bom头，如果有则去除
    if content.startswith('\ufeff'):
        content = content[1:]
parser = ContentParser(content)
result = parser.parse()

with open(output_filepath, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=4)
#单独取出result中的link_type_dict
link_type_dict = result['link_type_dict']
#去除link_type_dict
del result['link_type_dict']

#将result中的每个bg_temp添加到df中
for key in result.keys():
    bg_temp = result[key]
    bg_temp['名称'] = key
    #添加bg_temp到key为名称的行
    df.loc[key] = bg_temp
        

#输出df到df.csv
df.to_csv('df.csv', encoding='utf-8-sig')

