"""Helper module executed in a subprocess to enforce child-side limits

Usage: python -m runtime._sandbox_child --file <file> --backend <backend> [--mem MB]

This module sets RLIMIT_AS (address space) to limit memory (on Unix) then
imports the runtime compiler and runs the target file using compile_and_run.
Any unhandled exception will be printed and the process will exit with non-zero.
"""
import sys
import argparse
import traceback


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--file', required=True)
    p.add_argument('--backend', default='interp')
    p.add_argument('--mem', type=int, default=0, help='Memory limit in MB (Unix only)')
    args = p.parse_args()

    # Try to apply memory limit (Unix only)
    if args.mem and args.mem > 0:
        try:
            import resource
            soft = hard = args.mem * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (soft, hard))
        except Exception as e:
            print(f"[sandbox-child] warning: could not set memory limit: {e}", file=sys.stderr)

    # Optionally attempt to enable seccomp on Linux if python 'seccomp' is available.
    if sys.platform.startswith('linux'):
        try:
            import seccomp
            # Basic filter: allow stdio, exit, sigreturn, read/write on fd 0-2, minimal syscalls.
            f = seccomp.SyscallFilter(defaction=seccomp.KILL)
            allow = [
                'read', 'write', 'exit', 'exit_group', 'sigreturn', 'rt_sigreturn',
                'futex', 'clock_gettime', 'nanosleep', 'getpid', 'gettid',
                'close', 'brk', 'mmap', 'mprotect', 'munmap', 'arch_prctl'
            ]
            for name in allow:
                try:
                    f.add_rule(seccomp.ALLOW, name)
                except Exception:
                    # ignore missing syscalls for some kernels
                    pass
            f.load()
            print('[sandbox-child] seccomp filter loaded')
        except Exception:
            # seccomp binding not available or failed — continue without it
            print('[sandbox-child] seccomp not enabled (missing module or unsupported)', file=sys.stderr)

    # On Windows, attempt to place the process in a Job object if pywin32 is available to enforce limits
    if sys.platform.startswith('win'):
        try:
            import win32job
            import win32api
            hJob = win32job.CreateJobObject(None, '')
            # basic limits: terminate child processes on job close
            extended_limits = win32job.QueryInformationJobObject(hJob, win32job.JobObjectExtendedLimitInformation)
            # No aggressive limits by default — external supervisor can set memory/time via job object
            win32job.SetInformationJobObject(hJob, win32job.JobObjectExtendedLimitInformation, extended_limits)
            win32job.AssignProcessToJobObject(hJob, win32api.GetCurrentProcess())
            print('[sandbox-child] assigned to Job object')
        except Exception:
            print('[sandbox-child] Windows Job object not enabled (pywin32 missing or unsupported)', file=sys.stderr)

    try:
        from runtime.compiler import compile_and_run
        compile_and_run(args.file, backend=args.backend)
    except SystemExit:
        # allow SystemExit to propagate
        raise
    except Exception:
        traceback.print_exc()
        sys.exit(2)


if __name__ == '__main__':
    main()
