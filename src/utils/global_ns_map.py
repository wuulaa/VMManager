Global_NameSpaces = {}


def init():
    global Global_NameSpaces
    Global_NameSpaces = {}
    print("Global ns map initiated")


def register_namespace(prefix: str, uri: str):
    Global_NameSpaces[prefix] = uri


def unregister_namespace(prefix: str):
    Global_NameSpaces.pop(prefix)


def get_ns_map() -> dict:
    return Global_NameSpaces
