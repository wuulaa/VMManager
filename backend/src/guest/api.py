from src.volume.api import API
from src.guest.service import GuestService

status = {
    0:"nostate",
    1:"running",
    2:"blocked",
    3:"paused",
    4:"shutdown",
    5:"shutoff",
    6:"crashed",
    7:"pmsuspended"
}
guestService = GuestService()

class GuestAPI():

    def create_domain(self, domain_name: str, slave_name: str, **kwargs):
        return guestService.create_domain(domain_name, slave_name, **kwargs)

    def shutdown_domain(self, domain_name: str, slave_name: str):
        return guestService.shutdown_domain(domain_name, slave_name)

    def destroy_domain(self, domain_name: str, slave_name: str):
        return guestService.destroy_domain(domain_name, slave_name)

    def pause_domain(self, domain_name: str, slave_name: str):
        return guestService.pause_domain(domain_name, slave_name)(domain_name, slave_name)

    def resume_domain(self, domain_name: str, slave_name: str):
        return guestService.resume_domain(domain_name, slave_name)

    def start_domain(self, domain_name: str, slave_name: str):
        return guestService.start_domain(domain_name, slave_name)

    def batch_start_domains(self, domains_name_list, slave_name: str):
        return guestService.batch_start_domains(domains_name_list, slave_name)

    def batch_pause_domains(self, domains_name_list, slave_name: str):

        return guestService.batch_pause_domains(domains_name_list, slave_name)
    
    def batch_shutdown_domains(self, domains_name_list, slave_name: str):
        return guestService.batch_shutdown_domains(domains_name_list, slave_name)

    def batch_delete_domains(self, domains_name_list, slave_name: str):
        return guestService.batch_delete_domains(domains_name_list, slave_name)

    def batch_restart_domains(self, domains_name_list, slave_name: str):
        return guestService.batch_restart_domains(domains_name_list, slave_name)

    def get_domains_list():
        return guestService.get_domains_list()

    def rename_domain(self, domain_name: str, new_name: str, slave_name: str):
        return guestService.rename_domain(domain_name, new_name, slave_name)

    def put_description(self, domain_name: str, new_description: str, slave_name: str):
        return guestService.put_description(domain_name, new_description, slave_name)

    def delete_domain(self, domain_name: str, slave_name: str):
        return guestService.delete_domain(domain_name, slave_name)
    



    