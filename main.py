import subprocess
import threading


class ThreadBash:
    def __init__(self):
        self.exit_ = False

        self.stdout = bytearray()
        self.stderr = bytearray()
        self.stdout_thread = None
        self.stderr_thread = None

        self._process = subprocess.Popen(["bash"],
                                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                         shell=False, )

    def prime_stdout(self):
        def read_stdout():
            nonlocal self
            stdout = self.stdout
            proc_stdout = self._process.stdout
            while not self.exit_:
                msg = proc_stdout.readline()
                stdout.extend(msg)
                print("stdout: ", msg.decode())

        self.stdout_thread = threading.Thread(target=read_stdout)
        self.stdout_thread.start()

    def read_stdout(self):
        print(self.stdout.decode())
        self.stdout = bytearray()

    def prime_stderr(self):
        def read_stderr():
            nonlocal self
            stderr = self.stderr
            proc_stderr = self._process.stderr
            while not self.exit_:
                msg = proc_stderr.readline()
                stderr.extend(msg)
                print("stderr: ", msg.decode())

        self.stderr_thread = threading.Thread(target=read_stderr)
        self.stderr_thread.start()

    def read_stderr(self):
        print(self.stderr.decode())
        self.stderr = bytearray()

    def send(self, item: str):
        data = (item + '\n').encode()
        self._process.stdin.write(data)
        self._process.stdin.flush()

    def run(self):
        proc_stdin = self._process.stdin
        try:
            while not self.exit_:
                res = input(">")
                proc_stdin.write((res + '\n').encode())
                proc_stdin.flush()
        except KeyboardInterrupt:
            self.exit_ = True

thread = ThreadBash()
# thread.run()
try:
    while not thread.exit_:
        thread.send(input(">"))
        print(thread.stdout)

except KeyboardInterrupt:
    thread.exit_ = True
