import threading

def thread_get_specific(name, thread=None):
    if not thread:
        thread = threading.current_thread()
    key = "_specific_"+name
    return getattr(thread, key) if hasattr(thread, key) else None

def thread_set_specific(name, value, thread=None):
    if not thread:
        thread = threading.current_thread()
    key = "_specific_"+name
    setattr(thread, key, value)


def get_ref_thread(thread=None):
    return thread_get_specific("ref_thread", thread)

def __start_thread(bootstrap, args):
    ref_thread = threading.current_thread()
    def update_ref():
        thread_set_specific("ref_thread", ref_thread, thread=bootstrap.__self__)
        bootstrap(*args)
    threading.Thread(target=update_ref).start()

def thread_get_specific_recursively(name, thread=None):
    if not thread:
        thread = threading.current_thread() 
    val = thread_get_specific(name, thread)
    if val:
        return val
    ref_thread = get_ref_thread(thread)
    if ref_thread:
        return thread_get_specific_recursively(name, ref_thread)
    else:
        return None
