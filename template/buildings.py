import json
from template.template import BaseTemplate
from utils.folder import parser_file
from utils.utils import output_to_txt

class Buildings_group(BaseTemplate):
    def __init__(self, name ,if_init=False):
        original_file = "template/original/buildings_groups.txt"
        super().__init__(name,original_file, if_init)

class Buildings(BaseTemplate):
    def __init__(self, name ,if_init=False):
        original_file = "template/original/buildings.txt"
        super().__init__(name,original_file, if_init)


class Pmg(BaseTemplate):
    def __init__(self,name , if_init=False,Bindings: Buildings=None):
        original_file = "template/original/production_method_groups.txt"
        super().__init__(name ,original_file, if_init)
        if Bindings:
            self.bind(Bindings)
    def bind(self, Building: Buildings):
        Building.insert(self.name, "production_methods",True)


class Pm(BaseTemplate):
    def __init__(self,name , if_init=False,Pmg: Pmg=None):
        original_file = "template/original/production_methods.txt"
        super().__init__(name ,original_file, if_init)
        if Pmg:
            self.bind(Pmg)
    def bind(self, Pmg: Pmg):
        Pmg.insert(self.name, "production_methods",True)

