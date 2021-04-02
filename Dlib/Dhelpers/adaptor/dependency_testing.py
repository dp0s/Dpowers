#
#
# Copyright (c) 2020-2021 DPS, dps@my.mail.de
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#
import importlib, sys, warnings
from collections import defaultdict
from ..launcher import launch


class ReturnFromModule(Exception):
    #the whole prupose of this class is to be able to return from a module
    # without executing it completely. Must be caught by parent module as is
    # done in the get_module_dependencies function below.
    def __init__(self, manager_inst=None):
        self.manager_inst = manager_inst
        

def import_adapt_module(mod_full_name, dependency_folder=None):
    if dependency_folder:
        sys.path.insert(0, dependency_folder)
        # this makes sure that packages inside the dependency folder are
        # found first. Unless the module has already been imported.
    save = DependencyManager.raise_errors
    DependencyManager.raise_errors = BackendDependencyError
    try:
        mod = importlib.import_module(mod_full_name)
    except BackendDependencyError as e:
        e.handle()
        raise
    finally:
        DependencyManager.raise_errors = save
        if dependency_folder: sys.path.pop(0)
    try:
        manager_inst = DependencyManager.instances[mod_full_name]
    except KeyError:
        warnings.warn(f"Module {mod_full_name} did not define "
                      f"DependencyManager instance.")
        manager_inst = None
    return mod, manager_inst


def get_module_dependencies(mod_full_name,perform_check=False,**kwargs):
    try:
        return DependencyManager.instances[mod_full_name]
    except KeyError:
        pass
    DependencyManager.exit_module = True
    DependencyManager.check_dependency  = perform_check
    try:
        mod, manager_inst = import_adapt_module(mod_full_name,**kwargs)
    except ReturnFromModule as e:
        #this should happen if DependencyManager was used
        manager_inst = e.manager_inst
    else:
        # this normally happens if DependencyManager was not defined
        # otherwise the following warning will be triggered:
        if manager_inst is not None:
            warnings.warn(f"Failed to return from {mod_full_name} "
                   f"although DependencyManager instance was defined. Please "
                   f"use DependencyManager.exit() method.")
    finally:
        DependencyManager.exit_module = False
        DependencyManager.check_dependency = True
    return manager_inst
    
    



class BackendDependencyError(Exception):
    
    def __init__(self, dependency_object, caused_by=None):
        self.dependency_obj = dependency_object
        self.caused_by = caused_by
        self.manager_inst = dependency_object.manager
    
    def handle(self):
        #if isinstance(self.caused_by,ModuleNotFoundError):
        #    print(self.dependency_obj.install_instructions[""])
        raise self from self.caused_by
    
    def __str__(self) -> str:
        text = f"{self.dependency_obj}\nCaused by " + \
               f"{type(self.caused_by).__name__}: {self.caused_by}"
        if isinstance(self.caused_by, ModuleNotFoundError):
            text += "\nTry the following solution:\n" + \
                    str(self.dependency_obj.install_instructions[''])
        return text


class DependencyManager:
    raise_errors = True  #this is set in Dependency class inside method raise_
    exit_module = False
    check_dependency = True
    instances = {}
    
    def __init__(self, module_name) -> None:
        if self.instances.get(module_name) is not None:
            raise KeyError("Duplicate. DependencyTester already defined for "
                           "module "+module_name)
        if not self.exit_module:
            self.instances[module_name] = self
        self.module = module_name
        self.pydependencies = []
        self.shelldependencies = []
        self.systems = []
        self.errors = []
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None: self.exit()

    def exit(self):
        if self.exit_module: raise ReturnFromModule(self)
    
    def pydependency(self, *args, **kwargs):
        dep = PythonDependency(*args, **kwargs)
        self.pydependencies.append(dep)
        dep.manager = self
        return dep
    
    def import_module(self, *args, **kwargs):
        dep = self.pydependency(*args, **kwargs)
        return dep.imprt()

    def shelldependency(self, *args, **kwargs):
        dep = ShellDependency(*args, **kwargs)
        self.shelldependencies.append(dep)
        dep.manager = self
        return dep
    
    def test_shellcommand(self, *args,**kwargs):
        dep = self.shelldependency(*args,**kwargs)
        return dep.test()
    
    @property
    def dependencies(self):
        return self.pydependencies + self.shelldependencies
    
    def raise_error(self, dependency_inst):
        self.errors.append(dependency_inst)
        dependency_error = dependency_inst.error
        caused_by = dependency_error.caused_by
        try:
            self.instances.pop(self.module)
        except KeyError:
            pass
        if self.raise_errors is False: return False
        if self.raise_errors is True and isinstance(caused_by, Exception):
            raise caused_by
        if self.exit_module: return "exit"
        raise dependency_error



