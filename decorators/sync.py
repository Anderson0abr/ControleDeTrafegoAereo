import _thread
import threading
import types

def synchronized_with_attr(lock_name):
    def decorator(method):
        def synced_method(self, *args, **kws):
            lock = getattr(self, lock_name)
            with lock:
                return method(self, *args, **kws)
        return synced_method()
    return decorator

def synchronized_with(lock):
    def synchronized_obj(obj):
        if type(obj) is types.FunctionType:
            obj.__lock__ = lock
            def func(*args, **kws):
                with lock:
                    obj(*args, **kws)
            return func
        elif type(obj) is types.ClassType:
            orig_init = obj.__init__
            def __init__(self, *args, **kws):
                self.__lock__ = lock
                orig_init(self, *args, **kws)
            obj.__init__ = __init__

            for key in obj.__dict__:
                val = obj.__dict__[key]
                if type(val) is types.FunctionType:
                    decorator = synchronized_with(lock)
                    obj.__dict__[key] = decorator(val)
            return obj
    return synchronized_obj

def synchronized(item):
    if type(item) is type(""):
        decorator = synchronized_with(item)
        return decorator(item)
    if type(item) is _thread.LockType:
        decorator = synchronized_with(item)
        return decorator(item)
    else:
        new_lock = threading.Lock()
        decorator = synchronized_with(new_lock)
        return decorator(item)