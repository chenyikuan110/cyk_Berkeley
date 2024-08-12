import subprocess
import threading
import time
import re

def run_socat_and_wait_for_ports():
    try:
        # Start the socat command
        process = subprocess.Popen(
            ['socat', '-d', '-d', '-d', 'pty,raw', 'pty,raw'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        print(f"socat is running with PID {process.pid}")

        # Regular expression to find pty devices in the output
        pty_regex = re.compile(r'PTY is /dev/pts/\d+')

        # Function to monitor the output
        def monitor_output():
            for stdout_line in iter(process.stdout.readline, ""):
                print(f"STDOUT: {stdout_line.strip()}")
                # Check if the line contains a PTY device path
                match = pty_regex.search(stdout_line)
                if match:
                    print(f"Detected PTY device: {match.group()}")

            for stderr_line in iter(process.stderr.readline, ""):
                print(f"STDERR: {stderr_line.strip()}")

        # Start the monitoring thread
        output_thread = threading.Thread(target=monitor_output)
        output_thread.daemon = True
        output_thread.start()

        # Wait for a PTY device to be detected
        while True:
            time.sleep(1)  # Check every second

    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    run_socat_and_wait_for_ports()

if __name__ == "__main__":
    main()
