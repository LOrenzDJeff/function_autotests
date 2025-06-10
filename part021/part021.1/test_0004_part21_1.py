from conftest import *

@pytest.fixture(scope='function')
def ecmp_turn_on(host_ip, hostname, login, password):
    conn = Telnet()
    acc = Account(login, password)
    conn.connect(host_ip)
    conn.login(acc)
    conn.set_prompt('#')
    conn.execute('config')
    conn.execute('router equal-cost')
    conn.set_prompt('#')
    conn.execute('commit')
    conn.execute("end")
    yield

@pytest.mark.part21_1
@pytest.mark.base_function_ECMP
@allure.epic('21:ECMP')
@allure.feature('21.1:ECMP балансировка IP трафика в GRT (IGP: ISIS)')
@allure.story('21.1.2:Тестирование функционала балансировки IGP: ISIS трафика между интерфейсами')
@allure.title('Проверка балансировки IGP: ISIS трафика между интерфейсами')
@pytest.mark.dependency(depends=["load_config211_dut1","load_config211_dut2","load_config211_dut3"],scope='session')
@pytest.mark.parametrize('DUT, ip_iperf_server, vrf_cli, vrf_cli2', 
                         [(DUT1, '192.168.73.10', 'CE1', 'CE11'),
                          (DUT2, '192.168.70.10', 'CE2', 'CE12'),
                          (DUT3, '192.168.74.10', 'CE3', 'CE13')])

def test_ECMP_isis_balance_21_1(DUT, ip_iperf_server, vrf_cli, vrf_cli2):
    estimated_duration_time=40
    if DUT.host_ip == DUT1.host_ip:
        allure.attach.file('./network-schemes/part21_cli1_to_cli2.png','Схема теста:', attachment_type=allure.attachment_type.PNG)
    elif DUT.host_ip == DUT2.host_ip:
        allure.attach.file('./network-schemes/part21_cli2_to_cli3.png','Схема теста:', attachment_type=allure.attachment_type.PNG)
    else:
        allure.attach.file('./network-schemes/part21_cli3_to_cli1.png','Схема теста:', attachment_type=allure.attachment_type.PNG)

    start_traffic_gen=time.time() # Фиксируем время начала генерации трафика
    x=thread_with_trace(target=start_udp_esr_iperf3_server_client_queue,args=(ip_iperf_server,estimated_duration_time , '100M', vrf_cli))
    y=thread_with_trace(target=start_udp_esr_iperf3_server_client_queue,args=(ip_iperf_server,estimated_duration_time , '100M', vrf_cli2))
    x.start() # Запускаем iperf клиент и сервер в докер-контейнерах
    y.start()

    conn = Telnet()
    acc = Account(DUT.login, DUT.password)
    conn.connect(DUT.host_ip)
    conn.login(acc)
    conn.set_prompt('#')
    conn.execute('terminal datadump')
    time.sleep(30) # Ждем пока накопится статистика на интерфейсах 
    cmd=('show interfaces utilization | incl " 20 | Interf"')
    conn.execute(cmd)
    resp = conn.response
    allure.attach(resp, 'Вывод команды %s'%cmd, attachment_type=allure.attachment_type.TEXT)     
