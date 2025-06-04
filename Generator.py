from Parser import parse
from Parser import tree_to_dict
from Parser import pre_parse
import json
from pprint import pprint

class Generator:
    def __init__(self, ast):
        self.ast = ast
        self.indent_level = 0

    def generate(self):
        return self._generate_start(self.ast)

    def _generate_start(self, start):
        code = []
        
        automaton_template = f"class AutomatonType {{\npublic:\nPortType(){{}}\n}};"
        for item in start['start']:
            if 'typedef' in item:
                code.append("\n// type_def")
                code.append(self._generate_typedef(item['typedef']))
            elif 'automaton' in item:
                code.append("\n// automaton_def")
                code.append(self._generate_automaton(item['automaton']))
            elif 'system' in item:
                code.append("\n// system_def")
                code.append(self._generate_system(item['system']))
        return '\n'.join(code)

    def _generate_typedef(self, typedef):
        if 'struct_def' in typedef:
            return self._generate_struct_def(typedef['struct_def'], typedef['ID'])
        elif 'enum_def' in typedef:
            return self._generate_enum_def(typedef['enum_def'], typedef['ID'])

    def _generate_struct_def(self, struct_def, name):
        fields = ' '.join(self._generate_field(field) for field in struct_def['struct'])
        fields_op_eq = ' && '.join(f"{field['field']['ID'].value} == other.{field['field']['ID'].value}" for field in struct_def['struct'])
        
        return f"\nstruct {name} {{\n\t{fields}\n\tbool operator==(const {name}& other) const {{\n\t\treturn {fields_op_eq};\n\t}};\n\tbool operator!=(const {name}& other) const {{\n\t\treturn !(*this == other);\n\t}};\n}};"
    
    """
    struct {name} {
        {fields}
        bool operator==(const {name}& other) const {
            return x == other.x && y == other.y;
    };
    """

    def _generate_enum_def(self, enum_def, name):
        items = ', '.join(enum_def['enum'])
        return f"\nenum {name} {{ {items} }};"

    def _generate_field(self, field):
        return f"{self._generate_type(field['field']['type'])} {field['field']['ID'].value}; "

    def _generate_type(self, type):
        if 'primitive_type' in type:
            return type['primitive_type']['name']
        elif 'enum_type' in type:
            return self._generate_enum_type(type)
        elif 'struct_type' in type:
            return type['struct_type']['fields'][0]['ID']
        elif 'composite_type' in type:
            return type['composite_type']['name']
        elif 'map_type' in type:
            return f"map<{self._generate_type(type['map_type']['key'])}, {self._generate_type(type['map_type']['value'])}>"
        elif 'union_type' in type:
            return f"{self._generate_type(type['union_type']['type1'])} | {self._generate_type(type['union_type']['type2'])}"
        elif 'initialized_type' in type:
            return f"{self._generate_type(type['initialized_type']['type'])} init {type['initialized_type']['init']}"
        elif 'lhs' in type:
            return self._generate_lhs(type)
        else:
            return type
        
    def _generate_enum_type(self, enum_type):
        enum_item = ','.join(item.value for item in enum_type['enum_type']['items'])
        return 'enum' + '{' + enum_item + '}'

    def _generate_automaton(self, automaton):
        name = automaton['ID']
        template_params = self._generate_template_params(automaton['template'], "template")
        params_def = self._generate_template_params(automaton['template'], "def")
        params_pass = self._generate_template_params(automaton['template'], "pass")
        ports = '\n'.join(self._generate_port(port) for port in automaton['ports'])
        variables = '\n'.join(self._generate_var_decl(var) for var in automaton['variables']['variables'])
        transitions = '\n'.join(self._generate_transition(trans) for trans in automaton['transitions']['transitions'])
        # print(template_params)
        # print(name)
        # print(ports)
        # print(variables)
        # print(transitions)
        # return f"automaton<{template_params}> {name}({ports}) {{\n{variables}\n{transitions}\n}}"
        # return f"\nclass {name} {{\npublic: {name}({template_params}) \n\n{ports}\n\n{variables}\nvoid transition();}}; \n\nvoid {name}::transition(){{\nwhile(true){{ \n{transitions}\n}} \n}}\n"
        # return f"class {name}{{ \n\tpublic: {name}{template_params} \n\n{ports}\n\n{variables}\n\tTransition transition; TransitionGroup group; TransitionMap map; \n\n{transitions}\n}};\n\n"
        return f"\nstruct {name}{{\n\t{params_def}\n\t{ports}\n\n\t{variables}\n\n\tTransition transition; TransitionGroup group; TransitionMap map;\n\n\t{name}({template_params}): {params_pass}\n\t{{\n\t\t{transitions}\n\t}}\n}};\n\n"


    
    """
    struct election_module{
        {params_def}
        {ports}

        {variables}
        Transition transition; TransitionGroup group; TransitionMap map;

        election_module(int id): id(id){
            {transitions}
        }
    };
    """

    def _generate_template_params(self, params, Separator):
        # return f"({', '.join(self._generate_template_param(param, "paren") for param in params)}): {', '.join(self._generate_template_param(param, "comma") for param in params)}"
        if Separator == "template":
            return f"{', '.join(self._generate_template_param(param, "paren") for param in params)}"
        elif Separator == "def":
            return f"{'; '.join(self._generate_template_param(param, 'paren') for param in params)}" + ";"
        elif Separator == "pass":
            return f"{', '.join(self._generate_template_param(param, 'comma') for param in params)}"

    def _generate_template_param(self, param, returnstr):
        if returnstr == "paren":
            return f"{self._generate_type(param['template_param']['type']['ID'])} {param['template_param']['ID']}"
        elif returnstr == "comma":
            return f" {param['template_param']['ID']}({param['template_param']['ID']})"
        else:
            # print("ERROR")
            pass
        # return f"{self._generate_type(param['template_param']['type']['ID'])} {param['template_param']['ID']}"

    def _generate_port(self, port):
        direction = port['port']['DIRECTION']
        type = self._generate_type(port['port']['type']['ID'].value)
        # return f"{port['port']['ID']} : {direction} {type}"
        return f"Port<{type}> {port['port']['ID']}(Direction::{direction});"
    
    """
    Port<voteMsg> left(Direction::in);
    Port<voteMsg> right(Direction::out);
    """

    def _generate_var_decl(self, var_decl):
        type = self._generate_type(var_decl['var_decl']['type']['ID'])
        init_expr = f" = {self._generate_expr(var_decl['var_decl']['init_expr']['expr'])}" if var_decl['var_decl']['init_expr']['expr'] else ""
        # pprint(var_decl['var_decl']['init_expr']['expr'])
        return f"{type} {var_decl['var_decl']['ID']}{init_expr};"

    def _generate_transition(self, transition):
        if 'condition' in transition['transition']:
            condition = self._generate_expr(transition['transition']['condition']['expr'])
            actions = self._generate_action_block(transition['transition']['actions'])
            # return f"if({condition}){{\n{actions}\ncontinue;}}"
            return f"\n\t// transition def\n\n\ttransition.statements.clear();\n\n\t// guard def\n\ttransition.guard = []() -> bool {{\n\t\treturn {condition};\n\t}};{actions}\n\tgroup.clear();\n\tgroup.push_back(transition);\n\tmap.push_back(group);\n\n"

        elif 'group' in transition['transition']:
            # return f"group {{\n{'\n'.join(self._generate_transition(t) for t in transition['transition']['group'])}\n}}"
            pass
        
        """
        // 此地有巨大问题，因为transition非常抽象，可以和group爆改千层饼，之前没注意到这个事情，只做了一层
        // 笑点解析：leader里面用到零次group，这就是我和独一无二的测试用例的羁绊啊！
        // 所以现在group美美pass了。烦。
        // 晚上修改成下面的样式
        // std::vector<std::variant<Transition, Group>> transitions;
        
        // transition def

        transition.clear();

        // guard def
        transition.guard = []() -> bool {
            return true;
        };

        // add statements
        transition.statements.push_back([]() {
            // Executing statement 1
        });

        transition1.statements.push_back([]() {
            // Executing statement 2
        });

        group.clear();
        group.push_back(transition);
        map.push_back(group);
        
        """

    def _generate_action_block(self, action_block):
        # pprint(action_block['action_block'])
        return "\n\ttransition.statements.push_back([]() {\n\t\t" + '\n\t});\n\ttransition.statements.push_back([]() {'.join(self._generate_action_stmt(stmt['action_stmt']) for stmt in action_block['action_block']) + "\n\t});"
    
    """
    // add statements
    transition.statements.push_back([]() {
        // Executing statement 1
    });

    transition.statements.push_back([]() {
        // Executing statement 2
    });
    """

    def _generate_action_stmt(self, stmt):
        if 'assign' in stmt:
            return self._generate_assign_stmt(stmt['assign'])
        elif 'sync' in stmt:
            return self._generate_sync_stmt(stmt['sync'])
        elif 'perform' in stmt:
            return self._generate_perform_stmt(stmt['perform'])
        elif 'expr' in stmt:
            return self._generate_expr_stmt(stmt['expr'])

    def _generate_assign_stmt(self, assign):
        lhs = self._generate_lhs(assign['lhs'])
        expr = self._generate_expr(assign['expr']['expr'])
        return f"{lhs} = {expr};"

    def _generate_sync_stmt(self, sync):
        return f"sync {', '.join(sync)};"

    def _generate_perform_stmt(self, perform):
        return f"perform {', '.join(perform)};"

    def _generate_expr_stmt(self, expr):
        return f"{self._generate_expr(expr)};"

    def _generate_lhs(self, lhs):
        if isinstance(lhs, dict) and 'field' in lhs['lhs']:
            return f"{self._generate_lhs(lhs['lhs']['name'])}.{lhs['lhs']['field'].value}"
        else:
            return f"{lhs['lhs']['ID'].value}"
        return lhs

    def _generate_expr(self, expr):
        if 'compare_expr' in expr:
            return self._generate_compare_expr(expr['compare_expr'])
        elif len(expr) == 2:
            return f"{expr['op'].value} {self._generate_compare_expr(expr['right']['compare_expr'])}"
        elif len(expr) == 3:
            if 'compare_expr' in expr['left']:
                left = self._generate_compare_expr(expr['left']['compare_expr'])
                op = expr['op'].value
                right = self._generate_expr(expr['right']['expr'])
            else:
                left = self._generate_expr(expr['left']['expr'])
                op = expr['op'].value
                right = self._generate_compare_expr(expr['right']['compare_expr'])
            return f"({left} {op} {right})"
        # if isinstance(expr, dict):
        #     if 'value' in expr:
        #         return str(expr['value'])
        #     elif 'struct_literal' in expr:
        #         return self._generate_struct_literal(expr['struct_literal'])
        #     elif 'function_call' in expr:
        #         return self._generate_function_call(expr['function_call'])
        #     elif 'primary_expr' in expr:
        #         return self._generate_primary_expr(expr['primary_expr'])
        #     elif 'logical_expr' in expr:
        #         return self._generate_logical_expr(expr['logical_expr'])
        #     elif 'compare_expr' in expr:
        #         return self._generate_compare_expr(expr['compare_expr'])
        #     elif 'additive_expr' in expr:
        #         return self._generate_additive_expr(expr['additive_expr'])
        #     elif 'multiplicative_expr' in expr:
        #         return self._generate_multiplicative_expr(expr['multiplicative_expr'])
        # pprint(expr)
        return f"{expr}ERROR-EXPR"
    
    
    # def _generate_logical_expr(self, logical_expr):
    #     left = self._generate_expr(logical_expr['left'])
    #     op = logical_expr['op'].value
    #     right = self._generate_expr(logical_expr['right'])
    #     return f"({left} {op} {right})"

    def _generate_struct_literal(self, struct_literal):
        fields = ', '.join(f"{field['field_init']['name']} : {self._generate_expr(field['field_init']['expr']['expr'])}" for field in struct_literal['fields'])
        return f"{{ {fields} }}"

    def _generate_function_call(self, function_call):
        args = ', '.join(self._generate_expr(arg) for arg in function_call['args'])
        return f"{function_call['name']}({args})"

