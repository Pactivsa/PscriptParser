#P语言-Python解析器

一个用于将P脚本和Python进行双向转换的解析器。

## 用法
从[模板](template/template.py)中导入`P`类，然后创建一个`P`对象。
若设置初始化 if_init=True，则将从[原始文件](template/original/)下解析一个`P`脚本文件作为初始数据。
```python
buildings = Buildings("buildings_explosives_building_chemical_plants",if_init=True)

```
使用add方法添加一项数据
```python
buildings.add("unique", "=", "yes")
```
具体方法详见[模板](template/template.py)中的注释。
使用完成后可以使用`buildings.output(output_file)`方法将数据输出到指定文件中。
若有多个对象，可以构建列表，然后使用`compile_template(template_list,output_file)`方法将所有对象的数据合并输出到指定文件中。
