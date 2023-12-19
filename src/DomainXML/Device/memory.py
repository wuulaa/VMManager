from src.DomainXML.Device.device import Device
from src.Utils.XMLBuilder.xml_builder import XMLProperty, XMLChildBuilder, XMLBuilder


class _DeviceMemoryTarget(XMLBuilder):
    XML_NAME = "target"

    size = XMLProperty("./size", is_int=True)
    node = XMLProperty("./node", is_int=True)
    label_size = XMLProperty("./label/size", is_int=True)
    readonly = XMLProperty("./readonly", is_bool=True)
    block = XMLProperty("./block", is_int=True)
    requested = XMLProperty("./requested", is_int=True)
    current = XMLProperty("./current", is_int=True)


class _DeviceMemorySource(XMLBuilder):
    XML_NAME = "source"

    pagesize = XMLProperty("./pagesize", is_int=True)
    nodemask = XMLProperty("./nodemask")
    path = XMLProperty("./path")
    alignsize = XMLProperty("./alignsize", is_int=True)
    pmem = XMLProperty("./pmem", is_bool=True)


class DeviceMemory(Device):
    XML_NAME = "memory"

    MODEL_DIMM = "dimm"
    MODEL_NVDIMM = "nvdimm"
    models = [MODEL_DIMM, MODEL_NVDIMM]

    ACCESS_SHARED = "shared"
    ACCESS_PRIVATE = "private"
    accesses = [ACCESS_SHARED, ACCESS_PRIVATE]

    model = XMLProperty("./@model")
    access = XMLProperty("./@access")
    discard = XMLProperty("./@discard", is_yesno=True)
    uuid = XMLProperty("./uuid")

    source = XMLChildBuilder(_DeviceMemorySource, is_single=True)
    target = XMLChildBuilder(_DeviceMemoryTarget, is_single=True)
