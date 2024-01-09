import libvirt
import libvirt_qemu
import json
import base64


def get_guest_info(domain: libvirt.virDomain):
    command = '{"execute":"guest-info"}'
    res = libvirt_qemu.qemuAgentCommand(domain, command, timeout=-1, flags=0)
    return res


def guest_ping(domain: libvirt.virDomain):
    command = '{"execute":"guest-ping"}'
    res = libvirt_qemu.qemuAgentCommand(domain, command, timeout=-1, flags=0)
    return res


def guest_exec(domain: libvirt.virDomain,
               path: str,
               args: list = [],
               env: list = [],
               input_data: str = [],
               capture_output=True):
    command_args = {
        "path": path,
        "capture-output": capture_output
    }

    if args:
        command_args["arg"] = args

    if env:
        command_args["env"] = env

    if input_data:
        command_args["input_data"] = input_data

    command_json = {
        "execute": "guest-exec",
        "arguments": command_args
    }

    command = json.dumps(command_json)
    res = libvirt_qemu.qemuAgentCommand(domain, command, timeout=-1, flags=0)
    res_json: dict = json.loads(res)
    pid = res_json.get("return").get('pid')
    return pid


def guest_get_exec_result(domain: libvirt.virDomain, pid: int):
    command = '{"execute":"guest-exec-status","arguments":{"pid":%d}}' % pid
    res = libvirt_qemu.qemuAgentCommand(domain, command, timeout=-1, flags=0)
    return res


def guest_mkdir(domain: libvirt.virDomain, path: str):
    command = '{"execute":"guest-exec","arguments":{"path":"mkdir","arg":["-p","%s"],"capture-output":true}}' % path
    res = libvirt_qemu.qemuAgentCommand(domain, command, timeout=-1, flags=0)
    return res


def guest_open_file(domain: libvirt.virDomain, path: str, mode: str = "r"):
    command = '{"execute":"guest-file-open", "arguments":{"path":"%s","mode":"%s"}}' % (path, mode)
    res = libvirt_qemu.qemuAgentCommand(domain, command, timeout=-1, flags=0)
    return res


def guest_read_file(domain: libvirt.virDomain, handle: int, count: int = 4 * 1024):
    max_read_bytes = 48 * 1024 * 1024 # max is 48MB
    if count > max_read_bytes:
        count = max_read_bytes

    command = '{"execute":"guest-file-read", "arguments":{"handle":%s,"count":%s}}' % (handle, count)
    res = libvirt_qemu.qemuAgentCommand(domain, command, timeout=-1, flags=0)
    return res


def guest_write_file(domain: libvirt.virDomain, handle: int, content: str, is_content_base64: bool = False):
    if not is_content_base64:
        content = encode(content)
    command = '{"execute":"guest-file-write", "arguments":{"handle":%s,"buf-b64":"%s"}}' % (str(handle), content)
    res = libvirt_qemu.qemuAgentCommand(domain, command, timeout=-1, flags=0)
    return res


def guest_close_file(domain: libvirt.virDomain, handle: int):
    command = '{"execute":"guest-file-close", "arguments":{"handle":%s}}' % handle
    res = libvirt_qemu.qemuAgentCommand(domain, command, timeout=-1, flags=0)
    return res


def guest_get_network_interfaces(domain: libvirt.virDomain):
    command = '{"execute":"guest-network-get-interfaces"}'
    res = libvirt_qemu.qemuAgentCommand(domain, command, timeout=-1, flags=0)
    return res


####################
# Helper Functions #
####################
def encode(utf_str: str):
    """
    encode an utf8 str to base64 str
    """
    base64_str = base64.b64encode(utf_str.encode("utf-8"))
    return base64_str.decode("utf8")


def decode(base64_str: str):
    """
    decode a base64 str to a utf8 str
    """
    utf_str = base64.b64decode(base64_str).decode("utf-8")
    return utf_str


def decode_exec_res(res_str: str):
    """
    input: res_str
    Extract and decode the info within the execution result of a qemu-agent-command
    return the out_data or err_data if either of them exists.
    Return the value of "return" if neither of them exists.
    """
    res_json: dict = json.loads(res_str)
    out_data = res_json.get("return").get("out-data")
    err_data = res_json.get("return").get("err-data")
    if out_data:
        return decode(out_data)
    elif err_data:
        return decode(err_data)
    else:
        return str(res_json.get("return"))


def decode_file_read_res(res_str: str):
    res_json: dict = json.loads(res_str)
    buf_64 = res_json.get("return").get("buf-b64")
    if buf_64:
        return decode(buf_64)
    else:
        return str(res_json.get("return"))


def get_file_handle(res_str: str):
    res_json: dict = json.loads(res_str)
    return res_json.get("return")

