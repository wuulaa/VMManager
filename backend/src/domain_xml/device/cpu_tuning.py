from src.utils.xml_builder.xml_builder import XMLBuilder, XMLProperty, XMLChildBuilder


class Cachetune(XMLBuilder):
    XML_NAME = 'cachetune'
    vcpus = XMLProperty('./@vcpus')

    cache_id = XMLProperty('./cache/@id')
    cache_level = XMLProperty('./cache/@level')
    cache_type = XMLProperty('./cache/@type')
    cache_size = XMLProperty('./cache/@size')
    cache_unit = XMLProperty('./cache/@unit')

    monitor_level = XMLProperty('./monitor/@level')
    monitor_vcpus = XMLProperty('./monitor/@vcpus')

    def create(self, property: dict):
        self.vcpus = property.get("vcpus")

        self.cache_id = property.get("cache_id")
        self.cache_level = property.get("cache_level")
        self.cache_type = property.get("cache_type")
        self.cache_size = property.get("cache_size")
        self.cache_unit = property.get("cache_unit")

        self.monitor_level = property.get("monitor_level")
        self.monitor_vcpus = property.get("monitor_vcpus")


class Memorytune(XMLBuilder):
    XML_NAME = 'memorytune'
    vcpus = XMLProperty('./@vcpus')

    node_id = XMLProperty('./node/@id')
    node_bandwidth = XMLProperty('./node/@bandwidth')

    def create(self, property: dict):
        self.vcpus = property.get("vcpus")
        self.node_id = property.get("node_id")
        self.node_bandwidth = property.get("node_bandwidth")


class Cputune(XMLBuilder):

    # vcpuin
    vcpuin_vcpu = XMLProperty('./vcpuin/@vcpu')
    vcpuin_cpuset = XMLProperty('./cpuset/@cpuset')

    # emulatorpin
    emulatorpin_cpuset = XMLProperty('./emulatorpin/@cpuset')

    # iothreadpin
    iothreadpin_iothread = XMLProperty('./iothreadpin/@iothread')
    iothreadpin_cpuset = XMLProperty('./iothreadpin/@cpuset')

    # shares
    shares = XMLProperty('./shares')

    # period
    period = XMLProperty('./period')

    # quota
    quota = XMLProperty('./quota')

    # global_period
    global_period = XMLProperty('./global_period')

    # global_quota
    global_quota = XMLProperty('./global_quota')

    # emulator_period
    emulator_period = XMLProperty('./emulator_period')

    # emulator_quota
    emulator_quota = XMLProperty('./emulator_quota')

    # iothread_period
    iothread_period = XMLProperty('./iothread_period')

    # iothread_quota
    iothread_quota = XMLProperty('./iothread_quota')

    # vcpusched
    vcpusched_vcpus = XMLProperty('./vcpusched/@vcpus')
    vcpusched_scheduler = XMLProperty('./vcpusched/@scheduler')
    vcpusched_priority = XMLProperty('./vcpusched/@priority')

    # iothreadched
    iothreadched_iothread = XMLProperty('./iothreadched/@iothread')
    iothreadched_scheduler = XMLProperty('./iothreadched/@scheduler')

    # cachetune
    cachetune = XMLChildBuilder(Cachetune)

    # cachetune
    memorytune = XMLChildBuilder(Memorytune)

    def create(self, property: dict):
        self.vcpuin_vcpu = property.get("vcpuin_vcpu")
        self.vcpuin_cpuset = property.get("vcpuin_cpuset")

        self.emulatorpin_cpuset = property.get("emulatorpin_cpuset")

        self.iothreadpin_iothread = property.get("iothreadpin_iothread")
        self.iothreadpin_cpuset = property.get("iothreadpin_cpuset")

        self.shares = property.get("shares")

        self.period = property.get("period")

        self.quota = property.get("quota")

        self.global_period = property.get("global_period")
        self.global_quota = property.get("global_quota")

        self.emulator_period = property.get("emulator_period")
        self.emulator_quota = property.get("emulator_quota")

        self.iothread_period = property.get("iothread_period")
        self.iothread_quota = property.get("iothread_quota")

        self.vcpusched_vcpus = property.get("vcpusched_vcpus")
        self.vcpusched_scheduler = property.get("vcpusched_scheduler")
        self.vcpusched_priority = property.get("vcpusched_priority")

        self.iothreadched_iothread = property.get("iothreadched_iothread")
        self.iothreadched_scheduler = property.get("iothreadched_scheduler")
