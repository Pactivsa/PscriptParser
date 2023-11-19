import re
'''
    按pattern分割
    一般结构为 key = value
    或者 key ?= value
    value 可能为 {} 包含的结构，也可能为单个字符串，或者单纯的数字
'''
class Tokenizer:
    def __init__(self, content):
        self.content = content
        self.tokens = []
        self.current = 0
        self.current_line = 1
        # 定义正则表达式，要求只匹配从头开始的字符串
        self.patterns = [
            (r'^-?\d+\.\d+', 'NUMBER'),   # 匹配浮点数
            (r'^-?\d+', 'NUMBER'),        # 匹配整数
            (r'^"[^"]*"', 'STRING'),    # 匹配双引号字符串
            (r"^'[^']*'", 'STRING'),    # 匹配单引号字符串
            # 匹配“字符”+‘:’+“字符” 或 “字符”+‘/’+“字符”的标识符，如law_type:law_isolationism
            (r'^(\w+[:./])?\w+', 'IDENTIFIER'),
            (r'^#[^\n]*', 'COMMENT'),   #匹配开头为#的单行注释,直到换行符为止
            (r'^\n', 'NEWLINE'),        #匹配换行符
            (r'^\{', 'BLOCK_START'),
            (r'^\}', 'BLOCK_END'),
            (r'^(>=|<=|\?=|[<>]|=)', 'KEY_VALUE'),
            (r'^\s+', 'WHITESPACE'),    # 匹配空白字符,不包括换行符
        ]
    # 跳过开头的空白字符
    def skip_whitespace(self):
        match = re.match(r'^\s+', self.content[self.current:])
        if match:
            #检测有多少个换行符
            newline_count = match.group().count('\n')
            self.current += match.end()
            self.current_line += newline_count

    # 获取下一个token
    def get_next_token(self):
        if self.current >= len(self.content):
            return None

        for pattern, token_type in self.patterns:
            match = re.match(pattern, self.content[self.current:])
            if match:
                value = match.group()
                token = (value, token_type)
                self.tokens.append(token)
                self.current += len(value)
                return token

        raise ValueError('Illegal character at line %d，position %d, next character is %d,%s,nearest token is %s' % (
            self.current_line, self.current, ord(self.content[self.current]), self.content[self.current], self.tokens[-1]))
    
    # 获取所有的token
    def get_all_tokens(self):
        last_position = 0
        same_position_count = 0
        while self.current < len(self.content):
            self.skip_whitespace()
            #self.skip_newline()
            self.get_next_token()
            if self.current == last_position:
                same_position_count += 1
                if same_position_count > 3:
                    raise ValueError('Illegal character at line %d，position %d, next character is %d,%s,nearest token is %s' % (
                        self.current_line, self.current, ord(self.content[self.current]), self.content[self.current], self.tokens[-1]))
            last_position = self.current
            #输出进度
            #print('current progress: %d/%d' % (self.current, len(self.content)))


        return self.tokens

