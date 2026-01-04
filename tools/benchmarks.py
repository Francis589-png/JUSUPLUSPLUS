import os
import time
import sys
import tempfile
import statistics

from pathlib import Path

WORKDIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WORKDIR))


SAMPLES = {
    "fib_recursive": """
function fib(n):
    if n < 2:
        return n
    end
    return fib(n - 1) + fib(n - 2)
end

say fib(18)
""",
    "name_lookup_loop": None,
}


def write_temp(src: str) -> str:
    td = tempfile.NamedTemporaryFile(delete=False, suffix=".jusu", dir=str(WORKDIR))
    td.write(src.encode('utf-8'))
    td.flush()
    td.close()
    return td.name


def run_benchmark(sample_src: str, backend: str, warmups=2, runs=6):
    import runtime.compiler as compiler

    path = write_temp(sample_src)
    keep_temp_on_error = True
    try:
        # warmup
        for _ in range(warmups):
            compiler.compile_and_run(path, backend=backend)

        times = []
        for _ in range(runs):
            t0 = time.perf_counter()
            compiler.compile_and_run(path, backend=backend)
            t1 = time.perf_counter()
            times.append(t1 - t0)

        return times
    except Exception as e:
        if keep_temp_on_error:
            print(f"Benchmark failed, keeping temp file: {path}")
        raise
    finally:
        if not keep_temp_on_error:
            try:
                os.unlink(path)
            except Exception:
                pass


def build_name_lookup_program(repeats=2000):
    # Build a function that repeatedly reads a global value 'math.pi'
    lines = ["function hot():", "    x = 0"]
    for i in range(repeats):
        lines.append("    x = x + math.pi")
    lines.append("    return x")
    lines.append("end")
    lines.append("say hot()")
    return "\n".join(lines)


def main():
    results = {}
    print(f"Working dir: {WORKDIR}")

    # Populate the generated sample
    SAMPLES['name_lookup_loop'] = build_name_lookup_program(repeats=1500)

    for name, src in SAMPLES.items():
        print(f"\nBenchmarking sample: {name}")
        results[name] = {}
        for backend in ("interp", "vm", "regvm"):
            print(f" Running backend: {backend}")
            times = run_benchmark(src, backend=backend)
            mean = statistics.mean(times)
            stdev = statistics.stdev(times) if len(times) > 1 else 0.0
            results[name][backend] = (times, mean, stdev)
            print(f"  times: {[round(t,4) for t in times]}")
            print(f"  mean: {mean:.4f}s  stdev: {stdev:.4f}s")

    print("\nSummary:")
    for name, data in results.items():
        interp = data['interp'][1]
        vm = data['vm'][1]
        faster = 'vm' if vm < interp else 'interp'
        improvement = ((interp - vm) / interp * 100) if interp != 0 else 0
        print(f" {name}: interp={interp:.4f}s vm={vm:.4f}s -> {faster} faster ({improvement:.1f}%)")


if __name__ == '__main__':
    main()
