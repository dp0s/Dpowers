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
from warnings import warn
import time, threading, subprocess, multiprocessing
from .psutil_fix import psutil
from .arghandling import PositiveInt


def select_running_processes(*ps):
    # print(ps,type(ps))
    for p in ps:
        if isinstance(p, psutil.Process):
            if p.is_running(): yield p
        else:
            try:
                pid = p.pid
            except AttributeError:
                # print(p,type(p))
                if isinstance(p, PositiveInt):
                    pid = p
                else:
                    raise TypeError
            try:
                proc = psutil.Process(pid)
            except psutil.NoSuchProcess:
                pass
            else:
                if proc.is_running(): yield proc
   
def get_running_process(p):
    t = tuple(select_running_processes(p))
    if not t:
        raise ProcessLookupError("No running process for " + str(p))
    if len(t) > 1:
        raise ProcessLookupError("More than 1 running process found.")
    return t[0]



def terminate_process(*pids_or_processes, timeout=5, kill=True):
    procs = tuple(select_running_processes(*pids_or_processes))
    for proc in procs: proc.terminate()
    gone, alive = psutil.wait_procs(procs, timeout)
    if alive and kill:
        kill_process(*alive, timeout=timeout)
        
        
def kill_process(*pids_or_processes, timeout=5):
    procs = tuple(select_running_processes(*pids_or_processes))
    for proc in procs: proc.kill()
    gone, alive = psutil.wait_procs(procs, timeout)
    if alive:
        raise TimeoutError(f"The following process(es) could not be "
                           f"killed after {timeout} seconds:\n{alive}")


def find_other_instances(compare=("name", "exe", "cmdline"), ad_value=None):
    this_process = psutil.Process()
    this_dict = this_process.as_dict(compare, ad_value)
    print(this_dict)
    print("find other instances")
    for p in psutil.process_iter(compare, ad_value):
        if p == this_process: continue
        if this_dict["name"] == p.info["name"]:
            print(p.info)


