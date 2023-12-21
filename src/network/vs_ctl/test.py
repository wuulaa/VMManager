from src.network.vs_ctl.vsctl import VSCtl
vsctl = VSCtl('tcp', '192.168.1.18', 6640)
vsctl.run(command='show')