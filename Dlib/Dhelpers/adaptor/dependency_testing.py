import importlib, sys
from collections import defaultdict
from ..launcher import launch

class BackendDependencyError(Exception):
    
    def __init__(self, dependency_object, caused_by=None):
        self.dependency_obj = dependency_object
        self.caused_by = caused_by
    
    def handle(self):
        if isinstance(self.caused_by,ModuleNotFoundError):
            print(self.dependency_obj.install_tuple_dict)
            print(self.dependency_obj.install_instruction_dict)
        raise self
            
            
class DependencyManager:
    raise_errors = True
    dependency_folder = None
    instances = {}
    
    def __init__(self, module_name) -> None:
        if self.instances.get(module_name) is not None:
            raise KeyError("Duplicate. DependencyTester already defined for "
                           "module "+module_name)
        self.instances[module_name] = self
        self.module = module_name
        self.pydependencies = []
        self.shelldependencies = []
        self.systems = []
    
    def add_systems(self,*systems):
        self.systems += systems
    
    def pydependency(self, *args, **kwargs):
        dep = PythonDependency(*args, **kwargs)
        self.pydependencies.append(dep)
        dep.tester = self
        return dep
    
    def import_module(self, *args, **kwargs):
        dep = self.pydependency(*args, **kwargs)
        return dep.imprt()

    def shelldependency(self, *args, **kwargs):
        dep = ShellDependency(*args, **kwargs)
        self.shelldependencies.append(dep)
        dep.tester = self
        return dep
    
    def test_shellcommand(self, *args,**kwargs):
        dep = self.shelldependency(*args,**kwargs)
        return dep.test()




class Dependency:
    
    def __init__(self, name, install_tuple=None, install_instruction=None,
            system=""):
        self.name = name
        self.tester = None
        self.install_tuple_dict = defaultdict(list)
        self.install_instruction_dict = defaultdict(list)
        if install_tuple: self.install_tuple(*install_tuple, system=system)
        if install_instruction: self.install_instruction(install_instruction,
                system=system)
        
        
    def install_tuple(self,command,package,system=""):
        self.install_tuple_dict[system].append((command, package))
    
    def install_instruction(self, instr, system=""):
        self.install_instruction_dict[system].append(instr)
        
    def raise_BackendDependencyError(self, caused_by=None):
        re = self.tester.raise_errors
        if not re: return False
        if re is True and isinstance(caused_by, Exception): raise caused_by
        raise BackendDependencyError(self, caused_by)
        
class PythonDependency(Dependency):
    
    def __init__(self, module_name,install_tuple=None,
            install_instruction=None, system=""):
        super().__init__(module_name, install_tuple, install_instruction,
                system)
        self.module_name = module_name
        
    def imprt(self):
        if self.tester.dependency_folder:
            sys.path.insert(0, self.tester.dependency_folder)
            # this makes sure that packages
            # inside the dependency folder are  # found first. Unless the
            # module has already been imported.
        try:
            mod = importlib.import_module(self.module_name)
        except Exception as e:
            self.raise_BackendDependencyError(e)
            mod = NotImplemented
        if self.tester.dependency_folder: sys.path.pop(0)
        return mod
    
command_exists_cmd = "command -v "


class ShellDependency(Dependency):
    def __init__(self, cmd, test_cmd=None, expected_return=None,
            install_tuple=None, install_instruction=None, system=""):
        super().__init__(cmd,install_tuple, install_instruction, system)
        self.cmd = cmd
        self.test_cmd = test_cmd
        self.expected_return = expected_return
        
        
    def test(self):
        try:
            launch.get(command_exists_cmd + self.cmd)
        except launch.CalledProcessError:
            #return warn_or_error(
             #       "The following required bash command could not be found: "
              #      "'%s'"%first)
            return self.raise_BackendDependencyError()
        test = self.cmd if self.test_cmd is True else self.test_cmd
        if not test: return False
        try:
            out = launch.get(test)
        except launch.CalledProcessError as e:
            return self.raise_BackendDependencyError(e)
            #return warn_or_error(
             #       "The test bash command '{cmd}' returned non "
              #      "zero exit status.".format_map(locals()))
    
        if self.expected_return is not None and out != self.expected_return:
            return self.raise_BackendDependencyError()
            #return warn_or_error(
             #       "The test bash command '{cmd}'\n returned the value '{"
              #      "out}', "
               #     "\n but it should return '{expected_return}'.".format_map(
                #            locals()))
        return out