# 202505070309 按照Transformer里primary_expr下属函数进行修改
    def _generate_primary_expr(self, primary_expr):
        try:
            if 'value' in primary_expr[0]:
                return f"{primary_expr[0]['value']}"
            elif 'function_call' in primary_expr[0]:
                return self._generate_function_call(primary_expr[0]['function_call'])
            elif 'struct_literal' in primary_expr[0]:
                return self._generate_struct_literal(primary_expr[0]['struct_literal'])
            elif 'lhs' in primary_expr[0]:
                return self._generate_lhs(primary_expr[0])
            elif 'prec_expr' in primary_expr[0]:
                return self._generate_prec_expr(primary_expr[0]['prec_expr'])
        except Exception as e:
            # pprint(primary_expr)
            return f"{primary_expr}ERROR-PRIM"
        # if 'name' in primary_expr[0]:
        #     if 'field' in primary_expr[0]:
        #         return f"{primary_expr[0]['name']}.{primary_expr[0]['field']}"
        #     elif 'index' in primary_expr[0]:
        #         return f"{primary_expr[0]['name']}[{primary_expr[0]['index']}]"
        #     elif 'args' in primary_expr[0]:
        #         args = ', '.join(self._generate_expr(arg) for arg in primary_expr[0]['args'])
        #         return f"{primary_expr[0]['name']}({args})"
        # return primary_expr[0]['name']
    
    def _generate_prec_expr(self, prec_expr):
        return "(" + self._generate_expr(prec_expr['expr']) + ")"

    def _generate_compare_expr(self, compare_expr):
        if 'addi_expr' in compare_expr:
            return self._generate_additive_expr(compare_expr['addi_expr'])
        else:
            if 'addi_expr' in compare_expr['left']:
                left = self._generate_additive_expr(compare_expr['left']['addi_expr'])
                op = compare_expr['op']
                right = self._generate_compare_expr(compare_expr['right']['compare_expr'])
            else:
                left = self._generate_compare_expr(compare_expr['left']['compare_expr'])
                op = compare_expr['op']
                right = self._generate_additive_expr(compare_expr['right']['addi_expr'])
            return f"({left} {op} {right})"
            

    def _generate_additive_expr(self, additive_expr):
        # pprint(additive_expr)
        if 'multi_expr' in additive_expr:
            return self._generate_multiplicative_expr(additive_expr['multi_expr'])
        else:
            if 'multi_expr' in additive_expr['left']:
                left = self._generate_multiplicative_expr(additive_expr['left'])
                op = additive_expr['op']
                right = self._generate_additive_expr(additive_expr['right'])
            else:
                left = self._generate_additive_expr(additive_expr['left'])
                op = additive_expr['op']
                right = self._generate_multiplicative_expr(additive_expr['right'])
            return f"({left} {op} {right})"

    def _generate_multiplicative_expr(self, multiplicative_expr):
        if 'primary_expr' in multiplicative_expr:
            return self._generate_primary_expr(multiplicative_expr['primary_expr'])
        else:
            if 'primary_expr' in multiplicative_expr['left']:
                left = self._generate_primary_expr(multiplicative_expr['left'])
                op = multiplicative_expr['op']
                right = self._generate_multiplicative_expr(multiplicative_expr['right'])
            else:
                left = self._generate_multiplicative_expr(multiplicative_expr['left'])
                op = multiplicative_expr['op']
                right = self._generate_primary_expr(multiplicative_expr['right'])
            return f"({left} {op} {right})"

    def _generate_system(self, system):
        name = system['ID']
        components = '\n'.join(self._generate_component_decl(comp) for comp in system['components'])
        connections = '\n'.join(self._generate_connection(conn) for conn in system['connections']['connections'])
        # return f"system {name} {{\n{components}\n{connections}\n}}"
        return f"int main(){{\n{components}\n\n{connections}\n}}"
    """
    int main(){
        election_module E1(1);
        election_module E2(2);
        election_module E3(3);
        worker C1(1);
        worker C2(2);
        worker C3(3);

        {connections}

        // MPI code

        return 0;
    }
    """

    def _generate_component_decl(self, component_decl):
        names = ''.join(component_decl['component_decl']['names'])
        ID = self._generate_component_type(component_decl['component_decl']['component_type'], "ID")
        args = self._generate_component_type(component_decl['component_decl']['component_type'], "args")
        # return f"{names} : {component_type};"
        return f"{ID} {names}({args});"

    def _generate_component_type(self, component_type, part):
        template_args = ', '.join(self._generate_primary_expr(arg["primary_expr"]) for arg in component_type['component_type']['template_args']) if component_type['component_type']['template_args'] else ""
        if part == "ID":
            return f"{component_type['component_type']['ID']}"
        elif part == "args":
            return f"{template_args}"

    def _generate_connection(self, connection):
        # if 'template_args' in connection:
        template_args = ', '.join(self._generate_primary_expr(arg['primary_expr']) for arg in connection['connection']['template_args'])
        lhss = ', '.join(self._generate_lhs(lhs) for lhs in connection['connection']['lhss'])
        return f"{connection['connection']['ID']}<{template_args}> ({lhss});"
        # else:
        #     return f"{connection['ID1']} -> {connection['ID2']};"
