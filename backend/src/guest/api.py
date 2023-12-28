# from src.domain_xml.xml_init import create_initial_xml
# # from src.volume.xml.volume.rbd_builder import RbdVolumeXMLBuilder
# import configparser
# import requests
import os
import sys

# def create_domain(domain_name: str, slave_name: str):
#     cf = configparser.ConfigParser()
#     cf.read('backend/config.ini',encoding='utf-8')
#     print(cf.sections())
#     print(cf['slaves']['slave1'])
#     guest = create_initial_xml(domain_name)
#     rbdXML = RbdVolumeXMLBuilder()
#     device = rbdXML.construct(domain_name)
#     guest.devices.disk.append(device)
#     respose = requests.post("http://localhost:5001/addDomain/")
#     requests.

# create_domain("test", "test")

print(sys.path)
print(os.getcwd())

    