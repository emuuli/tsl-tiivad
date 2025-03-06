import ast
import re


class ValidationType:
    ALL_OF_THESE = "ALL_OF_THESE"
    ANY_OF_THESE = "ANY_OF_THESE"
    ANY = "ANY"
    NONE_OF_THESE = "NONE_OF_THESE"
    MISSING_AT_LEAST_ONE_OF_THESE = "MISSING_AT_LEAST_ONE_OF_THESE"
    NONE = "NONE"

class ProgramSyntaxTreeAnalyzer:
    def __init__(self, program_name, class_name=None, function_name=None, isMain=False):

        self.imports_module_names, self.defines_function_names = set(), set()
        self.defines_class_names, self.defines_subclass_names = set(), set()
        self.calls_function_names, self.calls_class_function_names = set(), set()
        self.contains_keyword_names, self.defined_vars = set(), set()
        self.contains_loop_tv = self.contains_try_except_tv = self.contains_return_tv = False
        self.is_class_tv = self.is_function_tv = self.is_pure_tv = False
        self.parent_classes, self.sub_classes = set(), set()
        self.calls_class = set()
        self.main_program_statements = [] 
        self.program_name = program_name
        self.actual = None
        self.expected = None
        self.exception = None

        try:
            with open(program_name, encoding="utf-8") as f:
                tree = ast.parse(f.read())
                self.treeWhole = tree
                self.tree = tree
        except Exception as e:
                self.treeWhole = None
                self.tree = None
                self.exception = e
    	        
        if isMain:
             self.extract_main_program()
             for node in ast.walk(self.treeWhole):
                if isinstance(node, ast.ClassDef):
                    self.defines_class_names.add(node.name)
        else:
            for node_type, name in [(ast.ClassDef, class_name), (ast.FunctionDef, function_name)]:
                if self.tree is not None and name is not None:
                    self.tree = next((x for x in ast.walk(self.tree)
                                    if isinstance(x, node_type) and x.name == name), None)
            if self.tree is None:
                self.exception = "Not found"
                return

        self.is_class_tv = isinstance(self.tree, ast.ClassDef)
        self.is_function_tv = self.is_pure_tv = isinstance(self.tree, ast.FunctionDef)
        self.contains_keyword_names = set(match[1] if match[1] else match[2] for match in re.findall(r'(["\'])([^\1]+?)\1|(\w+)', ast.unparse(self.tree)))
        self.traverse_nodes(self.tree)

    def raised_exception(self) -> bool:
            return self.exception is not None
    
    def extract_main_program(self):
            if self.tree is not None:
                self.main_program_statements = [node for node in self.tree.body if not isinstance(node, (ast.FunctionDef, ast.ClassDef))]
                self.tree = ast.Module(body=self.main_program_statements, type_ignores=[])

    def traverse_nodes(self, x):
        node_type = type(x).__name__
        if node_type == 'Import':
            for y in x.names:
                self.imports_module_names |= set(y.name.split("."))
        elif node_type == 'ImportFrom':
            self.imports_module_names |= set(x.module.split("."))
        elif node_type == 'ClassDef':
            self.defines_class_names.add(x.name)
            for y in x.bases:
                self.defines_subclass_names.add((x.name, y.id))
        elif node_type == 'FunctionDef':
            self.defines_function_names.add(x.name)
        elif node_type in ['For', 'While', 'comprehension']:
            self.contains_loop_tv = True
        elif node_type in ['Try', 'ExceptHandler']:
            self.contains_try_except_tv = True
        elif node_type == 'Call':
            if isinstance(x.func, ast.Name):
                self.calls_function_names.add(x.func.id)
                self.defined_vars.add(x.func.id)
                if x.func.id in self.defines_class_names:
                    self.calls_class.add(x.func.id)
            elif isinstance(x.func, ast.Attribute):
                self.calls_function_names.add(x.func.attr)
                self.calls_class_function_names.add(x.func.attr)
                self.defined_vars.add(x.func.attr)
        elif node_type == 'arg':
            self.defined_vars.add(x.arg)
        elif node_type == 'Name':
            if isinstance(x.ctx, ast.Store):
                self.defined_vars.add(x.id)
            elif isinstance(x.ctx, ast.Load) and x.id not in self.defined_vars and \
                    x.id not in self.imports_module_names:
                self.is_pure_tv = False
        elif node_type == 'Return':
            self.contains_return_tv = True
        for y in ast.iter_child_nodes(x):
            self.traverse_nodes(y)

    def is_class(self) -> bool:
        return self.is_class_tv

    def is_function(self) -> bool:
        return self.is_function_tv

    def imports_module(self, name: str = None) -> bool:
        return len(self.imports_module_names) > 0 if name is None \
            else name in self.imports_module_names

    def defines_class(self, name: str = None) -> bool:
        return len(self.defines_class_names) > 0 if name is None \
            else name in self.defines_class_names

    def defines_function(self, name: str = None) -> bool:
        return len(self.defines_function_names) > 0 if name is None \
            else name in self.defines_function_names

    def contains_loop(self) -> bool:
        return self.contains_loop_tv

    def contains_try_except(self) -> bool:
        return self.contains_try_except_tv

    def contains_word(self, name: str = None) -> bool:
        return len(self.contains_keyword_names) > 0 if name is None \
            else name in self.contains_keyword_names

    def calls_function(self, name: str = None) -> bool:
        return len(self.calls_function_names) > 0 if name is None \
            else name in self.calls_function_names

    def calls_print(self) -> bool:
        return "print" in self.calls_function_names

    def creates_instance(self, name: str = None) -> bool:
        return len(self.calls_function_names & self.defines_class_names) > 0 if name is None \
            else name in self.calls_function_names & self.defines_class_names

    def calls_class_function(self, name: str = None) -> bool:
        return len(self.calls_class_function_names) > 0 if name is None \
            else name in self.calls_class_function_names

    def analyze_with_quantifier(self, target: str, quantifier: str, names: set = set(),
                                nothing_else: bool = False) -> bool:
        match target:
            case 'imports_module':
                targetset = self.imports_module_names
            case 'defines_function':
                targetset = self.defines_function_names
            case 'calls_function':
                targetset = self.calls_function_names 
            case 'contains_keyword':
                targetset = self.contains_keyword_names
            case 'defines_class':
                targetset = self.defines_class_names
            case 'calls_class':
                targetset = self.calls_class
            case 'is_subclass':
                targetset = self.parent_classes
            case 'is_parentclass':
                targetset = self.sub_classes
            case 'creates_instance':
                targetset = self.defines_class_names & self.calls_function_names
            case 'calls_class_function':
                targetset = self.calls_class_function_names
            case _:
                return False
        self.actual = targetset
        match quantifier:
            case ValidationType.ALL_OF_THESE:
                return names <= targetset and (not nothing_else or targetset <= names)
            case ValidationType.ANY_OF_THESE:
                return len(names & targetset) > 0 and (not nothing_else or targetset <= names)
            case ValidationType.ANY:
                return len(targetset) > 0
            case ValidationType.MISSING_AT_LEAST_ONE_OF_THESE:
                return not (names <= targetset)
            case ValidationType.NONE_OF_THESE:
                return len(names & targetset) == 0
            case ValidationType.NONE:
                return len(targetset) == 0
            case _:
                return False