#    print(resp)
    template = open('./templates/parse_show_int_utilization.txt')
    fsm = textfsm.TextFSM(template)
    processed_result=fsm.ParseTextToDicts(resp)
    print(processed_result) # Раскомментируй чтобы посмотреть результат парсинга

    while x.is_alive() and y.is_alive():
        curr_seconds=time.time()
        duration_time=curr_seconds-start_traffic_gen
        time.sleep(2)
        if duration_time>estimated_duration_time:        
            x.kill()
            y.kill()
            print("Timeout - %d sec"%estimated_duration_time)   
      
    x.join() # Подождем пока генерация трафика не закончится, иначе могут начаться другие тесты а этот по сути ещё не окончился....
    y.join()

    number_of_elements = len(processed_result)
    assert_that(number_of_elements==4, "Кол-во элементов в списке processed_result не соответствует ожидаемым 4, а равно - %d" %number_of_elements)

    int1_name=processed_result[0]['Int_name']
    int1_send=processed_result[0]['Int_send']

    int2_name=processed_result[1]['Int_name']
    int2_send=processed_result[1]['Int_send']

    int3_name=processed_result[2]['Int_name']
    int3_send=processed_result[2]['Int_send']

    int4_name=processed_result[3]['Int_name']
    int4_send=processed_result[3]['Int_send']

    assert_that(int1_name=="te0/0/1","В выводе команды %s имя первого интерфейса не равно ожидаемому значению te0/0/1, а равно - %s"%(cmd,int1_name))
    assert_that(int2_name=="te0/0/2","В выводе команды %s имя второго интерфейса не равно ожидаемому значению te0/0/2, а равно - %s"%(cmd,int2_name))
    assert_that(int3_name=="te0/0/3","В выводе команды %s имя третьего интерфейса не равно ожидаемому значению te0/0/3, а равно - %s"%(cmd,int3_name))
    assert_that(int4_name=="te0/0/4","В выводе команды %s имя четвёртого интерфейса не равно ожидаемому значению te0/0/4, а равно - %s"%(cmd,int4_name))

    assert_that(int(int1_send)>10,"%s: На интерфейсе %s отсутствует исходящий трафик"%(DUT.hostname,int1_name))
    assert_that(int(int2_send)>10,"%s: На интерфейсе %s отсутствует исходящий трафик"%(DUT.hostname,int2_name))
    assert_that(int(int3_send)>10,"%s: На интерфейсе %s отсутствует исходящий трафик"%(DUT.hostname,int3_name))
    assert_that(int(int4_send)>10,"%s: На интерфейсе %s отсутствует исходящий трафик"%(DUT.hostname,int4_name))


    delta1_send=round((abs((int(int1_send) / (int(int1_send) + int(int2_send) + int(int3_send) + int(int4_send))) - 0.25))*100)
    delta2_send=round((abs((int(int2_send) / (int(int1_send) + int(int2_send) + int(int3_send) + int(int4_send))) - 0.25))*100)
    delta3_send=round((abs((int(int3_send) / (int(int1_send) + int(int2_send) + int(int3_send) + int(int4_send))) - 0.25))*100)
    delta4_send=round((abs((int(int4_send) / (int(int1_send) + int(int2_send) + int(int3_send) + int(int4_send))) - 0.25))*100)

    assert_that(delta1_send<=50,"%s: Балансировка IP трафика в %s очень плохая т.к. отклонение равно или превысило 50%% и равно - %d%%"%(DUT.hostname,int1_name,delta1_send))
    assert_that(delta1_send<=40,"%s: Балансировка IP трафика в %s плохая т.к. отклонение равно или превысило 40%% и равно - %d%%"%(DUT.hostname,int1_name,delta1_send))
    #assert_that(delta1_send<=30,"%s: Балансировка IP трафика в %s средняя т.к. отклонение равно или превысило 30%% и равно - %d%%"%(DUT.hostname,int1_name,delta1_send))
    #assert_that(delta1_send<=20,"%s: Балансировка IP трафика в %s нормальная т.к. отклонение равно или превысило 20%% и равно - %d%%"%(DUT.hostname,int1_name,delta1_send))
    #assert_that(delta1_send<=15,"%s: Балансировка IP трафика в %s приемлемая т.к. отклонение равно или превысило 15%% и равно - %d%%"%(DUT.hostname,int1_name,delta1_send))

    assert_that(delta2_send<=50,"%s: Балансировка IP трафика в %s очень плохая т.к. отклонение равно или превысило 50%% и равно - %d%%"%(DUT.hostname,int2_name,delta2_send))
    assert_that(delta2_send<=40,"%s: Балансировка IP трафика в %s плохая т.к. отклонение равно или превысило 40%% и равно - %d%%"%(DUT.hostname,int2_name,delta2_send))
    #assert_that(delta2_send<=30,"%s: Балансировка IP трафика в %s средняя т.к. отклонение равно или превысило 30%% и равно - %d%%"%(DUT.hostname,int2_name,delta2_send))
    #assert_that(delta2_send<=20,"%s: Балансировка IP трафика в %s нормальная т.к. отклонение равно или превысило 20%% и равно - %d%%"%(DUT.hostname,int2_name,delta2_send))
    #assert_that(delta2_send<=15,"%s: Балансировка IP трафика в %s приемлемая т.к. отклонение равно или превысило 15%% и равно - %d%%"%(DUT.hostname,int2_name,delta2_send))

    assert_that(delta3_send<=50,"%s: Балансировка IP трафика в %s очень плохая т.к. отклонение равно или превысило 50%% и равно - %d%%"%(DUT.hostname,int3_name,delta3_send))
    assert_that(delta3_send<=40,"%s: Балансировка IP трафика в %s плохая т.к. отклонение равно или превысило 40%% и равно - %d%%"%(DUT.hostname,int3_name,delta3_send))
    #assert_that(delta3_send<=30,"%s: Балансировка IP трафика в %s средняя т.к. отклонение равно или превысило 30%% и равно - %d%%"%(DUT.hostname,int3_name,delta3_send))
    #assert_that(delta3_send<=20,"%s: Балансировка IP трафика в %s нормальная т.к. отклонение равно или превысило 20%% и равно - %d%%"%(DUT.hostname,int3_name,delta3_send))
    #assert_that(delta3_send<=15,"%s: Балансировка IP трафика в %s приемлемая т.к. отклонение равно или превысило 15%% и равно - %d%%"%(DUT.hostname,int3_name,delta3_send))

    assert_that(delta4_send<=50,"%s: Балансировка IP трафика в %s очень плохая т.к. отклонение равно или превысило 50%% и равно - %d%%"%(DUT.hostname,int4_name,delta4_send))
    assert_that(delta4_send<=40,"%s: Балансировка IP трафика в %s плохая т.к. отклонение равно или превысило 40%% и равно - %d%%"%(DUT.hostname,int4_name,delta4_send))
    #assert_that(delta4_send<=30,"%s: Балансировка IP трафика в %s средняя т.к. отклонение равно или превысило 30%% и равно - %d%%"%(DUT.hostname,int4_name,delta4_send))
    #assert_that(delta4_send<=20,"%s: Балансировка IP трафика в %s нормальная т.к. отклонение равно или превысило 20%% и равно - %d%%"%(DUT.hostname,int4_name,delta4_send))
    #assert_that(delta4_send<=15,"%s: Балансировка IP трафика в %s приемлемая т.к. отклонение равно или превысило 15%% и равно - %d%%"%(DUT.hostname,int4_name,delta4_send))
    
    if delta1_send>=30:
        allure.attach("Балансировка IP трафика в %s средняя т.к. отклонение равно или превысило 30%% и равно - %d%%"%(int1_name,delta1_send),"Процент отклонения в %s"%int1_name, attachment_type=allure.attachment_type.TEXT)
    elif delta1_send>=20:
        allure.attach("Балансировка IP трафика в %s нормальная т.к. отклонение равно или превысило 20%% и равно - %d%%"%(int1_name,delta1_send),"Процент отклонения в %s"%int1_name, attachment_type=allure.attachment_type.TEXT)
    elif delta1_send>=15:
        allure.attach("Балансировка IP трафика в %s приемлемая т.к. отклонение равно или превысило 15%% и равно - %d%%"%(int1_name,delta1_send),"Процент отклонения в %s"%int1_name, attachment_type=allure.attachment_type.TEXT)
    else:
        allure.attach("Балансировка IP трафика в %s превосходная т.к. отклонение меньше 15%% и равно - %d%%"%(int1_name,delta1_send),"Процент отклонения в %s"%int1_name, attachment_type=allure.attachment_type.TEXT)

    if delta2_send>=30:
        allure.attach("Балансировка IP трафика в %s средняя т.к. отклонение равно или превысило 30%% и равно - %d%%"%(int2_name,delta2_send),"Процент отклонения в %s"%int2_name, attachment_type=allure.attachment_type.TEXT)
    elif delta2_send>=20:
        allure.attach("Балансировка IP трафика в %s нормальная т.к. отклонение равно или превысило 20%% и равно - %d%%"%(int2_name,delta2_send),"Процент отклонения в %s"%int2_name, attachment_type=allure.attachment_type.TEXT)
    elif delta2_send>=15:
        allure.attach("Балансировка IP трафика в %s приемлемая т.к. отклонение равно или превысило 15%% и равно - %d%%"%(int2_name,delta2_send),"Процент отклонения в %s"%int2_name, attachment_type=allure.attachment_type.TEXT)
    else:
        allure.attach("Балансировка IP трафика в %s превосходная т.к. отклонение меньше 15%% и равно - %d%%"%(int2_name,delta2_send),"Процент отклонения в %s"%int2_name, attachment_type=allure.attachment_type.TEXT)
    
    if delta3_send>=30:
        allure.attach("Балансировка IP трафика в %s средняя т.к. отклонение равно или превысило 30%% и равно - %d%%"%(int3_name,delta3_send),"Процент отклонения в %s"%int3_name, attachment_type=allure.attachment_type.TEXT)
    elif delta3_send>=20:
        allure.attach("Балансировка IP трафика в %s нормальная т.к. отклонение равно или превысило 20%% и равно - %d%%"%(int3_name,delta3_send),"Процент отклонения в %s"%int3_name, attachment_type=allure.attachment_type.TEXT)
    elif delta3_send>=15:
        allure.attach("Балансировка IP трафика в %s приемлемая т.к. отклонение равно или превысило 15%% и равно - %d%%"%(int3_name,delta3_send),"Процент отклонения в %s"%int3_name, attachment_type=allure.attachment_type.TEXT)
    else:
        allure.attach("Балансировка IP трафика в %s превосходная т.к. отклонение меньше 15%% и равно - %d%%"%(int3_name,delta3_send),"Процент отклонения в %s"%int3_name, attachment_type=allure.attachment_type.TEXT)
    
    if delta4_send>=30:
        allure.attach("Балансировка IP трафика в %s средняя т.к. отклонение равно или превысило 30%% и равно - %d%%"%(int4_name,delta4_send),"Процент отклонения в %s"%int4_name, attachment_type=allure.attachment_type.TEXT)
    elif delta4_send>=20:
        allure.attach("Балансировка IP трафика в %s нормальная т.к. отклонение равно или превысило 20%% и равно - %d%%"%(int4_name,delta4_send),"Процент отклонения в %s"%int4_name, attachment_type=allure.attachment_type.TEXT)
    elif delta4_send>=15:
        allure.attach("Балансировка IP трафика в %s приемлемая т.к. отклонение равно или превысило 15%% и равно - %d%%"%(int4_name,delta4_send),"Процент отклонения в %s"%int4_name, attachment_type=allure.attachment_type.TEXT)
    else:
        allure.attach("Балансировка IP трафика в %s превосходная т.к. отклонение меньше 15%% и равно - %d%%"%(int4_name,delta4_send),"Процент отклонения в %s"%int4_name, attachment_type=allure.attachment_type.TEXT)
