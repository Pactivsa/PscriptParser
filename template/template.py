#用于添加与控制的模板类
from utils.folder import parser_file
from utils.utils import output_to_txt

EQ = "="
NE = "!="
IFE = "?="
LT = "<"
GT = ">"
LE = "<="
GE = ">="

class BaseTemplate:

    def __init__(self, name ,original_file,if_init=False):
        self.original_file = original_file
        self.name = name
        self.data = {
            "link_type_dict": {
                name: EQ
            },
            name: {
                "link_type_dict": {
                },
            }
        }
        if if_init:
            self.init_from_file()


    
    
    def add(self, key, link_type, value):
        '''
            添加一项数据，如要添加一项后原数据为
            building = {
               texture = "path/to/texture"
               	production_method_groups = {
		            pmg_explosives_building_chemical_plants
		            pmg_ownership_capital_building_explosives_factory
	            }
            }
            则调用
            obj.add("texture", "=", '"path/to/texture"')
            obj.add("production_method_groups", "=", [
                "pmg_explosives_building_chemical_plants",
                "pmg_ownership_capital_building_explosives_factory"
            ])
            或
            add("texture", EQ , '"path/to/texture"')
            add("production_method_groups", EQ, [
                "pmg_explosives_building_chemical_plants",
                "pmg_ownership_capital_building_explosives_factory"
            ])

        '''
        self.data[self.name][key] = value
        self.data[self.name]["link_type_dict"][key] = link_type
        return self

    def add(self, key, link_type, value, root_path, if_recursive=False):
        '''
            在指定层级添加一项数据，如要添加一项后原数据为
            building = {
                texture = "path/to/texture"
                unlocking_technologies = {
		            intensive_agriculture
	            }
                possible = {
                        error_check = {
                            severity = fail
                        }
                }
            }
            则调用
            obj.add("possible", "=", {})
            obj.add("error_check", "=", {},"possible")
            obj.add("severity", "=", "fail","possible.error_check")
            或
            obj.add("severity", "=", "fail","possible.error_check",if_recursive=True)

        '''
        if root_path == "":
            self.add(key, link_type, value)
            return self
        root_path_list = root_path.split(".")
        #根据root_path_list，找到对应的层级
        current_data = self.data[self.name]
        trace = ""
        for path in root_path_list:
            trace = trace + path + "."
            #如果当前层级不存在，则创建
            if path not in current_data.keys():
                if if_recursive:
                    current_data[path] = {
                        "link_type_dict": {
                        }
                    }
                    current_data["link_type_dict"][path] = EQ
                else:
                    raise Exception("当前层级不存在"+trace)
            #进入下一层级
            current_data = current_data[path]
        #添加数据
        #如果当前层级为列表，则添加到列表中
        if isinstance(current_data, list):
            current_data.append(value)
            return self
        #如果当前层级为字典，则添加到字典中
        if isinstance(current_data, dict):
            current_data[key] = value
            current_data["link_type_dict"][key] = link_type
            return self
        
    def insert(self,value,root_path,if_recursive=False):
        '''
            插入一项数据，如要插入一项后原数据为
            building = {
                texture = "path/to/texture"
                unlocking_technologies = {
		            intensive_agriculture
                    manufacturies
	            }
                possible = {
                        error_check = {
                            severity = fail
                        }
                }
            }
            则调用
            obj.insert("manufacturies","unlocking_technologies")
        '''
        self.add("", "=", value, root_path, if_recursive)
    
    
    def init_from_file(self):
        result = parser_file(self.original_file)
        #获取result中非link_type_dict的第一个key
        key = ""
        for k in result.keys():
            if k != "link_type_dict":
                key = k
                break
        self.data[self.name] = result[key]


    def output(self, output_file):
        output_to_txt(output_path=output_file, dict=self.data)

    @staticmethod
    def merge_template(template_list):
        '''
            合并模板
        '''
        result = {
            "link_type_dict": {
            }
        }
        for template in template_list:
            result["link_type_dict"][template.name] = template.data["link_type_dict"][template.name]
            result[template.name] = template.data[template.name]
        return result
    
    @staticmethod
    def compile_template(template_list,output_file):
        '''
            编译模板,将多个模板合并为一个模板后输出
        '''
        result = BaseTemplate.merge_template(template_list)
        output_to_txt(output_path=output_file, dict=result)