class ContentParser():
    def __init__(self, content):
        self.content = content  
        self.max_depth = 10
        self.tokenizer = Tokenizer(content)
        self.tokens = self.tokenizer.get_all_tokens()
        #将COMMENT类型的token过滤,并将NUMBER类型的token转换为float类型
        self.tokens = [(float(token[0]), token[1]) if token[1] == 'NUMBER' else token for token in self.tokens if token[1] != 'COMMENT']
        # for i, token in enumerate(self.tokens):
        #     print('token %d: %s' % (i, token))
        #当前指针指向第一个token
        self.current = 0
    
    #查看下一个token
    def peek(self):
        return self.tokens[self.current+1]
    #查看当前token
    def current_token(self):
        return self.tokens[self.current]
    #获取下一个token
    def next_token(self):
        self.current += 1
        #如果当前指针超过tokens的长度，则返回None
        if self.current >= len(self.tokens):
            return None
        return self.tokens[self.current]
    #输出所有token，一行一个
    def print_tokens(self):
        for i, token in enumerate(self.tokens):
            print('token %d: %s' % (i, token))
    #解析value
    def parse_value(self):
        '''
            解析 = 后面的value
            value可能为['NUMBER', 'STRING', 'IDENTIFIER']中的一种
            也有可能是block
            假设当前token为key_value
        '''
        #检测当前token是否为key_value，如果不是，抛出异常
        token = self.current_token()
        if token[1] != 'KEY_VALUE':
            raise ValueError('Value parser start error at token %d,Currrent token is %s' % (self.current, token))
        #移动指针到下一个token
        token = self.next_token()
        #如果当前token是block_start，解析block
        if token[1] == 'BLOCK_START':
            return self.parse_block()
        #如果当前token是[NUMBER, STRING, IDENTIFIER]中的一种，返回对应的值,并移动指针到下一个token
        elif token[1] in ['NUMBER', 'STRING', 'IDENTIFIER']:
            self.next_token()
            return token[0]
        #如果当前token不是[NUMBER, STRING, IDENTIFIER]中的一种，抛出异常
        else:
            
            raise ValueError('Value parser value error at token %d,Currrent token is %s' % (self.current, token))

    #添加到结果中，如果有重复的key，则添加后缀
    def add_to_result(self, key, value ,result ,link_type):
        '''
            @param key: 键值
            @param value: 值
            @param result: 待添加的块
            @param link_type: 连接类型,分为“=”和“?=”,"<",">","<=",">="
        '''
        #添加后缀的格式为 key__1__,key__2__...
        if key in result:
            i = 1
            while True:
                new_key = '%s__%d__' % (key, i)
                if new_key not in result:
                    result[new_key] = value
                    break
                i += 1
        else:
            result[key] = value
        
        #添加key的连接类型到link_type_dict中
        result['link_type_dict'][key] = link_type
        return result


    #解析block
    def parse_block(self,depth=0):
        '''
            block结构为
            {
                key = value
                key = block
                ...
            }
            假设当前token为block_start
        '''
        #检测深度是否超过最大深度
        if depth > self.max_depth:
            raise ValueError('Block parser depth error at token %d,Currrent token is %s' % (self.current, token))

        #获取当前指针指向的token
        token = self.current_token()
        #如果当前token不是block_start，抛出异常
        if token[1] != 'BLOCK_START':
            raise ValueError('Illegal character at token %d,Currrent token is %s' % (self.current, token))
        #跳过block_start
        self.next_token()
        #获取下一个token
        token = self.current_token()
        #探测下一个token是否为KEY_VALUE，如果不是KEY_VALUE，则为list，否则为dict
        next_token = self.peek()
        #如果下一个token是KEY_VALUE，则为dict
        if next_token[1] == 'KEY_VALUE':
            result = {}
            #添加link_type_dict
            result['link_type_dict'] = {}            
            #如果当前token不是block_end，继续解析
            while token[1] != 'BLOCK_END':
                #如果当前token是identifier，获取key
                if token[1] == 'IDENTIFIER':
                    key = token[0]
                    #获取下一个token
                    token = self.next_token()
                    #如果当前token是key_value，获取value
                    if token[1] == 'KEY_VALUE':
                        #获取连接类型
                        link_type = token[0]
                        #解析value
                        value = self.parse_value()
                        #将key和value添加到结果中
                        result = self.add_to_result(key, value, result,link_type)
                    else:
                        #self.print_tokens()
                        raise ValueError('KEY_VALUE error at token %d,Currrent token is %s ,last token is %s' % (self.current, token,self.tokens[self.current-1]))
                    
                else:
                    raise ValueError('IDENTIFIER error at token %d,Currrent token is %s ,last token is %s' % (self.current, token,self.tokens[self.current-1]))
                #获取下一个token
                token = self.current_token()

            #检测当前token是否为block_end，如果不是，抛出异常
            token = self.current_token()
            if token[1] != 'BLOCK_END':
                raise ValueError('Illegal character at token %d,Currrent token is %s ,last token is %s' % (self.current, token,self.tokens[self.current-1]))
            #跳过block_end
            self.next_token()
            #返回结果
            return result
        #如果下一个token不是KEY_VALUE，则为list
        else:
            result = []
                #如果当前token不是block_end，继续解析
            while token[1] != 'BLOCK_END':
                #如果当前token是identifier，获取key
                if token[1] in ['NUMBER', 'STRING', 'IDENTIFIER']:
                    key = token[0]
                    #添加到结果中
                    result.append(key)
                    #获取下一个token
                    token = self.next_token()
                else:
                    raise ValueError('IDENTIFIER error at token %d,Currrent token is %s ,last token is %s' % (self.current, token,self.tokens[self.current-1]))
                #获取下一个token
                token = self.current_token()

            #检测当前token是否为block_end，如果不是，抛出异常
            token = self.current_token()
            if token[1] != 'BLOCK_END':
                raise ValueError('Illegal character at token %d,Currrent token is %s ,last token is %s' % (self.current, token,self.tokens[self.current-1]))
            #跳过block_end
            self.next_token()
            #返回结果
            return result

    #根据已经分词的结果，进行语法分析
    def parse(self):
        '''
            分词主函数
            结构可能为以下几种
            1. IDENTIFIER = NUMBER
            2. IDENTIFIER = STRING
            3. IDENTIFIER = BLOCK
            其中 = 为 KEY_VALUE
            COMMENT需要跳过
        '''
        #在tokens前后添加BLOCK_START和BLOCK_END，然后作为一个block进行解析
        self.tokens.insert(0, ('{', 'BLOCK_START'))
        self.tokens.append(('}', 'BLOCK_END'))
        # for i, token in enumerate(self.tokens):
        #     print('token %d: %s' % (i, token))
        #解析block
        result = self.parse_block()

        #返回结果
        return result

