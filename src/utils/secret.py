from src.utils.xml_builder.xml_builder import XMLBuilder, XMLChildBuilder, XMLProperty


class Usage(XMLBuilder):
    XML_NAME = 'usage'

    type = XMLProperty('./@type')

    volume = XMLProperty('./volume')
    name = XMLProperty('./name')
    target = XMLProperty('./target')


class Secret(XMLBuilder):
    XML_NAME = 'secret'

    ephemeral = XMLProperty('./@ephemeral', is_yesno=True)
    private = XMLProperty('./@private', is_yesno=True)

    description = XMLProperty('./description')
    uuid = XMLProperty('./uuid')

    usage = XMLChildBuilder(Usage)

    def set_defaults(self, cond=None):
        self.ephemeral = 'no'
        self.private = 'no'
