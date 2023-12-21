from src.utils.xml_builder.xml_builder import XMLBuilder, XMLProperty, XMLChildBuilder


class VPU(XMLBuilder):
    XML_NAME = 'vcpu'
    id = XMLProperty("./@id")
    enable = XMLProperty("./@enable")
    hotpluggable = XMLProperty("./@hotpluggable")
    order = XMLProperty("./@order")

    def create(self, property: dict):
        self.id = property.get("id")
        self.enalbe = property.get("enable")
        self.hotpluggable = property.get("hotpluggable")
        self.order = property.get("order")


class VPUS(XMLBuilder):
    XML_NAME = 'domain'
    vcpu = XMLProperty("./vcpu")
    placement = XMLProperty("./vcpu/@placement")
    cpuset = XMLProperty("./vcpu/@cpuset")
    current = XMLProperty("./vcpu/@current")
    vpus = XMLChildBuilder(VPU, './vcpus', is_single=False)

    def create(self, property: dict):
        self.vcpu = property.get("vcpu")
        self.placement = property.get("placement")
        self.cpuset = property.get("cpuset")
        self.current = property.get("current")


# v = VPUS()
# d = {"vcpu": 2, "placement": "test"}
# v.create(d)


# print(v.get_xml_string())