#输出一个block到txt文件中
def output_block_to_txt(block,f,depth=0):
    '''
        将block输出到txt文件中其中key和value之间用link_type连接
    '''
    # 若block为dict,按以下格式输出
    if isinstance(block, dict):
    #获取link_type_dict
        link_type_dict = block['link_type_dict']
        #删除link_type_dict
        del block['link_type_dict']
        #遍历block
        for key, value in block.items():
            #检测key是否有__i__后缀，如果有，去掉后缀
            match = re.match(r'(.*)__\d+__', key)
            if match:
                key = match.group(1)


            #检测link_type_dict中是否有key，如果没有，则link_type为=
            if key not in link_type_dict:
                link_type = '='
            else:
                #获取link_type
                link_type = link_type_dict[key]

            #如果value是block，递归调用
            if isinstance(value, dict) or isinstance(value, list):
                #输出tab，depth个
                f.write('\t' * depth)
                #输出key，空格，link，空格，{，换行
                f.write("{} {} {{\n".format(key,link_type))
                #递归调用
                output_block_to_txt(value,f,depth+1)
                #输出tab，depth个
                f.write('\t' * depth)
                #输出}，换行
                f.write('}\n')
            else:
                #输出tab，depth个
                f.write('\t' * depth)
                #输出key，空格，link，空格，value，换行
                f.write("{} {} {}\n".format(key,link_type,value))
    # 若block为list,按以下格式输出
    elif isinstance(block, list):
        #遍历block
        for item in block:
            #输出tab，depth个
            f.write('\t' * depth)
            #输出item，换行
            f.write("{}\n".format(item))

#将结果按照一定格式输出到txt文件中
def output_to_txt(output_path,dict):
    #以utf-8编码打开文件
    with open(output_path, 'w', encoding='utf-8') as f:
        #添加BOM头
        f.write('\ufeff')
        #递归输出block
        output_block_to_txt(dict,f)


# #测试用主函数
# if __name__ == '__main__':
#     #测试分词
#     test_filepath = r"pop_needs\elgar_pop_needs.txt"
#     #以utf-8编码读取文件,注意是否包含bom头
#     with open(test_filepath, 'r', encoding='utf-8') as f:
#         content = f.read()
#         #检测是否包含bom头，如果有则去除
#         if content.startswith('\ufeff'):
#             content = content[1:]
#     parser = ContentParser(content)
#     result = parser.parse()
#     #print(result)
#     import json
#     output_filepath = "test.json"
#     with open(output_filepath, 'w', encoding='utf-8') as f:
#         json.dump(result, f, ensure_ascii=False, indent=4)
#     output_txt_filepath = "test.txt"
#     output_to_txt(output_txt_filepath,result)
#     #测试分词结果