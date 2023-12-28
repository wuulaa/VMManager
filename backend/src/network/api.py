import requests
from utils.response import APIResponse
from domain_xml.device import interface

def create_interface():
    '''create default libvirt interface'''
    try:
        interface_builder: interface.DeviceInterface = interface.create_default_interface_builder()
        xml_string = interface_builder.get_xml_string()
        APIResponse.success(xml_string)
    except Exception as err:
        APIResponse.error(code=400, msg=str(err))
    
    
