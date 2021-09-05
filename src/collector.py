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
        yield XmlNodeGaugeMetricFamily('genesys_sipserver_tlib_clients', root, './sipCallManager/NTLIBCLIENTS')
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
