from conftest import *

@allure.epic('21:ECMP')
@allure.feature('21.3:ECMP балансировка IP трафика в L3VPN (IGP: OSPF)')
@allure.story('21.3.1:Базовая проверка функционала ECMP')
@allure.title('Проверка базового функционала ECMP')
@pytest.mark.part21_3
@pytest.mark.base_function_ECMP
@pytest.mark.dependency(depends=["load_config213_dut1","load_config213_dut2","load_config213_dut3"],scope='session')
@pytest.mark.parametrize("DUT",
			[
			 pytest.param(DUT1),
 			 pytest.param(DUT2), 
 			 pytest.param(DUT3)
			]
			)

def test_base_function_ECMP_part21_3(DUT):
    resp = ''
    conn = Telnet()
    acc = Account(DUT.login, DUT.password)
    conn.connect(DUT.host_ip)
    conn.login(acc)
    conn.set_prompt('#')

    cmd = 'show ospfv2 neighbors'
    conn.execute('config')
    conn.execute('no router equal-cost')
    conn.execute('commit')
    conn.execute('exit')
    conn.execute('terminal datadump')
    #time.sleep(15)
    conn.execute(cmd) 
    resp = conn.response
    allure.attach(resp, 'Вывод команды %s' % cmd, attachment_type=allure.attachment_type.TEXT)

    template = open('./templates/parse_show_ospfv2_neighbors_new.txt')
    fsm = textfsm.TextFSM(template)
    result = fsm.ParseTextToDicts(resp)
    
    if DUT.host_ip == DUT1.host_ip:
        time.sleep(15)
        ospf_neighbors = [
            [DUT2.loopback["ip_witout_mask"], '0.0.0.0', '1', 'full', 'not-required', '192.168.3.18', 'te0/0/1'],
            [DUT2.loopback["ip_witout_mask"], '0.0.0.0', '1', 'full', 'not-required', '192.168.3.22', 'te0/0/2'],
            [DUT3.loopback["ip_witout_mask"], '0.0.0.0', '1', 'full', 'not-required', '192.168.2.10', 'te0/0/3'],
            [DUT3.loopback["ip_witout_mask"], '0.0.0.0', '1', 'full', 'not-required', '192.168.2.13', 'te0/0/4']
        ]
        for i in range(4):
            assert_that(result[i]['nbr_id'] == ospf_neighbors[i][0], 'id соседа равен %s, а должен быть %s'%(result[i]['nbr_id'],ospf_neighbors[i][0]))
            assert_that(result[i]['nbr_area_id'] == ospf_neighbors[i][1], 'Ареа равна %s, а должен быть %s'%(result[i]['nbr_area_id'],ospf_neighbors[i][1]))
            assert_that(result[i]['nbr_priority'] == ospf_neighbors[i][2], 'Приоритет равен %s, а должен быть %s'%(result[i]['nbr_priority'],ospf_neighbors[i][2]))
            assert_that(result[i]['nbr_state'] == ospf_neighbors[i][3], 'Статус равен %s, а должен быть %s'%(result[i]['nbr_state'],ospf_neighbors[i][3]))
            assert_that(result[i]['nbr_bfd'] == ospf_neighbors[i][4], 'BFD равен %s, а должен быть %s'%(result[i]['nbr_bfd'],ospf_neighbors[i][4]))
            assert_that(result[i]['nbr_addr'] == ospf_neighbors[i][5], 'Адрес соседа равен %s, а должен быть %s'%(result[i]['nbr_addr'],ospf_neighbors[i][5]))
            assert_that(result[i]['nbr_int'] == ospf_neighbors[i][6], 'Интерфейс равен %s, а должен быть %s'%(result[i]['nbr_int'],ospf_neighbors[i][6]))

        conn.execute('show route vrf VRF40 192.168.73.0')
        resp = conn.response
        allure.attach(resp, 'Вывод команды show route vrf VRF40 192.168.73.0', attachment_type=allure.attachment_type.TEXT)
        with open('templates/parse_show_route_vrf_ipv4_ttp.txt', 'r') as t:
            template_ttp = t.read()
        parser = ttp(resp, template_ttp)
        parser.parse()
        result = parser.result()[0][0]

        assert_that(result['route_to_ipv4'] == "192.168.73.0/24", 'ip равен %s, а должен быть 192.168.73.0/24'%(result['route_to_ipv4']))
        assert_that(result['end'] == DUT2.loopback['ip_witout_mask'], f'ip равен %s, а должен быть {DUT2.loopback["ip"]}'%(result['route_to_ipv4']))
        assert_that(result['protocol'] == "bgp", 'protocol равен %s, а должен быть bgp'%(result['route_to_ipv4']))
        assert_that(result['type'] == "bgp-vpn", 'type равен %s, а должен быть bgp-vpn'%(result['route_to_ipv4']))
        assert_that(result['entries'] == "1", 'entries равен %s, а должен быть 1'%(result['route_to_ipv4']))

        route = [
            [DUT2.loopback['ip'],'192.168.3.18','te0/0/1','ospf','30','20','ospf-intra-area','none','remote'],
            [DUT2.loopback['ip'],'192.168.3.22',"te0/0/2",'ospf','30','20','ospf-intra-area','none','remote'],
            [DUT2.loopback['ip'],'192.168.2.10',"te0/0/3",'ospf','30','20','ospf-intra-area','none','remote'],
            [DUT2.loopback['ip'],'192.168.2.13',"te0/0/4",'ospf','30','20','ospf-intra-area','none','remote']
        ]
        l3forwarding = [
            [DUT2.loopback['ip'],'192.168.3.18',"Tengigabitethernet0/0/1",'e4:5a:d4:de:c8:81','e0:d9:e3:ff:48:87','0','0','1500','--','0xffffffff'],
            [DUT2.loopback['ip'],'192.168.3.22',"Tengigabitethernet0/0/2",'e4:5a:d4:de:c8:82','e0:d9:e3:ff:48:88','0','0','1500','--','0xffffffff'],
            [DUT2.loopback['ip'],'192.168.2.10',"Tengigabitethernet0/0/3",'e4:5a:d4:de:c8:83','a8:f9:4b:8b:92:ad','0','0','1500','23','0xffffffff'],
            [DUT2.loopback['ip'],'192.168.2.13',"Tengigabitethernet0/0/4",'e4:5a:d4:de:c8:84','a8:f9:4b:8b:92:ae','0','0','1500','23','0xffffffff']
        ]
        conn.execute('show route ' + DUT2.loopback['ip'])
        resp = conn.response
        with open('templates/parse_show_route_ipv4_ttp.txt', 'r') as t:
            template_ttp = t.read()
        parser = ttp(resp, template_ttp)
        parser.parse()
        result = parser.result()[0][0]
        
        j = 4
        for i in range(len(route)):
            if result['interface'] == route[i][2]:
                j = i
                break
        assert_that(j != 4, "Интерфейс должен быть %s или %s, а указан %s"%(route[0][2],route[1][2],result['interface']))

        assert_that(result['route_to_ipv4'] == route[j][0], 'ip равен %s, а должен быть %s'%(result['route_to_ipv4'],route[j][0]))
        assert_that(result['next_hop'] == route[j][1], 'next_hop равен %s, а должен быть %s'%(result['next_hop'],route[j][1]))
        assert_that(result['interface'] == route[j][2], 'интерфейс равен %s, а должен быть %s'%(result['interface'],route[j][2]))
        assert_that(result['protocol'] == route[j][3], 'Протокол указан %s, а должен быть %s'%(result['protocol'],route[j][3]))
        assert_that(result['dist'] == route[j][4], 'Дистанция равна %s, а должна быть %s'%(result['dist'],route[j][4]))
        assert_that(result['metric'] == route[j][5], 'Метрика равна %s, а должна быть %s'%(result['metric'],route[j][5]))
        assert_that(result['type'] == route[j][6], 'Тип маршрутизации указан %s, а должен быть %s'%(result['type'],route[j][6]))
        assert_that(result['protect'] == route[j][7], 'Тип указан %s, а должен быть %s'%(result['protect'],route[j][7]))
        assert_that(result['route_type'] == route[j][8], 'Защита указана %s, а должна быть %s'%(result['route_type'],route[j][8]))
        assert_that(result['entries'] == '1', 'Маршрутов указано %s, а должно быть 1'%result['entries'])

        conn.execute('show l3forwarding ' + DUT2.loopback['ip_witout_mask'])
        resp = conn.response
        allure.attach(resp, f'Вывод команды show l3forwarding {DUT2.loopback["ip"]} до router equal-cost', attachment_type=allure.attachment_type.TEXT)

        with open('templates/parse_show_l3forwarding_ttp.txt', 'r') as t:
            template_ttp2 = t.read()
        parser = ttp(resp, template_ttp2)
        parser.parse()
        result = parser.result()[0][0]

        assert_that(result['subnet'] == l3forwarding[j][0], 'ip равен %s, а должен быть %s'%(result['subnet'],l3forwarding[j][0]))
        assert_that(result['next_hop'] == l3forwarding[j][1], 'next_hop равен %s, а должен быть %s'%(result['next_hop'],l3forwarding[j][1]))
        assert_that(result['interface'] == l3forwarding[j][2], 'Интерфейс равен %s, а должен быть %s'%(result['interface'],l3forwarding[j][2]))
        assert_that(result['src_mac'] != "", 'src MAC равен %s, а должен быть %s'%(result['src_mac'],l3forwarding[j][3]))
        assert_that(result['dst_mac'] != "", 'dst MAC равен %s, а должен быть %s'%(result['dst_mac'],l3forwarding[j][4]))
        assert_that(result['Ovid'] == l3forwarding[j][5], 'Outer vid равен %s, а должен быть %s'%(result['Ovid'],l3forwarding[j][5]))
        assert_that(result['Ivid'] == l3forwarding[j][6], 'Inner vid равен %s, а должен быть %s'%(result['Ivid'],l3forwarding[j][6]))
        assert_that(result['mtu'] == l3forwarding[j][7], 'MTU равен %s, а должен быть %s'%(result['mtu'],l3forwarding[j][7]))
        
        conn.execute('config')
        conn.execute('router equal-cost')
        conn.execute('vrf VRF40')
        conn.execute('mpls')
        conn.execute('ecmp l3vpn')
        conn.execute('commit')
        time.sleep(5)


        for i in range(len(route)):
            route[i][7] = "ecmp"
            l3forwarding[i][9] = "0x20000002"

        conn.execute('do show route ' + DUT2.loopback['ip_witout_mask'])
        resp = conn.response
        allure.attach(resp, f'Вывод команды show route {DUT2.loopback["ip"]} после router equal-cost', attachment_type=allure.attachment_type.TEXT)

        parser = ttp(resp, template_ttp)
        parser.parse()
        result = parser.result()[0][0]
        for i in range(4):
            if result[i]['interface'] in route[0]:
                j = 0
            elif result[i]['interface'] in route[1]:
                j = 1
            elif result[i]['interface'] in route[2]:
                j = 2
            elif result[i]['interface'] in route[3]:
                j = 3
            else:
                assert_that(False, "Нету одного их этих интерфейсов %s, %s, %s или %s"%(route[0][2],route[1][2],route[2][2],route[3][2]))
            
            assert_that(result[i]['route_to_ipv4'] == route[j][0], 'ip равен %s, а должен быть %s'%(result[i]['route_to_ipv4'],route[j][0]))
            assert_that(result[i]['next_hop'] == route[j][1], 'next_hop равен %s, а должен быть %s'%(result[i]['next_hop'],route[j][1]))
            assert_that(result[i]['interface'] == route[j][2], 'интерфейс равен %s, а должен быть %s'%(result[i]['interface'],route[j][2]))
            assert_that(result[i]['protocol'] == route[j][3], 'Протокол указан %s, а должен быть %s'%(result[i]['protocol'],route[j][3]))
            assert_that(result[i]['dist'] == route[j][4], 'Дистанция равна %s, а должна быть %s'%(result[i]['dist'],route[j][4]))
            assert_that(result[i]['metric'] == route[j][5], 'Метрика равна %s, а должна быть %s'%(result[i]['metric'],route[j][5]))
            assert_that(result[i]['type'] == route[j][6], 'Тип маршрутизации указан %s, а должен быть %s'%(result[i]['type'],route[j][6]))
            assert_that(result[i]['protect'] == route[j][7], 'Тип указан %s, а должен быть %s'%(result[i]['protect'],route[j][7]))
            assert_that(result[i]['route_type'] == route[j][8], 'Защита указана %s, а должна быть %s'%(result[i]['route_type'],route[j][8]))
            
            route[j] = ""
        
        assert_that(result[3]['entries'] == '4', 'Маршрутов указано %s, а должно быть 4'%result[3]['entries'])
        
        conn.execute('end')
        conn.execute('show l3forwarding ' + DUT2.loopback['ip_witout_mask'])
        resp = conn.response
        allure.attach(resp, f'Вывод команды show l3forwarding {DUT2.loopback["ip"]} после router equal-cost', attachment_type=allure.attachment_type.TEXT)
        parser = ttp(resp, template_ttp2)
        parser.parse()
        result = parser.result()[0][0]
        for i in range(4):
            if result[i]['interface'] in l3forwarding[0]:
                j = 0
            elif result[i]['interface'] in l3forwarding[1]:
                j = 1
            elif result[i]['interface'] in l3forwarding[2]:
                j = 2
            elif result[i]['interface'] in l3forwarding[3]:
                j = 3
            else:
                assert_that(False, "Нету одного их этих интерфейсов %s, %s, %s или %s"%(route[0][2],route[1][2],route[2][2],route[3][2]))

            assert_that(result[i]['subnet'] == l3forwarding[j][0], 'ip равен %s, а должен быть %s'%(result[i]['subnet'],l3forwarding[j][0]))
            assert_that(result[i]['next_hop'] == l3forwarding[j][1], 'next_hop равен %s, а должен быть %s'%(result[i]['next_hop'],l3forwarding[j][1]))
            assert_that(result[i]['interface'] == l3forwarding[j][2], 'Интерфейс равен %s, а должен быть %s'%(result[i]['interface'],l3forwarding[j][2]))
            assert_that(result[i]['src_mac'] != "", 'src MAC равен %s, а должен быть %s'%(result[i]['src_mac'],l3forwarding[j][3]))
            assert_that(result[i]['dst_mac'] != "", 'dst MAC равен %s, а должен быть %s'%(result[i]['dst_mac'],l3forwarding[j][4]))
            assert_that(result[i]['Ovid'] == l3forwarding[j][5], 'Outer vid равен %s, а должен быть %s'%(result[i]['Ovid'],l3forwarding[j][5]))
            assert_that(result[i]['Ivid'] == l3forwarding[j][6], 'Inner vid равен %s, а должен быть %s'%(result[i]['Ivid'],l3forwarding[j][6]))
            assert_that(result[i]['mtu'] == l3forwarding[j][7], 'MTU равен %s, а должен быть %s'%(result[i]['mtu'],l3forwarding[j][7]))


    if DUT.host_ip == DUT2.host_ip:
        allure.attach.file('./network-schemes/part21_cli2_to_cli3.png','Схема теста:', attachment_type=allure.attachment_type.PNG)
        ospf_neighbors = [
            [DUT1.loopback['ip_witout_mask'], '0.0.0.0', '1', 'full', 'not-required', '192.168.3.17', 'te0/0/1'],
            [DUT1.loopback['ip_witout_mask'], '0.0.0.0', '1', 'full', 'not-required', '192.168.3.21', 'te0/0/2'],
            [DUT3.loopback['ip_witout_mask'], '0.0.0.0', '1', 'full', 'not-required', '192.168.1.13', 'te0/0/3'],
            [DUT3.loopback['ip_witout_mask'], '0.0.0.0', '1', 'full', 'not-required', '192.168.1.10', 'te0/0/4']
        ]
        for i in range(4):
            assert_that(result[i]['nbr_id'] == ospf_neighbors[i][0], 'id соседа равен %s, а должен быть %s'%(result[i]['nbr_id'],ospf_neighbors[i][0]))
            assert_that(result[i]['nbr_area_id'] == ospf_neighbors[i][1], 'Ареа равна %s, а должен быть %s'%(result[i]['nbr_area_id'],ospf_neighbors[i][1]))
            assert_that(result[i]['nbr_priority'] == ospf_neighbors[i][2], 'Приоритет равен %s, а должен быть %s'%(result[i]['nbr_priority'],ospf_neighbors[i][2]))
            assert_that(result[i]['nbr_state'] == ospf_neighbors[i][3], 'Статус равен %s, а должен быть %s'%(result[i]['nbr_state'],ospf_neighbors[i][3]))
            assert_that(result[i]['nbr_bfd'] == ospf_neighbors[i][4], 'BFD равен %s, а должен быть %s'%(result[i]['nbr_bfd'],ospf_neighbors[i][4]))
            assert_that(result[i]['nbr_addr'] == ospf_neighbors[i][5], 'Адрес соседа равен %s, а должен быть %s'%(result[i]['nbr_addr'],ospf_neighbors[i][5]))
            assert_that(result[i]['nbr_int'] == ospf_neighbors[i][6], 'Интерфейс равен %s, а должен быть %s'%(result[i]['nbr_int'],ospf_neighbors[i][6]))

        conn.execute('show route vrf VRF40 192.168.70.0')
        resp = conn.response
        allure.attach(resp, 'Вывод команды show route vrf VRF40 192.168.70.0', attachment_type=allure.attachment_type.TEXT)
        with open('templates/parse_show_route_vrf_ipv4_ttp.txt', 'r') as t:
            template_ttp = t.read()
        parser = ttp(resp, template_ttp)
        parser.parse()
        result = parser.result()[0][0]

        assert_that(result['route_to_ipv4'] == "192.168.70.0/24", 'ip равен %s, а должен быть 192.168.70.0/24'%(result['route_to_ipv4']))
        assert_that(result['end'] == DUT3.loopback['ip_witout_mask'], f'ip равен %s, а должен быть {DUT3.loopback["ip_witout_mask"]}'%(result['route_to_ipv4']))
        assert_that(result['protocol'] == "bgp", 'protocol равен %s, а должен быть bgp'%(result['route_to_ipv4']))
        assert_that(result['type'] == "bgp-vpn", 'type равен %s, а должен быть bgp-vpn'%(result['route_to_ipv4']))
        assert_that(result['entries'] == "1", 'entries равен %s, а должен быть 1'%(result['route_to_ipv4']))
        
        conn.execute(f'show route {DUT3.loopback["ip_witout_mask"]}')
        resp = conn.response
        allure.attach(resp, f'Вывод команды show route {DUT3.loopback["ip_witout_mask"]} до router equal-cost', attachment_type=allure.attachment_type.TEXT)

        route = [
            [DUT3.loopback['ip'],'192.168.1.13',"te0/0/3",'ospf','30','20','ospf-intra-area','none','remote'],
            [DUT3.loopback['ip'],'192.168.1.10',"te0/0/4",'ospf','30','20','ospf-intra-area','none','remote'],
            [DUT3.loopback['ip'],'192.168.3.17','te0/0/1','ospf','30','20','ospf-intra-area','none','remote'],
            [DUT3.loopback['ip'],'192.168.3.21',"te0/0/2",'ospf','30','20','ospf-intra-area','none','remote']
        ]
        l3forwarding = [
            [DUT3.loopback['ip'],'192.168.1.13',"Tengigabitethernet0/0/3",'e0:d9:e3:ff:48:83','a8:f9:4b:8b:93:83','0','0','1500','--','0xffffffff'],
            [DUT3.loopback['ip'],'192.168.1.10',"Tengigabitethernet0/0/4",'e0:d9:e3:ff:48:84','a8:f9:4b:8b:93:84','0','0','1500','--','0xffffffff'],
            [DUT3.loopback['ip'],'192.168.3.17',"Tengigabitethernet0/0/1",'e0:d9:e3:ff:48:87','e4:5a:d4:de:c8:81','0','0','1500','30','0xffffffff'],
            [DUT3.loopback['ip'],'192.168.3.21',"Tengigabitethernet0/0/2",'e0:d9:e3:ff:48:88','e4:5a:d4:de:c8:82','0','0','1500','30','0xffffffff']
        ]
        with open('templates/parse_show_route_ipv4_ttp.txt', 'r') as t:
            template_ttp = t.read()
        parser = ttp(resp, template_ttp)
        parser.parse()
        result = parser.result()[0][0]
        
        j = 4
        for i in range(len(route)):
            if result['interface'] == route[i][2]:
                j = i
                break
        assert_that(j != 4, "Интерфейс должен быть %s или %s, а указан %s"%(route[0][2],route[1][2],result['interface']))

        assert_that(result['route_to_ipv4'] == route[j][0], 'ip равен %s, а должен быть %s'%(result['route_to_ipv4'],route[j][0]))
        assert_that(result['next_hop'] == route[j][1], 'next_hop равен %s, а должен быть %s'%(result['next_hop'],route[j][1]))
        assert_that(result['interface'] == route[j][2], 'интерфейс равен %s, а должен быть %s'%(result['interface'],route[j][2]))
        assert_that(result['protocol'] == route[j][3], 'Протокол указан %s, а должен быть %s'%(result['protocol'],route[j][3]))
        assert_that(result['dist'] == route[j][4], 'Дистанция равна %s, а должна быть %s'%(result['dist'],route[j][4]))
        assert_that(result['metric'] == route[j][5], 'Метрика равна %s, а должна быть %s'%(result['metric'],route[j][5]))
        assert_that(result['type'] == route[j][6], 'Тип маршрутизации указан %s, а должен быть %s'%(result['type'],route[j][6]))
        assert_that(result['protect'] == route[j][7], 'Тип указан %s, а должен быть %s'%(result['protect'],route[j][7]))
        assert_that(result['route_type'] == route[j][8], 'Защита указана %s, а должна быть %s'%(result['route_type'],route[j][8]))
        assert_that(result['entries'] == '1', 'Маршрутов указано %s, а должно быть 1'%result['entries'])

        conn.execute(f'show l3forwarding {DUT3.loopback["ip_witout_mask"]}')
        resp = conn.response
        allure.attach(resp, f'Вывод команды show l3forwarding {DUT3.loopback["ip_witout_mask"]} до router equal-cost', attachment_type=allure.attachment_type.TEXT)

        with open('templates/parse_show_l3forwarding_ttp.txt', 'r') as t:
            template_ttp2 = t.read()
        parser = ttp(resp, template_ttp2)
        parser.parse()
        result = parser.result()[0][0]

        assert_that(result['subnet'] == l3forwarding[j][0], 'ip равен %s, а должен быть %s'%(result['subnet'],l3forwarding[j][0]))
        assert_that(result['next_hop'] == l3forwarding[j][1], 'next_hop равен %s, а должен быть %s'%(result['next_hop'],l3forwarding[j][1]))
        assert_that(result['interface'] == l3forwarding[j][2], 'Интерфейс равен %s, а должен быть %s'%(result['interface'],l3forwarding[j][2]))
        assert_that(result['src_mac'] != "", 'src MAC равен %s, а должен быть %s'%(result['src_mac'],l3forwarding[j][3]))
        assert_that(result['dst_mac'] != "", 'dst MAC равен %s, а должен быть %s'%(result['dst_mac'],l3forwarding[j][4]))
        assert_that(result['Ovid'] == l3forwarding[j][5], 'Outer vid равен %s, а должен быть %s'%(result['Ovid'],l3forwarding[j][5]))
        assert_that(result['Ivid'] == l3forwarding[j][6], 'Inner vid равен %s, а должен быть %s'%(result['Ivid'],l3forwarding[j][6]))
        assert_that(result['mtu'] == l3forwarding[j][7], 'MTU равен %s, а должен быть %s'%(result['mtu'],l3forwarding[j][7]))

        conn.execute('show hw-module maximum | include "Used|ECMP"')
        resp = conn.response
        allure.attach(resp, 'Вывод команды show hw-module maximum | include "Used|ECMP" до router equal-cost', attachment_type=allure.attachment_type.TEXT)

        with open('templates/parse_show_hw-module_maximum_ttp.txt', 'r') as t:
            template_ttp3 = t.read()
        parser = ttp(resp, template_ttp3)
        parser.parse()
        result = parser.result()[0][0]

        assert_that(result['used'] == '0', 'used равен %s, а должен быть 0'%result['used'])
        
        conn.execute('config')
        conn.execute('router equal-cost')
        conn.execute('vrf VRF40')
        conn.execute('mpls')
        conn.execute('ecmp l3vpn')
        conn.execute('commit')
        time.sleep(5)


        for i in range(len(route)):
            route[i][7] = "ecmp"
            l3forwarding[i][9] = "0x20000002"

        conn.execute(f'do show route {DUT3.loopback["ip_witout_mask"]}')
        resp = conn.response
        allure.attach(resp, f'Вывод команды show route {DUT3.loopback["ip_witout_mask"]} после router equal-cost', attachment_type=allure.attachment_type.TEXT)

        parser = ttp(resp, template_ttp)
        parser.parse()
        result = parser.result()[0][0]
        for i in range(4):
            if result[i]['interface'] in route[0]:
                j = 0
            elif result[i]['interface'] in route[1]:
                j = 1
            elif result[i]['interface'] in route[2]:
                j = 2
            elif result[i]['interface'] in route[3]:
                j = 3
            else:
                assert_that(False, "Нету одного их этих интерфейсов %s, %s, %s или %s"%(route[0][2],route[1][2],route[2][2],route[3][2]))
            
            assert_that(result[i]['route_to_ipv4'] == route[j][0], 'ip равен %s, а должен быть %s'%(result[i]['route_to_ipv4'],route[j][0]))
            assert_that(result[i]['next_hop'] == route[j][1], 'next_hop равен %s, а должен быть %s'%(result[i]['next_hop'],route[j][1]))
            assert_that(result[i]['interface'] == route[j][2], 'интерфейс равен %s, а должен быть %s'%(result[i]['interface'],route[j][2]))
            assert_that(result[i]['protocol'] == route[j][3], 'Протокол указан %s, а должен быть %s'%(result[i]['protocol'],route[j][3]))
            assert_that(result[i]['dist'] == route[j][4], 'Дистанция равна %s, а должна быть %s'%(result[i]['dist'],route[j][4]))
            assert_that(result[i]['metric'] == route[j][5], 'Метрика равна %s, а должна быть %s'%(result[i]['metric'],route[j][5]))
            assert_that(result[i]['type'] == route[j][6], 'Тип маршрутизации указан %s, а должен быть %s'%(result[i]['type'],route[j][6]))
            assert_that(result[i]['protect'] == route[j][7], 'Тип указан %s, а должен быть %s'%(result[i]['protect'],route[j][7]))
            assert_that(result[i]['route_type'] == route[j][8], 'Защита указана %s, а должна быть %s'%(result[i]['route_type'],route[j][8]))
            
            route[j] = ""
        
        assert_that(result[3]['entries'] == '4', 'Маршрутов указано %s, а должно быть 4'%result[3]['entries'])

        conn.execute(f'do show l3forwarding {DUT3.loopback["ip_witout_mask"]}')
        resp = conn.response
        allure.attach(resp, f'Вывод команды show l3forwarding {DUT3.loopback["ip_witout_mask"]} после router equal-cost', attachment_type=allure.attachment_type.TEXT)
        parser = ttp(resp, template_ttp2)
        parser.parse()
        result = parser.result()[0][0]

        for i in range(4):
            if result[i]['interface'] in l3forwarding[0]:
                j = 0
            elif result[i]['interface'] in l3forwarding[1]:
                j = 1
            elif result[i]['interface'] in l3forwarding[2]:
                j = 2
            elif result[i]['interface'] in l3forwarding[3]:
                j = 3
            else:
                assert_that(False, "Нету одного их этих интерфейсов %s, %s, %s или %s"%(route[0][2],route[1][2],route[2][2],route[3][2]))

            assert_that(result[i]['subnet'] == l3forwarding[j][0], 'ip равен %s, а должен быть %s'%(result[i]['subnet'],l3forwarding[j][0]))
            assert_that(result[i]['next_hop'] == l3forwarding[j][1], 'next_hop равен %s, а должен быть %s'%(result[i]['next_hop'],l3forwarding[j][1]))
            assert_that(result[i]['interface'] == l3forwarding[j][2], 'Интерфейс равен %s, а должен быть %s'%(result[i]['interface'],l3forwarding[j][2]))
            assert_that(result[i]['src_mac'] != "", 'src MAC равен %s, а должен быть %s'%(result[i]['src_mac'],l3forwarding[j][3]))
            assert_that(result[i]['dst_mac'] != "", 'dst MAC равен %s, а должен быть %s'%(result[i]['dst_mac'],l3forwarding[j][4]))
            assert_that(result[i]['Ovid'] == l3forwarding[j][5], 'Outer vid равен %s, а должен быть %s'%(result[i]['Ovid'],l3forwarding[j][5]))
            assert_that(result[i]['Ivid'] == l3forwarding[j][6], 'Inner vid равен %s, а должен быть %s'%(result[i]['Ivid'],l3forwarding[j][6]))
            assert_that(result[i]['mtu'] == l3forwarding[j][7], 'MTU равен %s, а должен быть %s'%(result[i]['mtu'],l3forwarding[j][7]))



    if DUT.host_ip == DUT3.host_ip:
        allure.attach.file('./network-schemes/part21_cli3_to_cli1.png','Схема теста:', attachment_type=allure.attachment_type.PNG)
        ospf_neighbors = [
            [DUT1.loopback['ip_witout_mask'], '0.0.0.0', '1', 'full', 'not-required', '192.168.2.9', 'te0/0/1'],
            [DUT1.loopback['ip_witout_mask'], '0.0.0.0', '1', 'full', 'not-required', '192.168.2.14', 'te0/0/2'],
            [DUT2.loopback['ip_witout_mask'], '0.0.0.0', '1', 'full', 'not-required', '192.168.1.14', 'te0/0/3'],
            [DUT2.loopback['ip_witout_mask'], '0.0.0.0', '1', 'full', 'not-required', '192.168.1.9', 'te0/0/4']
        ]
        for i in range(4):
            assert_that(result[i]['nbr_id'] == ospf_neighbors[i][0], 'id соседа равен %s, а должен быть %s'%(result[i]['nbr_id'],ospf_neighbors[i][0]))
            assert_that(result[i]['nbr_area_id'] == ospf_neighbors[i][1], 'Ареа равна %s, а должен быть %s'%(result[i]['nbr_area_id'],ospf_neighbors[i][1]))
            assert_that(result[i]['nbr_priority'] == ospf_neighbors[i][2], 'Приоритет равен %s, а должен быть %s'%(result[i]['nbr_priority'],ospf_neighbors[i][2]))
            assert_that(result[i]['nbr_state'] == ospf_neighbors[i][3], 'Статус равен %s, а должен быть %s'%(result[i]['nbr_state'],ospf_neighbors[i][3]))
            assert_that(result[i]['nbr_bfd'] == ospf_neighbors[i][4], 'BFD равен %s, а должен быть %s'%(result[i]['nbr_bfd'],ospf_neighbors[i][4]))
            assert_that(result[i]['nbr_addr'] == ospf_neighbors[i][5], 'Адрес соседа равен %s, а должен быть %s'%(result[i]['nbr_addr'],ospf_neighbors[i][5]))
            assert_that(result[i]['nbr_int'] == ospf_neighbors[i][6], 'Интерфейс равен %s, а должен быть %s'%(result[i]['nbr_int'],ospf_neighbors[i][6]))

        conn.execute('show route vrf VRF40 192.168.74.0')
        resp = conn.response
        allure.attach(resp, 'Вывод команды show route vrf VRF40 192.168.74.0', attachment_type=allure.attachment_type.TEXT)
        with open('templates/parse_show_route_vrf_ipv4_ttp.txt', 'r') as t:
            template_ttp = t.read()
        parser = ttp(resp, template_ttp)
        parser.parse()
        result = parser.result()[0][0]

        assert_that(result['route_to_ipv4'] == "192.168.74.0/24", 'ip равен %s, а должен быть 192.168.74.0/24'%(result['route_to_ipv4']))
        assert_that(result['end'] == DUT1.loopback['ip_witout_mask'], f'ip равен %s, а должен быть {DUT1.loopback["ip_witout_mask"]}'%(result['route_to_ipv4']))
        assert_that(result['protocol'] == "bgp", 'protocol равен %s, а должен быть bgp'%(result['route_to_ipv4']))
        assert_that(result['type'] == "bgp-vpn", 'type равен %s, а должен быть bgp-vpn'%(result['route_to_ipv4']))
        assert_that(result['entries'] == "1", 'entries равен %s, а должен быть 1'%(result['route_to_ipv4']))

        conn.execute(f'show route {DUT1.loopback["ip_witout_mask"]}')
        resp = conn.response
        allure.attach(resp, f'Вывод команды show route {DUT1.loopback["ip_witout_mask"]} до router equal-cost', attachment_type=allure.attachment_type.TEXT)

        route = [
            [DUT1.loopback['ip'],'192.168.1.14',"te0/0/3",'ospf','30','20','ospf-intra-area','none','remote'],
            [DUT1.loopback['ip'],'192.168.1.9',"te0/0/4",'ospf','30','20','ospf-intra-area','none','remote'],
            [DUT1.loopback['ip'],'192.168.2.9','te0/0/1','ospf','30','20','ospf-intra-area','none','remote'],
            [DUT1.loopback['ip'],'192.168.2.14',"te0/0/2",'ospf','30','20','ospf-intra-area','none','remote']
        ]
        l3forwarding = [
            [DUT1.loopback['ip'],'192.168.1.14',"Tengigabitethernet0/0/3",'a8:f9:4b:8b:93:83','e0:d9:e3:ff:48:83','0','0','1500','24','0xffffffff'],
            [DUT1.loopback['ip'],'192.168.1.9',"Tengigabitethernet0/0/4",'a8:f9:4b:8b:93:84','e0:d9:e3:ff:48:84','0','0','1500','24','0xffffffff'],
            [DUT1.loopback['ip'],'192.168.2.9',"Tengigabitethernet0/0/1",'a8:f9:4b:8b:92:ad','e4:5a:d4:de:c8:83','0','0','1500','--','0xffffffff'],
            [DUT1.loopback['ip'],'192.168.2.14',"Tengigabitethernet0/0/2",'a8:f9:4b:8b:92:ae','e4:5a:d4:de:c8:84','0','0','1500','--','0xffffffff']            
        ]
        with open('templates/parse_show_route_ipv4_ttp.txt', 'r') as t:
            template_ttp = t.read()
        parser = ttp(resp, template_ttp)
        parser.parse()
        result = parser.result()[0][0]
        
        j = 4
        for i in range(len(route)):
            if result['interface'] == route[i][2]:
                j = i
                break
        assert_that(j != 4, "Интерфейс должен быть %s или %s, а указан %s"%(route[0][2],route[1][2],result['interface']))

        assert_that(result['route_to_ipv4'] == route[j][0], 'ip равен %s, а должен быть %s'%(result['route_to_ipv4'],route[j][0]))
        assert_that(result['next_hop'] == route[j][1], 'next_hop равен %s, а должен быть %s'%(result['next_hop'],route[j][1]))
        assert_that(result['interface'] == route[j][2], 'интерфейс равен %s, а должен быть %s'%(result['interface'],route[j][2]))
        assert_that(result['protocol'] == route[j][3], 'Протокол указан %s, а должен быть %s'%(result['protocol'],route[j][3]))
        assert_that(result['dist'] == route[j][4], 'Дистанция равна %s, а должна быть %s'%(result['dist'],route[j][4]))
        assert_that(result['metric'] == route[j][5], 'Метрика равна %s, а должна быть %s'%(result['metric'],route[j][5]))
        assert_that(result['type'] == route[j][6], 'Тип маршрутизации указан %s, а должен быть %s'%(result['type'],route[j][6]))
        assert_that(result['protect'] == route[j][7], 'Тип указан %s, а должен быть %s'%(result['protect'],route[j][7]))
        assert_that(result['route_type'] == route[j][8], 'Защита указана %s, а должна быть %s'%(result['route_type'],route[j][8]))
        assert_that(result['entries'] == '1', 'Маршрутов указано %s, а должно быть 1'%result['entries'])

        conn.execute(f'show l3forwarding {DUT1.loopback["ip_witout_mask"]}')
        resp = conn.response
        allure.attach(resp, f'Вывод команды show l3forwarding {DUT1.loopback["ip_witout_mask"]} до router equal-cost', attachment_type=allure.attachment_type.TEXT)

        with open('templates/parse_show_l3forwarding_ttp.txt', 'r') as t:
            template_ttp2 = t.read()
        parser = ttp(resp, template_ttp2)
        parser.parse()
        result = parser.result()[0][0]

        assert_that(result['subnet'] == l3forwarding[j][0], 'ip равен %s, а должен быть %s'%(result['subnet'],l3forwarding[j][0]))
        assert_that(result['next_hop'] == l3forwarding[j][1], 'next_hop равен %s, а должен быть %s'%(result['next_hop'],l3forwarding[j][1]))
        assert_that(result['interface'] == l3forwarding[j][2], 'Интерфейс равен %s, а должен быть %s'%(result['interface'],l3forwarding[j][2]))
        assert_that(result['src_mac'] != "", 'src MAC равен %s, а должен быть %s'%(result['src_mac'],l3forwarding[j][3]))
        assert_that(result['dst_mac'] != "", 'dst MAC равен %s, а должен быть %s'%(result['dst_mac'],l3forwarding[j][4]))
        assert_that(result['Ovid'] == l3forwarding[j][5], 'Outer vid равен %s, а должен быть %s'%(result['Ovid'],l3forwarding[j][5]))
        assert_that(result['Ivid'] == l3forwarding[j][6], 'Inner vid равен %s, а должен быть %s'%(result['Ivid'],l3forwarding[j][6]))
        assert_that(result['mtu'] == l3forwarding[j][7], 'MTU равен %s, а должен быть %s'%(result['mtu'],l3forwarding[j][7]))
        
        conn.execute('config')
        conn.execute('router equal-cost')
        conn.execute('vrf VRF40')
        conn.execute('mpls')
        conn.execute('ecmp l3vpn')
        conn.execute('commit')
        time.sleep(5)


        for i in range(len(route)):
            route[i][7] = "ecmp"
            l3forwarding[i][9] = "0x20000002"

        conn.execute(f'do show route {DUT1.loopback["ip_witout_mask"]}')
        resp = conn.response
        allure.attach(resp, f'Вывод команды show route {DUT1.loopback["ip_witout_mask"]} после router equal-cost', attachment_type=allure.attachment_type.TEXT)

        parser = ttp(resp, template_ttp)
        parser.parse()
        result = parser.result()[0][0]
        for i in range(4):
            if result[i]['interface'] in route[0]:
                j = 0
            elif result[i]['interface'] in route[1]:
                j = 1
            elif result[i]['interface'] in route[2]:
                j = 2
            elif result[i]['interface'] in route[3]:
                j = 3
            else:
                assert_that(False, "Нету одного их этих интерфейсов %s, %s, %s или %s"%(route[0][2],route[1][2],route[2][2],route[3][2]))
            
            assert_that(result[i]['route_to_ipv4'] == route[j][0], 'ip равен %s, а должен быть %s'%(result[i]['route_to_ipv4'],route[j][0]))
            assert_that(result[i]['next_hop'] == route[j][1], 'next_hop равен %s, а должен быть %s'%(result[i]['next_hop'],route[j][1]))
            assert_that(result[i]['interface'] == route[j][2], 'интерфейс равен %s, а должен быть %s'%(result[i]['interface'],route[j][2]))
            assert_that(result[i]['protocol'] == route[j][3], 'Протокол указан %s, а должен быть %s'%(result[i]['protocol'],route[j][3]))
            assert_that(result[i]['dist'] == route[j][4], 'Дистанция равна %s, а должна быть %s'%(result[i]['dist'],route[j][4]))
            assert_that(result[i]['metric'] == route[j][5], 'Метрика равна %s, а должна быть %s'%(result[i]['metric'],route[j][5]))
            assert_that(result[i]['type'] == route[j][6], 'Тип маршрутизации указан %s, а должен быть %s'%(result[i]['type'],route[j][6]))
            assert_that(result[i]['protect'] == route[j][7], 'Тип указан %s, а должен быть %s'%(result[i]['protect'],route[j][7]))
            assert_that(result[i]['route_type'] == route[j][8], 'Защита указана %s, а должна быть %s'%(result[i]['route_type'],route[j][8]))
            
            route[j] = ""
        
        assert_that(result[3]['entries'] == '4', 'Маршрутов указано %s, а должно быть 4'%result[3]['entries'])

        conn.execute(f'do show l3forwarding {DUT1.loopback["ip_witout_mask"]}')
        resp = conn.response
        allure.attach(resp, f'Вывод команды show l3forwarding {DUT1.loopback["ip_witout_mask"]} после router equal-cost', attachment_type=allure.attachment_type.TEXT)
        parser = ttp(resp, template_ttp2)
        parser.parse()
        result = parser.result()[0][0]

        for i in range(4):
            if result[i]['interface'] in l3forwarding[0]:
                j = 0
            elif result[i]['interface'] in l3forwarding[1]:
                j = 1
            elif result[i]['interface'] in l3forwarding[2]:
                j = 2
            elif result[i]['interface'] in l3forwarding[3]:
                j = 3
            else:
                assert_that(False, "Нету одного их этих интерфейсов %s, %s, %s или %s"%(route[0][2],route[1][2],route[2][2],route[3][2]))

            assert_that(result[i]['subnet'] == l3forwarding[j][0], 'ip равен %s, а должен быть %s'%(result[i]['subnet'],l3forwarding[j][0]))
            assert_that(result[i]['next_hop'] == l3forwarding[j][1], 'next_hop равен %s, а должен быть %s'%(result[i]['next_hop'],l3forwarding[j][1]))
            assert_that(result[i]['interface'] == l3forwarding[j][2], 'Интерфейс равен %s, а должен быть %s'%(result[i]['interface'],l3forwarding[j][2]))
            assert_that(result[i]['src_mac'] != "", 'src MAC равен %s, а должен быть %s'%(result[i]['src_mac'],l3forwarding[j][3]))
            assert_that(result[i]['dst_mac'] != "", 'dst MAC равен %s, а должен быть %s'%(result[i]['dst_mac'],l3forwarding[j][4]))
            assert_that(result[i]['Ovid'] == l3forwarding[j][5], 'Outer vid равен %s, а должен быть %s'%(result[i]['Ovid'],l3forwarding[j][5]))
            assert_that(result[i]['Ivid'] == l3forwarding[j][6], 'Inner vid равен %s, а должен быть %s'%(result[i]['Ivid'],l3forwarding[j][6]))
            assert_that(result[i]['mtu'] == l3forwarding[j][7], 'MTU равен %s, а должен быть %s'%(result[i]['mtu'],l3forwarding[j][7]))