class LaunchFuncs:
    """This class offers functions to introduce an easier syntax for calling
    subprocesses and threads. It should be used via the instance "launch".
    examples:
    launch("notify-send text")
    launch(["notify-send","text"])
    launch("notify-send","text")
    """
    
    @staticmethod
    def thread(targetfunc, *argstopass, initial_time_delay=None,
            **kwargstopass):
        if initial_time_delay:
            subthread = threading.Timer(initial_time_delay, targetfunc,
                    args=argstopass, kwargs=kwargstopass)
        else:
            subthread = threading.Thread(target=targetfunc,
                args=argstopass, kwargs=kwargstopass)
        subthread.start()
        return subthread
    
    
    
    PIPE = subprocess.PIPE
    CalledProcessError = subprocess.CalledProcessError
    TimeoutExpired = subprocess.TimeoutExpired
    SubprocessError = subprocess.SubprocessError
    class SubprocessStdErrReceived(SubprocessError):
        pass
    class Automatic:
        pass
    
    @staticmethod
    def _handle_arguments(*args):
        l = len(args)
        if l == 0:
            raise SyntaxError("no arguments for Popen specified.")
        elif l == 1:
            args = args[0]
            if isinstance(args, str):
                if " " in args: return args, True
                return args, False
            elif not isinstance(args, (list, tuple)):
                raise TypeError(
                        "command passed must be a string, list or tuple.")
        return [str(i) for i in args], False
    
    default_Popen_kwargs = {"universal_newlines": True}
    
    def set_default_Popen_kwargs(self, **kwargs):
        self.default_Popen_kwargs = kwargs
    
    def __call__(self, *args, stdout=None, stderr=None, stdin=None, check=False,
            check_err=False, timeout=None, shell=Automatic, wait=False,
            couple=False, **Popen_kwargs):
        """Does NOT wait for the process to finish before continuing."""
        args, s = self._handle_arguments(*args)
        if shell is not self.Automatic: s = shell
        if stdout is True: stdout = subprocess.PIPE
        if stderr is True: stderr = subprocess.PIPE
        if stdin is True: stdin = subprocess.PIPE
        if stderr is None and check_err: stderr = subprocess.PIPE
        kwargs = self.default_Popen_kwargs.copy()
        if Popen_kwargs: kwargs.update(Popen_kwargs)
        Popen_object = psutil.Popen(args, shell=s, stdout=stdout, stderr=stderr,
                stdin=stdin, **kwargs)
        Popen_object.time_started = time.time()
        if couple:
            Popen_object.couple_object = self.CoupleProcess(Popen_object)
        if wait:
            self.wait_check_process(Popen_object, check, check_err, timeout,
                    raise_error=True)
        elif check or timeout or check_err:
            self.thread(self.wait_check_process, Popen_object, check, check_err,
                    timeout, raise_error=False)
        return Popen_object
    
    @staticmethod
    def wait_check_process(Popen_object, check_exitCode=True, check_err=True,
            timeout=None, raise_error=False):
        try:
            exitCode = Popen_object.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            Popen_object.kill()
            Popen_object.wait()
            raise
        try:
            Popen_object.duration = time.time() - Popen_object.time_started
        except AttributeError:
            pass
        if check_exitCode and exitCode:
            msg = "Command '{Popen_object.args}' returned Nonzero exit status " \
                  "" \
                  "{exitCode} after duration {" \
                  "Popen_object.duration}.".format_map(locals())
            if raise_error: raise subprocess.SubprocessError(msg)
            warn(msg)
        if check_err:
            err = Popen_object.stderr.read()
            if err:
                msg = "Command '{Popen_object.args}' returned following value " \
                      "" \
                      "for stderr after duration {Popen_object.duration}:\n{" \
                      "err}".format_map(locals())
                if raise_error: raise subprocess.SubprocessError(msg)
                warn(msg)
    
    
    
    def get(self, *args, stdout=True, stderr=True, stdin=None, ret_stdout=True,
            check=True, check_err=True, shell=Automatic, input=None,
            **Popen_run_kwargs):
        """Waits for the subprocess to finish and returns the
        subproces.CompletedProcess object."""
        args, shell_ = self._handle_arguments(*args)
        if shell is not self.Automatic: shell_ = shell
        if stdout is True: stdout = subprocess.PIPE
        if stderr is True: stderr = subprocess.PIPE
        if stdin is True: stdin = subprocess.PIPE
        if stdout is not subprocess.PIPE: ret_stdout = False
        if stderr is not subprocess.PIPE: check_err = False
        if not check_err and ret_stdout:
            # in this case, the stderr value is not used anyway
            stderr = None
        time_started = time.time()
        # _print(args)
        if input is not None:
            Popen_run_kwargs["input"] = input
        elif stdin is not None:
            Popen_run_kwargs["stdin"] = stdin
        kwargs = self.default_Popen_kwargs.copy()
        kwargs.update(Popen_run_kwargs)
        CompletedProc = subprocess.run(args, shell=shell_, stdout=stdout,
                stderr=stderr, check=check, **kwargs)
        CompletedProc.duration = time.time() - time_started
        if check_err and CompletedProc.stderr:
            raise self.SubprocessStdErrReceived(
                    "Command '{args}' returned following value for stderr "
                    "after duration {CompletedProc.duration}:"
                    "{CompletedProc.stderr}".format_map(locals()))
        if ret_stdout:
            stdout = CompletedProc.stdout
            if stdout.endswith("\n"): stdout = stdout[:-1]
            return stdout
        return CompletedProc
    
    
    def wait(self, *args, stdout=None, stderr=None, check_err=False, **kwargs):
        if stderr is None:
            if check_err: stderr = subprocess.PIPE
        else:
            check_err = False
        return self.get(*args, stdout=stdout, stderr=stderr,
                check_err=check_err, ret_stdout=False, **kwargs)
    
    
    class CoupleProcess:
        def __init__(self, child, parent=None, checktime=1):
            self.checktime = checktime
            self.child = get_running_process(child)
            if parent:
                self.parent = get_running_process(parent)
            else:
                # use this process as parent
                self.parent = psutil.Process()
            # print(self.parent,self.child)
            checker_process = multiprocessing.Process(target=self.run)
            checker_process.daemon = True
            checker_process.start()
        def run(self):
            time.sleep(self.checktime)
            while self.parent.is_running() and self.child.is_running() and \
                self.parent.status() != psutil.STATUS_ZOMBIE  and  \
                    self.child.status() != psutil.STATUS_ZOMBIE:
                time.sleep(self.checktime)
            #print(self.parent.status(), self.child.status())
            kill_process(self.child, self.parent)



launch = LaunchFuncs()