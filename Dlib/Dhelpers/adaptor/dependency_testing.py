#
#
# Copyright (c) 2020-2024 DPS, dps@my.mail.de
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


class DependencyManagerBase:
    raise_errors = True  #this is set in Dependency class inside method raise_
    exit_module_after_import = False
    check_dependency = True
    instances = {}
    saved_dependency_infos = dict()
    platform_info = None
    
    def __init__(self, module_name) -> None:
        if self.instances.get(module_name) is not None:
            raise KeyError("Duplicate. DependencyTester already defined for "
                           "module "+module_name)
        if not self.exit_module_after_import:
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
        if self.exit_module_after_import: raise ReturnFromModule(self)
    
    def pydependency(self, module_name, **kwargs):
        dep = PythonDependency(module_name,self, **kwargs)
        self.pydependencies.append(dep)
        return dep
    
    def import_module(self, module_name, **kwargs):
        dep = self.pydependency(module_name, **kwargs)
        return dep.imprt()

    def shelldependency(self, cmd, **kwargs):
        dep = ShellDependency(cmd, self, **kwargs)
        self.shelldependencies.append(dep)
        return dep
    
    def test_shellcommand(self, cmd,**kwargs):
        dep = self.shelldependency(cmd,**kwargs)
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
        if self.exit_module_after_import: return "exit"
        raise dependency_error

    @classmethod
    def save_dependency_info(cls, name, **kwargs):
        cls.saved_dependency_infos[name] = kwargs


    @classmethod
    def import_adapt_module(cls, mod_full_name, dependency_folder=None):
        if dependency_folder:
            sys.path.insert(0,
                    dependency_folder)  # this makes sure that packages
            # inside the dependency folder are  # found first. Unless the
            # module has already been imported.
        save = cls.raise_errors
        cls.raise_errors = BackendDependencyError
        try:
            mod = importlib.import_module(mod_full_name)
        except BackendDependencyError as e:
            e.handle()
            raise
        finally:
            cls.raise_errors = save
            if dependency_folder: sys.path.pop(0)
        try:
            manager_inst = cls.instances[mod_full_name]
        except KeyError:
            warnings.warn(f"Module {mod_full_name} did not define "
                          f"DependencyManager instance.")
            manager_inst = None
        return mod, manager_inst

    @classmethod
    def get_module_dependencies(cls, mod_full_name, perform_check=False,
            **kwargs):
        try:
            return cls.instances[mod_full_name]
        except KeyError:
            pass
        cls.exit_module_after_import = True
        cls.check_dependency = perform_check
        try:
            mod, manager_inst = cls.import_adapt_module(mod_full_name, **kwargs)
        except ReturnFromModule as e:
            # this should happen if DependencyManager was used
            manager_inst = e.manager_inst
        else:
            # this normally happens if DependencyManager was not defined
            # otherwise the following warning will be triggered:
            if manager_inst is not None:
                warnings.warn(f"Failed to return from {mod_full_name} "
                              f"although DependencyManager instance was "
                              f"defined. Please "
                              f"use DependencyManager.exit() method.")
        finally:
            cls.exit_module_after_import = False
            cls.check_dependency = True
        return manager_inst


class Dependency:
    
    default_install_tool = None
    
    def __init__(self, name, manager_inst, **kwargs):
        self.name = name
        self.manager = manager_inst
        self.error = None
        self.install_instructions = defaultdict(InstallInstruction)
        # map {system: InstallInstruction instance}
        try:
            kwarg_infos = self.manager.saved_dependency_infos[name]
        except KeyError:
            kwarg_infos = kwargs
        else:
            kwarg_infos.update(kwargs)
        self.process_kwargs(**kwarg_infos)
        
    
    def process_kwargs(self, pkg=None, instruction=None,
            install_tool=None, platform=""):
        if instruction:
            self.add_instruction(pkg, instruction, platform=platform)
        if pkg:
            self.add_pkg(pkg, install_tool=install_tool, platform=platform)
        if platform and self.perform_check:
            state = self.manager.platform_info.effective_vals.get(platform)
            if state is not True: warnings.warn(f"Dependency {self} requires "
                    f"platform {platform}.")
        
    
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} '{self.name}' from " \
                    f"{self.manager.module}>"

    @property
    def perform_check(self):
        return self.manager.check_dependency
    
    def add_pkg(self,*pkgs,install_tool=None,platform=""):
        if not install_tool: install_tool = self.default_install_tool
        self.install_instructions[platform].add_names(install_tool,*pkgs)
    
    def add_instruction(self,name, instruction,platform=""):
        self.install_instructions[platform].add_instructions(name, instruction)
        
    def raise_BackendDependencyError(self, caused_by=None):
        self.error = BackendDependencyError(self,caused_by)
        return self.manager.raise_error(self)
    
        
class PythonDependency(Dependency):
    
    default_install_tool = "pip"
        
    def imprt(self):
        if not self.perform_check: return
        try:
            mod = importlib.import_module(self.name)
        except Exception as e:
            self.raise_BackendDependencyError(e)
            mod = NotImplemented
        return mod
    
    
    
command_exists_cmd = "command -v "


class ShellDependency(Dependency):
    
    default_install_tool = "apt"
    
    def __init__(self, cmd, manager_inst, *, test_cmd=None,
            expected_return=None, **kwargs):
        super().__init__(cmd,manager_inst,**kwargs)
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
    
    
    
    
install_commands = {"pip" : "pip install -U", "apt": "sudo apt install"}


class InstallInstruction:
    
    def __str__(self):
        ret = ""
        for tool, pkgs in self.packages.items():
            if not pkgs: continue
            ret += install_commands[tool].strip() + " " + " ".join(pkgs) + "\n"
        if self.instructions:
            ret += "\n--- Additional instructions:\n"
            for pkg, instruction in self.instructions.items():
                if not instruction: continue
                ret += f"    {pkg}: " + ", ".join(instruction) + "\n"
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
        self.instructions = defaultdict(set)
        
    def add_instructions(self, name, *instructions):
        self.instructions[name] |= set(instructions)
    
    def add_names(self, tool, *names):
        self.packages[tool] |= set(names)
        
    def update(self, other):
        if not isinstance(other,self.__class__):
            raise ValueError
        for tool, names in other.packages.items():
            self.add_names(tool, *names)
        for name, instructions in other.instructions.items():
            self.add_instructions(name, *instructions)
            
    def __bool__(self):
        return bool(self.packages)