class ClassSyntaxTreeAnalyzer(ProgramSyntaxTreeAnalyzer):
    def __init__(self, program_name, class_name):
        super().__init__(program_name, class_name)
        self.class_name = class_name
        if self.exception is not None:
            return
        self.calls_function_names = set()
        self.get_parentClasses(class_name)
        self.get_subClasses(class_name)

    def get_parentClasses(self,className):
        self.parent_classes = {parent for child, parent in self.defines_subclass_names if child == className}

    def get_subClasses(self, className):
        subclass_set = set() 
        def find_subclasses(target_class):
            for node in ast.walk(self.treeWhole):
                if isinstance(node, ast.ClassDef):  
                    for base in node.bases:
                        if hasattr(base, "id") and base.id == target_class:  
                            if node.name not in subclass_set:  
                                subclass_set.add(node.name)
                                find_subclasses(node.name)  
        find_subclasses(className)  
        self.sub_classes = subclass_set

class FunctionSyntaxTreeAnalyzer(ProgramSyntaxTreeAnalyzer):
    def __init__(self, program_name, function_name):
        self.function_name = function_name  
        super().__init__(program_name, None, function_name)
        if self.exception is not None:
            return
        self.global_vars = set() 
        self._analyze_global_variables() 

    def _analyze_global_variables(self):
        if self.tree is None:
            return

        global_scope_vars = set() 
        #leiame põhiprogrammi muutujate väärtustused
        for node in self.treeWhole.body: 
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name): 
                        global_scope_vars.add(target.id)

        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef) and node.name == self.function_name:
                function_scope_vars = set()
                for sub_node in ast.walk(node):
                    # Global märkega muutujad
                    if isinstance(sub_node, ast.Global):
                        self.global_vars.update(sub_node.names)
                    # Muutujate kasutus
                    if isinstance(sub_node, ast.Name) and isinstance(sub_node.ctx, ast.Load):
                        function_scope_vars.add(sub_node.id)
                self.global_vars.update(function_scope_vars & global_scope_vars)

    def is_pure(self) -> bool:
        return not self.global_vars
    
    def contains_return(self) -> bool:
        return self.contains_return_tv

    def is_recursive(self) -> bool:
        return self.is_function_tv and self.calls_function(self.tree.name)

    def prints_instead_of_returning(self) -> bool:
        return self.is_function_tv and self.calls_print() and not self.contains_return()

class MainProgramSyntaxTreeAnalyzer(ProgramSyntaxTreeAnalyzer):
    def __init__(self, program_name):
        super().__init__(program_name, None, None, True)

if __name__ == "__main__":
    ca = FunctionSyntaxTreeAnalyzer("../test/samples/func_is_pure.py", "kõige_sagedasem")
    print(ca.defined_vars, ca.imports_module_names)
    print(ca.is_pure())
