from src.Utils.XMLBuilder.xml_builder import XMLProperty, XMLBuilder


class memory_allocation(XMLBuilder):
    XML_NAME = 'domain'

    size = XMLProperty('./maxMemory')
    slot = XMLProperty("./maxMemory/@slot")
    unit = XMLProperty("./maxMemory/@unit")

    size_memory = XMLProperty('./memory')
    unit_memory = XMLProperty("./memory/@unit")

    size_current_memory = XMLProperty('./currentMemory')
    unit_current_memory = XMLProperty("./currentMemory/@unit")

    def create(self, property: dict):
        self.size = property.get("size")
        self.slot = property.get("slot")
        self.unit = property.get("unit")

        self.size_memory = property.get("size_memory")
        self.unit_memory = property.get("unit_memory")

        self.size_current_memory = property.get("size_current_memory")
        self.unit_current_memory = property.get("unit_current_memory")
