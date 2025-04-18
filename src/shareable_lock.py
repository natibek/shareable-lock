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


class ShareableLock:
    def __init__(
        self, fname: str = "lock.lock", create: bool = False,
    ) -> None:
        """Instantiates the lock with the associated file.

        Args:
            - fname: The name of the file to use as locks. `lock.lock` by default.
            - create: Whether to create the file when instantiating the lock. `False` by default.

        Raises:
            - FileNotFoundError: If not creating creating the file and file is not found.
        """
        self.create = create
        self.lock_path = fname

        if create:
            self.fd = open(self.lock_path, "x")
        elif os.path.isfile(self.lock_path):
            self.fd = open(self.lock_path)
        else:
            raise FileNotFoundError(f"{self.lock_path} not found")

        self.locked = False

    def acquire(self, t: int | None = None) -> bool:
        """Acquires the lock with an optional timeout (in seconds). An exclusive
        lock on the file is used. If timeout is exceeded, the `acquire` returns `False`.
        Otherwise, it returns true.

        Args:
            - t: Optional time out in seconds.

        Returns: `True` if lock is acquired successfully and `False` otherwise.

        Raises:
            - IOError: If `flock.flock` fails with an IOError.
        """
        if t is not None:
            with timeout(t):
                try:
                    fcntl.flock(self.fd, fcntl.LOCK_EX)
                    self.locked = True
                    return True
                except TimeoutError:
                    return False
                except IOError:
                    raise
        else:
            try:
                fcntl.flock(self.fd, fcntl.LOCK_EX)
                self.locked = True
                return True
            except IOError:
                raise

    def release(self):
        """Releases the lock. If it has not been acquired yet, as assertion error
        will be raised.

        Raises:
            - IOError: If `flock.flock` fails with an IOError.
        """
        assert self.locked, "Releasing a lock that has not been acquired."
        try:
            fcntl.flock(self.fd, fcntl.LOCK_UN)
            self.locked = False
        except IOError:
            raise

    def delete_lock(self, unlink: bool = False):
        """Close the file being used for locking the resource. If unlink is `True`,
        it also deletes the file.

        Args:
            - unlink: Whether to delete the lock file.
        """
        self.fd.close()
        if unlink:
            os.remove(self.lock_path)
