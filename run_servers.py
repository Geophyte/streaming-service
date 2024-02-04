import multiprocessing
import subprocess
import signal
import os


def run_process(program, *args, cwd=None):
    print(f"Running: {program} with arguments: {args}")
    subprocess.run([program, *args], cwd=cwd)


def signal_handler(signum, frame):
    print(f"Received signal {signum}. Terminating all processes.")
    os.kill(os.getpid(), signal.SIGINT)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    coordinator_host = "127.0.0.1"
    coordinator_port = 5000

    server_ports = [5001, 5002]

    coordinator_programs = [["python", "coordinator.py",
                             "--coordinator_host", coordinator_host,
                             "--coordinator_port", str(coordinator_port)]]
    server_programs = []
    for i, port in enumerate(server_ports):
        server_programs.append(["python", "server.py",
                                "--coordinator_host", coordinator_host,
                                "--coordinator_port", str(coordinator_port),
                                "--server_host", "127.0.0.1",
                                "--server_port", str(port),
                                "--server_id", str(i)])

    processes = []

    try:
        for program, *args in coordinator_programs:
            process = multiprocessing.Process(target=run_process, args=(program, *args))
            processes.append(process)
            process.start()
        for program, *args in server_programs:
            cwd = os.path.abspath('hls-server')
            process = multiprocessing.Process(target=run_process, args=(program, *args), kwargs={'cwd': cwd})
            processes.append(process)
            process.start()

        while True:
            pass

    except KeyboardInterrupt:
        print("KeyboardInterrupt: Terminating all processes.")
    finally:
        for process in processes:
            process.terminate()
            process.join()

    print("All processes terminated.")
