from lark import Transformer, v_args
from lark.tree import Tree
from pprint import pprint

class MediatorTransformer(Transformer):
    def start(self, items):
        start = []
        result = {"start":start}
        
        for item in items:
            if "typedef" in item:
                start.append(item)
            elif "automaton" in item:
                start.append(item)
            elif "system" in item:
                start.append(item)
        return result
    
    def typedef(self, items):
        # pprint(items[0])
        if "struct" in items[0]:
            struct_def, id = items
            return {"typedef": {"struct_def": struct_def, "ID": id}}
        elif "enum" in items[0]:
            enum_def, id = items
            return {"typedef": {"enum_def": enum_def, "ID": id}}

    def struct_def(self, items):
        return {"struct": [field for field in items if isinstance(field, dict)]}

    def enum_def(self, items):
        return {"enum": [id for id in items if isinstance(id, str)]}

    def field(self, items):
        id, type = items
        return {"field": {"ID": id, "type": type['ID']}}

    def automaton(self, items):
        template = items[0]
        id = items[1]
        ports = items[2]
        variables = items[3]
        transitions = items[4]
        return {"automaton": {"ID": id, "template": template, "ports": ports, "variables": variables, "transitions": transitions}}

    def template(self, items): 
        template_prams = [template_param for template_param in items if isinstance(template_param, dict)]
        return template_prams

    def template_param(self, items):
        id, type = items
        return {"template_param": {"ID": id, "type": type}}

    def ports(self, items):
        ports = [port for port in items if isinstance(port, dict)]
        return ports

    def port(self, items):
        id, direction, type = items
        return {"port": {"ID": id, "DIRECTION": direction, "type": type}}

    def variables(self, items):
        var_decls = [decl for decl in items if isinstance(decl, dict)]
        return {"variables": var_decls}

    def var_decl(self, items):
        id, type = items[:2]
        init_expr = items[2] if len(items) > 2 else None
        return {"var_decl": {"ID": id, "type": type, "init_expr": init_expr}}

    def transitions(self, items):
        transitions = [trans for trans in items if isinstance(trans, dict)]
        return {"transitions": transitions}

    def transition(self, items):
        if len(items) == 2:
            condition, action_block = items
            return {"transition": {"condition": condition, "actions": action_block}}
        elif len(items) == 1:
            group = items[0]
            return {"transition": {"group": group}}

    def group(self, items):
        transitions = [trans for trans in items if isinstance(trans, dict)]
        return {"group": transitions}

    def condition(self, items):
        return items[0]

    def action_block(self, items):
        # pprint(items)
        actions = [stmt for stmt in items if isinstance(stmt, dict)]
        return {"action_block": actions}

    def action_stmt(self, items):
        # pprint(items)
        return {"action_stmt": items[0]}
    
    def assign_stmt(self, items):
        lhs, expr = items
        return {"assign": {"lhs": lhs, "expr": expr}}

    def sync_stmt(self, items):
        ids = [id for id in items if isinstance(id, str)]
        return {"sync": ids}

    def perform_stmt(self, items):
        ids = [id for id in items if isinstance(id, str)]
        return {"perform": ids}

    def expr_stmt(self, items):
        return {"expr": items[0]}

    def system(self, items):
        id = items[0]
        components = items[1]
        connections = items[2]
        return {"system": {"ID": id, "components": components, "connections": connections}}

    def components(self, items):
        component_decls = [decl for decl in items if isinstance(decl, dict)]
        return component_decls

    def component_decl(self, items):
        ids, component_type = items
        return {"component_decl": {"names": ids, "component_type": component_type}}

    def component_type(self, items):
        id = items[0]
        template_args = items[1] if len(items) > 1 else None
        return {"component_type": {"ID": id, "template_args": template_args}}

    def template_args(self, items):
        args = [arg for arg in items if isinstance(arg, dict)]
        return args

    def connections(self, items):
        connections = [conn for conn in items if isinstance(conn, dict)]
        return {"connections": connections}

    def connection(self, items):
        if len(items) == 2:
            id1, id2 = items
            return {"connection": {"ID1": id1, "ID2": id2}}
        elif len(items) >= 3:
            id, template_args, *lhss = items
            return {"connection": {"ID": id, "template_args": template_args, "lhss": lhss}}

    def type(self, items):
        return {"ID": items[0]}
        
        # elif len(items) == 2 and isinstance(items[1], dict):
        #     return [items[1]]
        # elif len(items) == 2 and isinstance(items[1], str):
        #     return {"type": items[1]}
        # elif len(items) == 3 and items[1] == "init":
        #     return {"type": items[0], "init": items[2]}

    def composite_type(self, items):
        if len(items) == 2:
            return {"composite_type": {"name": items[0], "value": items[1]}}
        elif len(items) == 3 and items[1] == "init":
            return {"composite_type": {"name": items[0], "value": items[2]}}

    def map_type(self, items):
        key_type, value_type = items
        return {"map_type": {"key": key_type, "value": value_type}}

    # def array_type(self, items):
    #     type_name = items[0]
    #     size_expr = items[1] if len(items) > 1 else None
    #     return {"array_type": {"type": type_name, "size": size_expr}}

    def union_type(self, items):
        type1, type2 = items
        return {"union_type": {"type1": type1, "type2": type2}}

    def initialized_type(self, items):
        type_name, init_expr = items
        return {"initialized_type": {"type": type_name, "init": init_expr}}

    def struct_type(self, items):
        fields = [field for field in items if isinstance(field, dict)]
        return {"struct_type": {"fields": fields}}

    def enum_type(self, items):
        ids = [id for id in items if isinstance(id, str)]
        return {"enum_type": {"items": ids}}
    
    def primitive_type(self, items):
        type_name = items[0]
        range_expr = items[1] if len(items) > 1 else None
        return {"primitive_type": {"name": type_name, "range": range_expr}}

    def range(self, items):
        return {"range_lhs": items[0], "range_rhs": items[1]}


    def expr(self, items):
        if len(items) == 1:
            return {"expr": items[0]}
        elif len(items) == 2:
            return {"expr": {"op": items[0], "right": items[1]}}
        elif len(items) == 3:
            return {"expr": {"left": items[0], "op": items[1], "right": items[2]}}

    def compare_expr(self, items):
        if len(items) == 1:
            return {"compare_expr": items[0]}
        elif len(items) == 3:
            return {"compare_expr": {"left": items[0], "op": items[1], "right": items[2]}}

    def addi_expr(self, items):
        if len(items) == 1:
            return {"addi_expr": items[0]}
        elif len(items) == 3:
            return {"addi_expr": {"left": items[0], "op": items[1], "right": items[2]}}

    def multi_expr(self, items):
        if len(items) == 1:
            return {"multi_expr": items[0]}
        elif len(items) == 3:
            return {"multi_expr": {"left": items[0], "op": items[1], "right": items[2]}}

    def primary_expr(self, items):
        # pprint(items)
        if items[0].get("value"):
            return {"primary_expr": items}
        elif items[0].get("function_call"):
            return {"primary_expr": items}
        elif items[0].get("struct_literal"):
            return {"primary_expr": items}
        elif items[0].get("lhs"):
            return {"primary_expr": items}
        elif items[0].get("prec_expr"):
            return {"primary_expr": items}
        # elif len(items) == 2 and isinstance(items[1], dict):
        #     return {"primary_expr": {"name": items[0], "value": items[1]}}
        # elif len(items) == 2 and isinstance(items[1], str):
        #     return {"primary_expr": {"name": items[0], "field": items[1]}}
        # elif len(items) == 2 and isinstance(items[1], dict):
        #     return {"primary_expr": {"name": items[0], "index": items[1]}}
        # elif len(items) == 3:
        #     return {"primary_expr": {"name": items[0], "args": items[1]}}
        else:
            return {"primary_expr": items}

    def prec_expr(self, items):
        return {"prec_expr": items[0]}

    def struct_literal(self, items):
        field_type = items[0]
        # field_inits = [field for field in items if isinstance(field, dict)]
        field_inits = items[1:]  
        return {"struct_literal": {"field_type": field_type, "fields": field_inits}}

    def field_init(self, items):
        id, expr = items
        return {"field_init": { "name": id, "expr": expr}}

    def function_call(self, items):
        id = items[0]
        args = items[1] if len(items) > 1 else []
        return {"function_call": {"name": id, "args": args}}

    def value(self, items):
        # pprint(items)
        return {"value": items[0]}

    def lhs(self, items):
        if len(items) == 1:
            return {"lhs":{"ID": items[0]}}
        elif len(items) == 2:
            return {"lhs": {"name": items[0], "field": items[1]}}
        
    def field_type(self, items):
        return {"ID": items[0].value}

    def STRING(self, s):
        return s[1:-1]

    def ID(self, id):
        return id

    def NUMBER(self, num):
        return int(num)

    def WS(self, _):
        return None

    def COMMENT(self, _):
        return None
