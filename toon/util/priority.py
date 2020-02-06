# rush derived from Psychtoolbox
import os
import gc
import sys
import warnings


if sys.platform == 'win32':
    kernel32 = None
    avrt = None
    from ctypes import WinDLL, get_last_error, set_last_error, byref
    from ctypes.wintypes import LPDWORD, LPCSTR
    try:
        kernel32 = WinDLL('kernel32', use_last_error=True)
    except Exception:
        warnings.warn('kernel32 import failed.')
    try:
        avrt = WinDLL('Avrt', use_last_error=True)
    except Exception:
        warnings.warn('Avrt import failed.')

    # https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-setpriorityclass
    NORMAL_PRIORITY_CLASS = 0x00000020
    HIGH_PRIORITY_CLASS = 0x00000080
    REALTIME_PRIORITY_CLASS = 0x00000100

    # https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-setthreadpriority
    THREAD_PRIORITY_NORMAL = 0
    THREAD_PRIORITY_ABOVE_NORMAL = 1
    THREAD_PRIORITY_HIGHEST = 2
    THREAD_PRIORITY_TIME_CRITICAL = 15

    # https://docs.microsoft.com/en-us/windows/win32/procthread/process-security-and-access-rights
    PROCESS_SET_INFORMATION = 0x0200
    PROCESS_QUERY_INFORMATION = 0x0400

    thread_pool = {}  # keep a dict of

    # refs:
    # https://github.com/Psychtoolbox-3/Psychtoolbox-3/blob/e65061d5e7e6ff1fcf45c50eecd5819daa857919/PsychSourceGL/Source/Common/Screen/SCREENGetMouseHelper.c#L608
    # https://github.com/Psychtoolbox-3/Psychtoolbox-3/blob/2ad56475c2b5059701e2616cc1b77a6f6f20380b/PsychSourceGL/Source/Windows/Base/PsychTimeGlue.c#L1358
    def priority(level=0, pid=None):
        # 0 = normal priority
        # 1 = high
        # 2 = realtime
        if level > 0:
            gc.disable()
        else:
            gc.enable()

        if kernel32 is None and avrt is None:
            # nothing to do if we don't have these
            return False

        pid = os.getpid()
        process = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_SET_INFORMATION, 0, pid)
        thread = kernel32.GetCurrentThread()

        if thread in thread_pool.keys():
            thread_grp = thread_pool[thread]
        else:
            thread_grp = {'mmcss': None}
            thread_pool[thread] = thread_grp

        # if this is a MMCSS scheduled thread, need to revert to normal first
        if avrt and thread_grp['mmcss']:
            avrt.AvRevertMmThreadCharacteristics(thread_grp['mmcss'])
            thread_grp['mmcss'] = None

        # clear error if anything?
        err = get_last_error()
        if err:
            set_last_error(0)
            return False
        if level == 0:
            kernel32.SetPriorityClass(process, NORMAL_PRIORITY_CLASS)
            kernel32.SetThreadPriority(thread, THREAD_PRIORITY_NORMAL)
        elif level == 1:
            kernel32.SetPriorityClass(process, HIGH_PRIORITY_CLASS)
            if avrt:
                tmp = LPDWORD()
                thread_grp['mmcss'] = avrt.AvSetMmMaxThreadCharacteristicsA(LPCSTR(b'Pro Audio'), LPCSTR(b'Capture'), byref(tmp))
            if not thread_grp['mmcss']:  # failed
                kernel32.SetThreadPriority(thread, THREAD_PRIORITY_HIGHEST)

        elif level == 2:
            # first try to set time critical
            if (not kernel32.SetPriorityClass(process, REALTIME_PRIORITY_CLASS) or
                    kernel32.GetPriorityClass(process) != REALTIME_PRIORITY_CLASS):
                # try for high priority scheduling instead
                kernel32.SetPriorityClass(process, HIGH_PRIORITY_CLASS)
            if avrt:
                tmp = LPDWORD()
                thread_grp['mmcss'] = avrt.AvSetMmMaxThreadCharacteristicsA(LPCSTR(b'Pro Audio'), LPCSTR(b'Capture'), byref(tmp))
            if not thread_grp['mmcss']:  # failed
                kernel32.SetThreadPriority(thread, THREAD_PRIORITY_ABOVE_NORMAL)

        return True

elif sys.platform == 'darwin':
    # TODO
    # https://developer.apple.com/library/archive/documentation/Darwin/Conceptual/KernelProgramming/scheduler/scheduler.html#//apple_ref/doc/uid/TP30000905-CH211-BABCHEEB
    def priority(level=0, pid=None):
        if level > 0:
            gc.disable()
        else:
            gc.enable()
        return True

else:  # linux
    import os
    import ctypes
    import ctypes.util

    MCL_CURRENT = 1
    MCL_FUTURE = 2

    libc = ctypes.CDLL(ctypes.util.find_library('c'))

    def priority(level=0, pid=0):
        if level > 0:
            gc.disable()
        else:
            gc.enable()

        libc.munlockall()
        if level == 1:
            policy = os.SCHED_RR
        elif level == 2:
            policy = os.SCHED_FIFO
        else:
            policy = os.SCHED_OTHER

        sched_param = os.sched_param(os.sched_get_priority_max(policy))

        try:
            os.sched_setscheduler(pid, policy, sched_param)
        except PermissionError:
            return False

        if level == 2:  # try to lock memory (and we succeeded in sched already)
            res = libc.mlockall(MCL_CURRENT | MCL_FUTURE)
            if res != 0:
                libc.munlockall()

        return True
