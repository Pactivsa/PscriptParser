from utils.folder import parser_folder
import os 
import json
import pandas
folder_path = 'input/buildings'

result, result_list = parser_folder(folder_path)

result_filepath = 'result.json'
result_list_filepath = 'result_list.json'
with open(result_filepath, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=4)
with open(result_list_filepath, 'w', encoding='utf-8') as f:
    json.dump(result_list, f, ensure_ascii=False, indent=4)

output_dir = 'output/buildings'

#遍历result_list
for i, result in enumerate(result_list):
    columns = {}
    bool_columns = {}
    #遍历result中的每一项
    for key in result:
        block = result[key]
        #取出block中的link_type_dict的每一个key，加入到columns中
        for link_type in block['link_type_dict']:
            #如果是'yes或者'no',则加入到bool_columns中
            if block[link_type] == 'yes' or block[link_type] == 'no':
                bool_columns[link_type] = block[link_type]
                continue
            columns[link_type] = []
            #检测block中link_type对应的value的类型
            if isinstance(block[link_type], list):
                columns[link_type] = '列表'
                continue
            elif isinstance(block[link_type], dict):
                columns[link_type] = '块属性'
                continue
            #数值
            elif isinstance(block[link_type], int) or isinstance(block[link_type], float):
                columns[link_type] = '数值'
                continue
            else:
                #如果是字符串，则加入到columns中
                columns[link_type] = '字符串'
    file_name = 'result_' + str(i) + '说明.txt'
    output_dir_path = os.path.join(output_dir, file_name)
    with open(output_dir_path, 'w', encoding='utf-8') as f:
        #写入columns
        f.write('普通列：\n')
        for key, value in columns.items():
            print(key, value)
            f.write(key + '：' + value + '\n')
        #写入bool_columns
        f.write('\n布尔列：\n')
        for key in bool_columns.keys():
            f.write(key + '\n')
    excel_name = 'result_' + str(i) + '.xlsx'
    columns_list = columns.keys()
    #添加 yes列和 no列
    columns_list = list(columns_list)
    columns_list.append('yes')
    columns_list.append('no')
    columns_list.append('ID')
    #创建DataFrame
    df = pandas.DataFrame(columns=columns_list)
    #设置ID为索引
    df.set_index('ID', inplace=True)
    #写入excel
    excel_path = os.path.join(output_dir, excel_name)
    df.to_excel(excel_path, index=True)
    
    
            
            
            
        

