from conftest import *


@allure.epic('00:Загрузка начальной конфигурации')
@allure.feature('Часть 21.3')
@allure.story('Загрузка конфигурации на ME маршрутизатор')
@allure.title('Загрузка конфигурации на ME маршрутизатор')
@pytest.mark.part21_3
@pytest.mark.init_config21_3
@pytest.mark.parametrize("DUT",
			[
			 pytest.param(DUT1, marks=pytest.mark.dependency(name="load_config213_dut1",scope="session")), 
 			 pytest.param(DUT2, marks=pytest.mark.dependency(name="load_config213_dut2",scope="session")), 
 			 pytest.param(DUT3, marks=pytest.mark.dependency(name="load_config213_dut3",scope="session"))
			]
			)
                              
def test_me_init_config_upload_part21_3(DUT):
# В данном тесте будем загружать начальную конфигурацию на ME маршрутизаторы для тестов из Части 21.3 документа   
   DUT.connection()
   DUT.startup()
   DUT.hash_field("ip","dst")
   DUT.hash_field("ip","src")
   DUT.hash_field("port","dst")
   DUT.hash_field("port","src")
   DUT.ospf_custom('0.0.0.0','te0/0/1')
   DUT.ospf_custom('0.0.0.0','te0/0/2')
   DUT.ospf_custom('0.0.0.0','te0/0/3')
   DUT.ospf_custom('0.0.0.0','te0/0/4')
   DUT.ospf_redistribution()
   DUT.mpls_custom('te0/0/1')
   DUT.mpls_custom('te0/0/2')
   DUT.mpls_custom('te0/0/3')
   DUT.mpls_custom('te0/0/4')
   DUT.ldp_custom('te0/0/1')
   DUT.ldp_custom('te0/0/2')
   DUT.ldp_custom('te0/0/3')
   DUT.ldp_custom('te0/0/4')
   DUT.loopback_ipv4()
   DUT.vrf_add('VRF40','100:40','100:40','100:40')
   DUT.bgp_add()
   DUT.bgp_redistribution("65100","ipv4","unicast","1","static","redist_static","VRF40")
   if DUT.hostname == DUT1.hostname:
      DUT.ip_custom('ipv4','te0/0/1','192.168.3.17/30')
      DUT.ip_custom('ipv4','te0/0/2','192.168.3.21/30')
      DUT.ip_custom('ipv4','te0/0/3','192.168.2.9/30')
      DUT.ip_custom('ipv4','te0/0/4','192.168.2.14/30')
      DUT.double_subint('te0/0/11.10074','100','74','192.168.74.1/24','VRF40')
      DUT.double_subint('te0/0/11.100174','100','174','192.168.174.1/24','VRF40')
      DUT.ospf_metric('0.0.0.0','te0/0/1','20')
      DUT.ospf_metric('0.0.0.0','te0/0/2','20')
      DUT.ospf_metric('0.0.0.0','te0/0/3','10')
      DUT.ospf_metric('0.0.0.0','te0/0/4','10')
   elif DUT.hostname == DUT2.hostname:
      DUT.ip_custom('ipv4','te0/0/1','192.168.3.18/30')
      DUT.ip_custom('ipv4','te0/0/2','192.168.3.22/30')
      DUT.ip_custom('ipv4','te0/0/3','192.168.1.14/30')
      DUT.ip_custom('ipv4','te0/0/4','192.168.1.9/30')
      DUT.double_subint('te0/0/11.10073','100','73','192.168.73.1/24','VRF40')
      DUT.double_subint('te0/0/11.100173','100','173','192.168.173.1/24','VRF40')
      DUT.ospf_metric('0.0.0.0','te0/0/1','10')
      DUT.ospf_metric('0.0.0.0','te0/0/2','10')
      DUT.ospf_metric('0.0.0.0','te0/0/3','20')
      DUT.ospf_metric('0.0.0.0','te0/0/4','20')
   elif DUT.hostname == DUT3.hostname:
      DUT.ip_custom('ipv4','te0/0/1','192.168.2.10/30')
      DUT.ip_custom('ipv4','te0/0/2','192.168.2.13/30')
      DUT.ip_custom('ipv4','te0/0/3','192.168.1.13/30')
      DUT.ip_custom('ipv4','te0/0/4','192.168.1.10/30')
      DUT.double_subint('te0/0/5.10070','100','70','192.168.70.1/24','VRF40')
      DUT.double_subint('te0/0/5.100170','100','170','192.168.170.1/24','VRF40')
      DUT.ospf_metric('0.0.0.0','te0/0/1','20')
      DUT.ospf_metric('0.0.0.0','te0/0/2','20')
      DUT.ospf_metric('0.0.0.0','te0/0/3','10')
      DUT.ospf_metric('0.0.0.0','te0/0/4','10')
   DUT.close()