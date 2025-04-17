import fcntl
import os.path
from contextlib import contextmanager
import signal

# https://stackoverflow.com/questions/5255220/fcntl-flock-how-to-implement-a-timeout
@contextmanager
def timeout(seconds):
    def timeout_handler(signum, frame):
        raise TimeoutError

    original_handler = signal.signal(signal.SIGALRM, timeout_handler)

    try:
        signal.alarm(seconds)
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, original_handler)

class SharableLock:
    def __init__(self, fname: str = "lock.lock", create: bool = False, id: str|None = None) -> None:
        self.create = create
        self.lock_path = fname
        if create:
            self.fd = open(self.lock_path, "x")
        elif os.path.isfile(self.lock_path):
            self.fd = open(self.lock_path)
        else:
            raise FileNotFoundError(f"{self.lock_path} not found")

        self.file = None
        self.locked = False
        self.id = id


    def acquire(self, t: int | None = None) -> bool:
        if t is not None:
            #print(f"{self.id} waiting for the lock.")
            with timeout(t):
                try:
                    fcntl.flock(self.fd, fcntl.LOCK_EX)
                    self.locked = True
                    return True
                except TimeoutError:
                    print("Lock timed out")
                    return False
                except IOError:
                    print("Failed")
                    raise IOError

        else:
            try:
                fcntl.flock(self.fd, fcntl.LOCK_EX)
                self.locked = True
                print(f"{self.id} acquired lock")
                return True
            except IOError:
                print("Failed")
                raise IOError

    def release(self):
        assert self.locked, "Releasing a lock that has not been acquired."
        try:
            fcntl.flock(self.fd, fcntl.LOCK_UN)
            self.locked = False
        except IOError:
            print("Failed")
            raise IOError

    def delete_lock(self, unlink: bool = False):
        self.fd.close()
        if unlink:
            os.remove(self.lock_path)
