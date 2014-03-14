import os
import options
from writer import TemplateFabric

def get_serializer():
    form = options.getOptions()[0].out_format
    a = {"python" : PythonSerializer()}
    return a[form]


class PythonSerializer(object):
    def __init__(self):
        self.lib_imp="prophy."

    def serialize(self, dataHolder):
        out = ""
        
        out += self._serialize_include(dataHolder.include.get_list()) + os.linesep
        out += self._serialize_union(dataHolder.union_dict) + os.linesep
        out += self._serialize_constant(dataHolder.constant) + os.linesep
        out += self._serialize_typedef(dataHolder) + os.linesep
        out += self._serialize_enum(dataHolder.enum_dict) + os.linesep
        out += self._serialize_msgs(dataHolder.sort_struct())
        out += self._serialize_msgs(dataHolder.msgs_list)


        return out

    def _serialize_enum(self, enum_dic):
        def serialize_enum_members(list):
            desc = []
            for member in list:
                    k,v = member
                    desc.append("('{0}',{1})" .format(k , v))
            return ", ".join(desc)
        out = ""
        
        for key, val in enum_dic.iteritems():
            out += "class {0}({1}enum):" .format(key, self.lib_imp) + "\n"
            out += "    __metaclass__ = {0}enum_generator" .format(self.lib_imp) + "\n"
            out += "    _enumerators  = [" + serialize_enum_members(val.list) + "]\n"

        return out
    
#######################################################################
                        

#######################################################################
    
    def _serialize_typedef(self, dataHolder):
        typedef_list = dataHolder.typedef.get_list()
        struct_list = dataHolder.struct_list
        enum_dict = dataHolder.enum_dict
        list_used_structed = []
        list_used_enums = []
        out = ""
        for key, val in typedef_list:
            if val.startswith('u') or val.startswith('i') or val.startswith('r'):
                out += key + " = " + self.lib_imp + val + '\n'
            elif val.startswith('S'):
                if val not in list_used_structed:
                    out += self._get_struct_for_typedef(val,struct_list) + '\n'  
                list_used_structed.append(val)
                out += key + " = "  + val + '\n'
            elif val.startswith('E'):
                if val not in list_used_enums :
                    out += self._get_enum_for_typedef(val,enum_dict) + '\n'  
                list_used_enums .append(val)
                out += key + " = "  + val + '\n'
            else:
                out += key + " = "  + val + '\n'
        return out

    def _get_struct_for_typedef(self,val,struct_list):
        out = ""
        for i in xrange(len(struct_list)):
            if struct_list[i].name == val:
                x = struct_list.pop(i)
                return self._serialize_msgs([x])
        print struct_list[i].name,val
        return "1"

    def _get_enum_for_typedef(self,val2,enum_dict):
        out = ""
        for key,val in enum_dict.iteritems():
            if key == val2:
                enum_dict.pop(key,val)                
                return self._serialize_enum({key:val})
        return "1"
        
    def _serialize_include(self, include_list):
        out = "import {0} \n" .format(self.lib_imp[:-1])
        for inc in include_list:
            out += "from " + inc + " import *" + '\n'
        return out

    def _serialize_constant(self, constant):
        out = ""
        for key,val in constant.get_sorted_list():
            out += key + " = " + val + '\n'
        return out

    def _serialize_union(self, union_dict):
        def serialize_union_members(list):
            desc = []
            for member in list:
                    k,v = member
                    desc.append("('{0}',{1})" .format(k , v))
            return ", ".join(desc)
        out = ""
        
        for key, val in union_dict.iteritems():
            out += "class {0}({1}union):" .format(key, self.lib_imp) + "\n"
            out += "    __metaclass__ = {0}union_generator" .format(self.lib_imp) + "\n"
            out += "    _discriminator = EDisc{0}" .format(key) + "\n"
            out += "    _descriptor  = [" + serialize_union_members(val.list) + "]\n"

        return out

    def _serialize_msgs(self,msgs_list):
        out = ""

        def serialize_members(keys):
            desc = []
            for member in keys:
                if member.type.startswith('u') or member.type.startswith('i') or member.type.startswith('r')  :
                    lib_imp = self.lib_imp
                else :
                    lib_imp = ""
                if len(member.list) > 0:
                    desc.append(self._serialize_msg_member(member))
                else:
                    desc.append("('{0}',{1}{2})" .format(member.name ,lib_imp, member.type))
            return ", ".join(desc)
        for key in msgs_list:
            out += "class {0}({1}struct):" .format(key.name, self.lib_imp) + "\n"
            out += "    __metaclass__ = {0}struct_generator" .format(self.lib_imp) + "\n"
            out += "    _descriptor = [" + serialize_members(key.get_list()) + "]\n"
        return out

    def _serialize_msg_member(self, member):
        def format_simple_list(a, b):
            return  "('{0}',{1}), " .format(a, b)
        def format_array(a, b, c, d):
            return "('{0}',{1}array({2},bound='{3}'))" .format(a, b,c,d)
        def format_bytes_list(a,b,c):
            return  "('{0}',{1}bytes(size={2}))" .format(a,b,c)
        def format_variable_bytes_list(a,b,c,d):
            return  "('{0}',{1}bytes(size={2},bound='{3}'))" .format(a,b,c,d)

        str = ""
        variable_name_index = member.get_dimension_field_index('variableSizeFieldName')
        variable_type_index = member.get_dimension_field_index('variableSizeFieldType')
        size_index = member.get_dimension_field_index('size')
        is_variable_index = member.get_dimension_field_index('isVariableSize')

        if variable_name_index == -1:
            variable_name = "tmpName"
        else:
            variable_name = member.list[variable_name_index].dimension_field_value

        if variable_type_index == -1:
            variable_type = "TNumberOfItems"
        else:
            variable_type = member.list[variable_type_index].dimension_field_value

        if len(member.list) == 1 and size_index != -1:
            str += format_bytes_list(member.name, self.lib_imp,member.list[size_index].dimension_field_value )
        else:
            str += format_simple_list(variable_name,variable_type)
            str += format_array(member.name, self.lib_imp, member.type,variable_name)

        return str
