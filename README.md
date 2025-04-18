# Shareable Lock
`shareable_lock` is a lock implementation that uses file locking underneath that can be shared across Python processes. Available locks from `multiprocessing` and `threading` don't allow for sharing instances for the same locks across Python processes. With `shareable_lock`'s `ShareableLock`, a lock for the same resource can be instantiated across different Python processes by creating an instance of the `ShareableLock` with the same locking file.

## Installing

Use `uv` to install the `shareable_lock` to your project.
```bash
uv pip install shareable_lock
```

## Creating the Lock instance

To create an instance of the lock, you can provide the path for the file associated with the resource being locked. Using the same file name across different processes implies locking the same resource. The `create` argument should be set to True for one of these processes to create the file used for locking and all other processes can create an instance of the lock for the same resource with `create = False`.

```python3
from shareable_lock import ShareableLock

lock = ShareableLock(fname = "lock.lock", create = True)
```

## Acquiring the Lock

To acquire the lock, create the instance of the `ShareableLock` and use the `acquire` method.
This uses the `fcntl.flock` internally to get a `fcntl.LOCK_EX` type lock on the file. If
`fcntl.flock` fails, an IOError is raised.

```python3
from shareable_lock import ShareableLock

lock = ShareableLock()
if lock.acquire(): 
    print("Lock acquired.")
```

A timeout can also be set to interrupt the `acquire` method after a give number of seconds pass.

```python3
from shareable_lock import ShareableLock

lock = ShareableLock()
if lock.acquire(): 
    print("Lock acquired.")
else:
    print("Acquire method timedout.")
```

## Releasing the Lock
To release the lock, create the instance of the `ShareableLock` and use the `release` method.
This uses the `fcntl.floc(self.fd, fcntl.LOCK_UN)` to release the `fcntl.LOCK_EX` on the file. If `fcntl.flock` fails, an IOError is raised.

```python3
from shareable_lock import ShareableLock

lock = ShareableLock()
lock.acquire()

lock.release()
```

Trying to release an unacquired lock will raise an assertion error.
```python3
from shareable_lock import ShareableLock

lock = ShareableLock()
lock.release()
```

## Deleting the Lock
The lock should be deleted once it is no longer being used by a process.

```python3
from shareable_lock import ShareableLock

lock = ShareableLock()
lock.delete()
```

The process that created the file being used by the `ShareableLock` should call `delete` with 
`unlink = True`. This will delete the file in addition to closing it.

```python3
from shareable_lock import ShareableLock

lock = ShareableLock(create = True)
lock.delete(unlink = True)
```
