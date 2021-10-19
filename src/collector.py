from xml.etree.ElementTree import XML, fromstring
import requests
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily, StateSetMetricFamily

HA_ROLE_MAP = {'Primary (Active)':'primary', 'Backup (Passive)': 'backup'}

def get_labels(root):
  name = root.find('./sipServer/NAME').text
  version = root.find('./version').text
  ha_role = HA_ROLE_MAP.get(root.find('./sipServer/HA_ROLE').text)
  return [name, version, ha_role]

class XmlNodeGaugeMetricFamily(GaugeMetricFamily):
  def __init__(self, name, root_node, search_path):
    node = root_node.find(search_path)
    super().__init__(name, node.get('rem'), labels=['app_name', 'app_version', 'app_ha_role'])
    self.add_metric(get_labels(root_node), node.text)

class XmlNodeCounterMetricFamily(CounterMetricFamily):
  def __init__(self, name, root_node, search_path):
    node = root_node.find(search_path)
    super().__init__(name, node.get('rem'), labels=['app_name', 'app_version', 'app_ha_role'])
    self.add_metric(get_labels(root_node), node.text)

class XmlNodeEnumMetricFamily(StateSetMetricFamily):
  def __init__(self, name, states, root_node, search_path):
    node = root_node.find(search_path)
    value_dict = dict()
    for state, label in states:
      value_dict[label] = (state == node.text and 1 or 0)
    super().__init__(name, node.get('rem'), labels=['app_name', 'app_version', 'app_ha_role'])
    self.add_metric(get_labels(root_node), value=value_dict),

