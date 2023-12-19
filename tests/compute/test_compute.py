import os
import src.compute.compute as compute


def test_list_all_domains():
    conn = compute.get_conn()
    domain_all = os.popen('virsh list --all')
    domain_count = domain_all.read().count('\n') - 3
    result = compute.list_all_domains(conn)
    assert result['is_success'] is True
    assert domain_count == len(result['result'])
    conn.close()


def test_conn_is_invalid():
    conn = compute.get_conn()
    conn.close()
    result = compute.list_all_domains(conn)
    assert result['is_success'] is False


def test_get_domain_detail():
    domain_uuid = '9b299916-73d7-4464-9b6e-d2286f5423e1'
    conn = compute.get_conn()
    detail_info = compute.get_domain_detail(conn, domain_uuid)
    assert detail_info['is_success'] is True
    assert detail_info['domain_detail']['domain_id'] == 5
    assert detail_info['domain_detail']['domain_name'] == 'test'
    assert detail_info['domain_detail']['domain_state'] == 'RUNNING'
    conn.close()


def test_domain_auto_start():
    domain_uuid = '9b299916-73d7-4464-9b6e-d2286f5423e1'
    conn = compute.get_conn()
    domain = conn.lookupByUUIDString(domain_uuid)
    result = compute.set_domain_auto_start(conn, domain_uuid, True)
    assert result['is_success'] is True and domain.autostart() == 1
    result = compute.set_domain_auto_start(conn, domain_uuid, False)
    assert result['is_success'] is True and domain.autostart() == 0
    conn.close()