class Dependency:
    
    default_install_tool = None
    
    def __init__(self, name, pkg=None, instruction=None,install_tool=None, system=""):
        self.name = name
        self.manager = None
        self.error = None
        self.install_instructions = defaultdict(InstallInstruction)
            #map {system: InstallInstruction instance}
        if instruction:
            self.add_instruction(instruction, system=system)
        if pkg:
            self.add_pkg(pkg, install_tool=install_tool, system=system)
        
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} '{self.name}' from " \
                    f"{self.manager.module}>"

    @property
    def perform_check(self):
        return self.manager.check_dependency
    
    def add_pkg(self,*pkgs,install_tool=None,system=""):
        if not install_tool: install_tool = self.default_install_tool
        self.install_instructions[system].add_names(install_tool,*pkgs)
    
    def add_instruction(self, instr, system=""):
        self.install_instructions[system].specific_instruction = instr
        
    def raise_BackendDependencyError(self, caused_by=None):
        self.error = BackendDependencyError(self,caused_by)
        return self.manager.raise_error(self)
    
        
class PythonDependency(Dependency):
    
    default_install_tool = "pip"
    
    def __init__(self, module_name,*args,**kwargs):
        super().__init__(module_name, *args,**kwargs)
        self.module_name = module_name
        
    def imprt(self):
        if not self.perform_check: return
        try:
            mod = importlib.import_module(self.module_name)
        except Exception as e:
            self.raise_BackendDependencyError(e)
            mod = NotImplemented
        return mod
    
    
    
command_exists_cmd = "command -v "


class ShellDependency(Dependency):
    
    default_install_tool = "apt"
    
    def __init__(self, cmd, test_cmd=None, expected_return=None,*args,
            **kwargs):
        super().__init__(cmd,*args,**kwargs)
        self.cmd = cmd
        self.test_cmd = test_cmd
        self.expected_return = expected_return
        
        
    def test(self):
        if not self.perform_check: return
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
    
    
    
    
install_commands = {"pip" : "pip install", "apt": "apt install"}


class InstallInstruction:
    
    def __str__(self):
        ret = ""
        for tool, pkgs in self.packages.items():
            if not pkgs: continue
            ret += install_commands[tool]
            for pkg in pkgs:
                ret += " " + pkg
            ret += "\n"
        for instruction in self.instructions:
            ret += "\n " + instruction
        return ret
    
    def command_list(self):
        commands = []
        for tool, pkgs in self.packages.items():
            if not pkgs: continue
            command = install_commands[tool]
            for pkg in pkgs: command += " " + pkg
            commands.append(command)
        return commands
        
    
    def __init__(self):
        self.packages = defaultdict(set)
        self.instructions = []
    
    def add_names(self, tool, *names):
        self.packages[tool] |= set(names)
        
    def update(self, other):
        if not isinstance(other,self.__class__):
            raise ValueError
        for tool, pkgs in other.packages.items():
            self.add_names(tool, *pkgs)
        for instruction in other.instructions:
            if instruction in self.instructions: pass
            self.instructions.append(instruction)
            
    def __bool__(self):
        return bool(self.packages)