class GenesysSIPServerCollector(object):
    registry = None

    def __init__(self, registry=None):
      if registry:
        self.registry = registry
        registry.register(self)

    def collect(self):
      if self.registry._target_info and 'target' in self.registry._target_info:
        target = self.registry._target_info.get('target')

        try:
          r = requests.get('http://{}/serverx'.format(target))
        except:
          return

        root = fromstring(r.text)
        node_sipserver = root.find('./sipServer')
        node_sipcallmanager = root.find('./sipCallManager')

        yield XmlNodeGaugeMetricFamily('genesys_sipserver_thread_count', root, './sipServer/CORE_THREADS_COUNT')
        yield XmlNodeGaugeMetricFamily('genesys_sipserver_memory_usage', root, './sipServer/SIPS_MEMORY_USAGE')
        yield XmlNodeGaugeMetricFamily('genesys_sipserver_cpu_usage', root, './sipServer/SIPS_CPU_USAGE')
        yield XmlNodeEnumMetricFamily('genesys_sipserver_ha_role', [('Primary (Active)', 'primary'), ('Backup (Passive)', 'backup')], root, './sipServer/HA_ROLE')
        yield XmlNodeCounterMetricFamily('genesys_sipserver_calls_created_total', root, './sipCallManager/NCALLSCREATED')
        yield XmlNodeGaugeMetricFamily('genesys_sipserver_calls', root, './sipCallManager/NCALLS')
        yield XmlNodeGaugeMetricFamily('genesys_sipserver_parties', root, './sipCallManager/NPARTIES')
        yield XmlNodeGaugeMetricFamily('genesys_sipserver_connections', root, './sipCallManager/NCONNECTIONS')
        yield XmlNodeGaugeMetricFamily('genesys_sipserver_operators', root, './sipCallManager/NOPERATIONS')
        yield XmlNodeGaugeMetricFamily('genesys_sipserver_music_services', root, './sipCallManager/NMUSICSERVICES')
        yield XmlNodeGaugeMetricFamily('genesys_sipserver_treatments', root, './sipCallManager/NTREATMENTS')
        yield XmlNodeGaugeMetricFamily('genesys_sipserver_greetings', root, './sipCallManager/NGREATINGS')
        yield XmlNodeGaugeMetricFamily('genesys_sipserver_recorders', root, './sipCallManager/NRECORDERS')
        yield XmlNodeGaugeMetricFamily('genesys_sipserver_mcu_channels', root, './sipCallManager/NMCUCHANNELS')
        yield XmlNodeCounterMetricFamily('genesys_sipserver_calls_abandoned_total', root, './sipCallManager/NCALLSABANDONED')
        yield XmlNodeGaugeMetricFamily('genesys_sipserver_logged_on_agents', root, './sipCallManager/NLOGGEDAGENTS')
        yield XmlNodeGaugeMetricFamily('genesys_sipserver_ntlibclients', root, './sipCallManager/NTLIBCLIENTS')
        yield XmlNodeGaugeMetricFamily('genesys_sipserver_nregistereddns', root, './sipCallManager/NREGISTEREDDNS') # Number of registered DNs Number of registered DNs by using a TRegisterAddress request.
        yield XmlNodeGaugeMetricFamily('genesys_sipserver_nsipregisteredep', root, './sipCallManager/NSIPREGISTEREDEP') # / Number of active SIP registrations
        yield XmlNodeGaugeMetricFamily('genesys_sipserver_nsipexpiredregs', root, './sipCallManager/NSIPEXPIREDREGS') # / Number of expired SIP registrations
        yield XmlNodeGaugeMetricFamily('genesys_sipserver_pm_nactive_registrations', root, './sipPresenceManager/PM_NACTIVE_REGISTRATIONS') # / Number of active registrations
        yield XmlNodeGaugeMetricFamily('genesys_sipserver_tl_ntransports', root, './sipTransportLayer/TL_NTRANSPORTS') # / Number of transports
        yield XmlNodeGaugeMetricFamily('genesys_sipserver_sips_process_id', root, './sipServer/SIPS_PROCESS_ID') # / Process identifier
        yield XmlNodeGaugeMetricFamily('genesys_sipserver_queue_main_cm', root, './sipServer/QUEUE_MAIN_CM') # / Queue Size Main>CM
        yield XmlNodeGaugeMetricFamily('genesys_sipserver_queue_cm_main', root, './sipServer/QUEUE_CM_MAIN') # / Queue Size CM>Main
        yield XmlNodeGaugeMetricFamily('genesys_sipserver_queue_from_trasnport', root, './sipServer/QUEUE_FROM_TRASNPORT') # / Queue Size From Transport
        yield XmlNodeGaugeMetricFamily('genesys_sipserver_queue_to_trasnport', root, './sipServer/QUEUE_TO_TRASNPORT') # / Queue Size To Transport
        yield XmlNodeGaugeMetricFamily('genesys_sipserver_readiness_switchover', root, './sipServer/READINESS_SWITCHOVER') # / Readiness For Switchover
        yield XmlNodeGaugeMetricFamily('genesys_sipserver_readiness_upgrade', root, './sipServer/READINESS_UPGRADE') # / Readiness For Upgrade
        yield XmlNodeGaugeMetricFamily('genesys_sipserver_num_sipps', root, './sipServer/NUM_SIPPS') # / Number of SIP Proxies available
        yield XmlNodeGaugeMetricFamily('genesys_sipserver_num_msmls', root, './sipServer/NUM_MSMLS') # / Number of Media Services available
        yield XmlNodeGaugeMetricFamily('genesys_sipserver_num_trunks', root, './sipServer/NUM_TRUNKS') # / Number of SIP TRUNKs available
        yield XmlNodeGaugeMetricFamily('genesys_sipserver_num_softswitches', root, './sipServer/NUM_SOFTSWITCHES') # / Number of SIP SOFTSWITCHs available
        yield XmlNodeGaugeMetricFamily('genesys_sipserver_ha_link', root, './sipServer/HA_LINK') # / HA link established
        yield XmlNodeGaugeMetricFamily('genesys_sipserver_connection_to_scs', root, './sipServer/CONNECTION_TO_SCS') # / Connection to SCS
        yield XmlNodeGaugeMetricFamily('genesys_sipserver_application_service', root, './sipServer/APPLICATION_SERVICE') # Application Service Available
        yield XmlNodeCounterMetricFamily('genesys_sipserver_call_recording_failed_total', root, './sipCallManager/NCALLRECORDINGFAILED')

        genesys_sipserver_trunk_calls = GaugeMetricFamily('genesys_sipserver_trunk_calls', 'Calls', labels=['app_name', 'app_version', 'app_ha_role','trunk_name'])
        genesys_sipserver_trunk_capacity = GaugeMetricFamily('genesys_sipserver_trunk_capacity', 'Capacity', labels=['app_name', 'app_version', 'app_ha_role','trunk_name'])
        genesys_sipserver_trunk_in_service = GaugeMetricFamily('genesys_sipserver_trunk_in_service', 'In Service', labels=['app_name', 'app_version', 'app_ha_role','trunk_name'])

        node_siptrunks = root.find('./sipTrunkStatistics/sipTrunkStatistics[@id="sipTrunkTable"]')
        for node_siptrunk_data in node_siptrunks.findall('./sipTrunkData'):
          trunk_name = node_siptrunk_data.find('./TRUNK').text
          in_service = (node_siptrunk_data.find('./IN_SERVICE').text == '1')
          genesys_sipserver_trunk_calls.add_metric(get_labels(root)+[trunk_name], node_siptrunk_data.find('./CURRENT_CALLS').text)
          genesys_sipserver_trunk_capacity.add_metric(get_labels(root)+[trunk_name], node_siptrunk_data.find('./CAPACITY').text)
          genesys_sipserver_trunk_in_service.add_metric(get_labels(root)+[trunk_name], in_service)

        yield genesys_sipserver_trunk_calls
        yield genesys_sipserver_trunk_capacity
        yield genesys_sipserver_trunk_in_service
