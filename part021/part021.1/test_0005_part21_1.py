from conftest import *

@pytest.fixture(scope='function')
def remove_undo_test(DUT):
  yield
  conn = Telnet()
  acc = Account(DUT.login, DUT.password)
  conn.connect(DUT.host_ip)
  conn.set_prompt('#')
  conn.login(acc)
  conn.execute("config")

  if DUT.host_ip == DUT1.host_ip:
    conn.execute("interface te0/0/4")
    conn.execute("load-interval 20")
    conn.execute("no shutdown")
    conn.execute("commit")
    conn.execute("end")

    conn.execute("config")
    conn.execute("interface te0/0/3")
    conn.execute("load-interval 20")
    conn.execute("router isis test")
    conn.execute("interface te0/0/3")
    conn.execute("no level level-2")
    conn.execute("commit")
    conn.execute("end")

    conn.execute("config")
    conn.execute("interface te0/0/2")
    conn.execute("load-interval 20")
    conn.execute("router isis test")
    conn.execute("interface te0/0/2")
    conn.execute("address-family ipv4 unicast")
    conn.execute("exit")
    conn.execute("point-to-point")
    conn.execute("level level-2")

  elif DUT.host_ip == DUT2.host_ip:
    conn.execute("interface te0/0/4")
    conn.execute("load-interval 20")
    conn.execute("no shutdown")
    conn.execute("commit")
    conn.execute("end")

    conn.execute("config")
    conn.execute("interface te0/0/3")
    conn.execute("load-interval 20")
    conn.execute("router isis test")
    conn.execute("interface te0/0/3")
    conn.execute("level level-2")
    conn.execute("metric 20")
    conn.execute("commit")
    conn.execute("end")

    conn.execute("config")
    conn.execute("interface te0/0/2")
    conn.execute("load-interval 20")
    conn.execute("router isis test")
    conn.execute("interface te0/0/2")
    conn.execute("address-family ipv4 unicast")
    conn.execute("exit")
    conn.execute("point-to-point")
    conn.execute("no level level-2")

  else:
    conn.execute("interface te0/0/4")
    conn.execute("load-interval 20")
    conn.execute("no shutdown")
    conn.execute("commit")
    conn.execute("end")

    conn.execute("config")
    conn.execute("interface te0/0/3")
    conn.execute("load-interval 20")
    conn.execute("router isis test")
    conn.execute("interface te0/0/3")
    conn.execute("no level level-2")
    conn.execute("commit")
    conn.execute("end")

    conn.execute("config")
    conn.execute("interface te0/0/2")
    conn.execute("load-interval 20")
    conn.execute("router isis test")
    conn.execute("interface te0/0/2")
    conn.execute("address-family ipv4 unicast")
    conn.execute("exit")
    conn.execute("point-to-point")
    conn.execute("level level-2")
    conn.execute("metric 20")

  conn.execute("commit")
  conn.execute("end")


def gen_traffic(ip_iperf_server, login, password, host_ip, vrf_cli, vrf_cli2):
  estimated_duration_time=40

  start_traffic_gen=time.time() # Фиксируем время начала генерации трафика
  x=thread_with_trace(target=start_udp_esr_iperf3_server_client_queue,args=(ip_iperf_server,estimated_duration_time , '100M', vrf_cli))
  y=thread_with_trace(target=start_udp_esr_iperf3_server_client_queue,args=(ip_iperf_server,estimated_duration_time , '100M', vrf_cli2))
  x.start() # Запускаем iperf клиент и сервер в докер-контейнерах
  y.start()

  conn = Telnet()
  acc = Account(login, password)
  conn.connect(host_ip)
  conn.login(acc)
  conn.set_prompt('#')
  conn.execute('terminal datadump')
  time.sleep(30) # Ждем пока накопится статистика на интерфейсах 
  cmd=('show interfaces utilization | incl " 20 | Interf"')
  conn.execute(cmd)
  resp = conn.response
  allure.attach(resp, 'Вывод команды %s'%cmd, attachment_type=allure.attachment_type.TEXT)   
#  print(resp)
  template = open('./templates/parse_show_int_utilization.txt')
  fsm = textfsm.TextFSM(template)
  processed_result=fsm.ParseTextToDicts(resp)

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
  return processed_result, cmd

def switch_int(step, login, password, host_ip):
  conn = Telnet()
  acc = Account(login, password)
  conn.connect(host_ip)
  conn.login(acc)
  conn.execute("config")
  if host_ip == DUT1.host_ip:
    if step == 1:
      conn.execute("interface te0/0/4")
      conn.execute("no load-interval 20")
      conn.execute("shutdown")
    elif step == 2:
      conn.execute("interface te0/0/3")
      conn.execute("no load-interval 20")
      conn.execute("router isis test")
      conn.execute("interface te0/0/3")
      conn.execute("level level-2")
      conn.execute("metric 100")
    elif step == 3:
      conn.execute("interface te0/0/2")
      conn.execute("no load-interval 20")
      conn.execute("router isis test")
      conn.execute("no interface te0/0/2")
    else:
      conn.execute("interface te0/0/4")
      conn.execute("load-interval 20")
      conn.execute("no shutdown")
      conn.execute("commit")
      conn.execute("end")

      conn.execute("config")
      conn.execute("interface te0/0/3")
      conn.execute("load-interval 20")
      conn.execute("router isis test")
      conn.execute("interface te0/0/3")
      conn.execute("no level level-2")
      conn.execute("commit")
      conn.execute("end")

      conn.execute("config")
      conn.execute("interface te0/0/2")
      conn.execute("load-interval 20")
      conn.execute("router isis test")
      conn.execute("interface te0/0/2")
      conn.execute("address-family ipv4 unicast")
      conn.execute("exit")
      conn.execute("point-to-point")
      conn.execute("level level-2")
      conn.execute("metric 20")
  
  elif host_ip == DUT2.host_ip:
    if step == 1:
      conn.execute("interface te0/0/4")
      conn.execute("no load-interval 20")
      conn.execute("shutdown")
    elif step == 2:
      conn.execute("interface te0/0/3")
      conn.execute("no load-interval 20")
      conn.execute("router isis test")
      conn.execute("interface te0/0/3")
      conn.execute("level level-2")
      conn.execute("metric 100")
    elif step == 3:
      conn.execute("interface te0/0/2")
      conn.execute("no load-interval 20")
      conn.execute("router isis test")
      conn.execute("no interface te0/0/2")
    else:
      conn.execute("interface te0/0/4")
      conn.execute("load-interval 20")
      conn.execute("no shutdown")
      conn.execute("commit")
      conn.execute("end")

      conn.execute("config")
      conn.execute("interface te0/0/3")
      conn.execute("load-interval 20")
      conn.execute("router isis test")
      conn.execute("interface te0/0/3")
      conn.execute("level level-2")
      conn.execute("metric 20")
      conn.execute("commit")
      conn.execute("end")

      conn.execute("config")
      conn.execute("interface te0/0/2")
      conn.execute("load-interval 20")
      conn.execute("router isis test")
      conn.execute("interface te0/0/2")
      conn.execute("address-family ipv4 unicast")
      conn.execute("exit")
      conn.execute("point-to-point")
      conn.execute("no level level-2")
      
  else:
    if step == 1:
      conn.execute("interface te0/0/4")
      conn.execute("no load-interval 20")
      conn.execute("shutdown")
    elif step == 2:
      conn.execute("interface te0/0/3")
      conn.execute("no load-interval 20")
      conn.execute("router isis test")
      conn.execute("interface te0/0/3")
      conn.execute("level level-2")
      conn.execute("metric 100")
    elif step == 3:
      conn.execute("interface te0/0/2")
      conn.execute("no load-interval 20")
      conn.execute("router isis test")
      conn.execute("no interface te0/0/2")
    else:
      conn.execute("interface te0/0/4")
      conn.execute("load-interval 20")
      conn.execute("no shutdown")
      conn.execute("commit")
      conn.execute("end")

      conn.execute("config")
      conn.execute("interface te0/0/3")
      conn.execute("load-interval 20")
      conn.execute("router isis test")
      conn.execute("interface te0/0/3")
      conn.execute("no level level-2")
      conn.execute("commit")
      conn.execute("end")

      conn.execute("config")
      conn.execute("interface te0/0/2")
      conn.execute("load-interval 20")
      conn.execute("router isis test")
      conn.execute("interface te0/0/2")
      conn.execute("address-family ipv4 unicast")
      conn.execute("exit")
      conn.execute("point-to-point")
      conn.execute("level level-2")
      conn.execute("metric 20")

  conn.execute("commit")
  conn.execute("end")
   

@pytest.mark.part21_1
@pytest.mark.base_function_ECMP
@allure.epic('21:ECMP')
@allure.feature('21.1:ECMP балансировка IP трафика в GRT (IGP: ISIS)')
@allure.story('21.1.3:Тестирование функционала балансировки IGP: ISIS трафика между интерфейсами методом лестница')
@allure.title('Проверка балансировки IGP: ISIS трафика между интерфейсами с отключением интерфейсов')
@pytest.mark.dependency(depends=["load_config211_dut1","load_config211_dut2","load_config211_dut3"],scope='session')
@pytest.mark.parametrize('DUT, ip_iperf_server, vrf_cli, vrf_cli2', 
                         [(DUT1, '192.168.73.10', 'CE1', 'CE11'),
                          (DUT2, '192.168.70.10', 'CE2', 'CE12'),
                          (DUT3, '192.168.74.10', 'CE3', 'CE13')])
@pytest.mark.usefixtures('remove_undo_test')
def test_ECMP_isis_upstair_21_1(DUT, ip_iperf_server, vrf_cli, vrf_cli2):
  check = ["te0/0/1", "te0/0/2", "te0/0/3", "te0/0/4"]
  if DUT.host_ip == DUT1.host_ip:
      allure.attach.file('./network-schemes/part21_cli1_to_cli2.png','Схема теста:', attachment_type=allure.attachment_type.PNG)
  elif DUT.host_ip == DUT2.host_ip:
      allure.attach.file('./network-schemes/part21_cli2_to_cli3.png','Схема теста:', attachment_type=allure.attachment_type.PNG)
  else:
      allure.attach.file('./network-schemes/part21_cli3_to_cli1.png','Схема теста:', attachment_type=allure.attachment_type.PNG)

  step = 4
  for i in range(1, step + 1):
    switch_int(i, DUT.login, DUT.password, DUT.host_ip)
    processed_result, cmd = gen_traffic(ip_iperf_server, DUT.login, DUT.password, DUT.host_ip, vrf_cli, vrf_cli2)
    print(processed_result)
    number_of_elements = len(processed_result)
    if i != step:
      mas = []
      for j in range(step - i):
        mas.append(processed_result[j]['Int_name'])
        mas.append(processed_result[j]['Int_send'])
        assert_that(processed_result[j]['Int_name']==check[j],"В выводе команды %s имя первого интерфейса не равно ожидаемому значению %s, а равно - %s тест закончился на этапе %d"%(cmd,check[j],processed_result[j]['Int_name'], i))
        assert_that(int(processed_result[j]['Int_send'])>10,"%s: На интерфейсе %s отсутствует исходящий трафик тест закончился на этапе %d"%(DUT.host_ip,processed_result[j]['Int_name'], i))
      delta_send = []
      sum = 0

      for j in range(1,len(mas),2):
        sum += int(mas[j]) 

      for j in range(1,len(mas),2):
        delta_send.append(abs((int(mas[j]) / sum) - (1 / (step - i))) * 100)
      
      for j in range(len(delta_send)):
        assert_that(delta_send[j]<=50,"%s: Балансировка IP трафика в %s очень плохая т.к. отклонение равно или превысило 50%% и равно - %d%% тест закончился на этапе %d"%(DUT.host_ip,mas[j * 2],delta_send[j], i))
        assert_that(delta_send[j]<=40,"%s: Балансировка IP трафика в %s плохая т.к. отклонение равно или превысило 40%% и равно - %d%% тест закончился на этапе %d"%(DUT.host_ip,mas[j * 2],delta_send[j], i))
        #assert_that(delta_send[j]<=30,"%s: Балансировка IP трафика в %s средняя т.к. отклонение равно или превысило 30%% и равно - %d%% тест закончился на этапе %d"%(DUT.host_ip,mas[j * 2],delta_send[j], i))
        #assert_that(delta_send[j]<=20,"%s: Балансировка IP трафика в %s нормальная т.к. отклонение равно или превысило 20%% и равно - %d%% тест закончился на этапе %d"%(DUT.host_ip,mas[j * 2],delta_send[j], i))
        #assert_that(delta_send[j]<=15,"%s: Балансировка IP трафика в %s приемлемая т.к. отклонение равно или превысило 15%% и равно - %d%% тест закончился на этапе %d"%(DUT.host_ip,mas[j * 2],delta_send[j], i))
        if delta_send[j]>=30:
          allure.attach("Балансировка IP трафика в %s средняя т.к. отклонение равно или превысило 30%% и равно - %d%%, этап %d"%(mas[j * 2],delta_send[j], i),"Процент отклонения в %s"%mas[j * 2], attachment_type=allure.attachment_type.TEXT)
        elif delta_send[j]>=20:
          allure.attach("Балансировка IP трафика в %s нормальная т.к. отклонение равно или превысило 20%% и равно - %d%%, этап %d"%(mas[j * 2],delta_send[j], i),"Процент отклонения в %s"%mas[j * 2], attachment_type=allure.attachment_type.TEXT)
        elif delta_send[j]>=15:
          allure.attach("Балансировка IP трафика в %s приемлемая т.к. отклонение равно или превысило 15%% и равно - %d%%, этап %d"%(mas[j * 2],delta_send[j], i),"Процент отклонения в %s"%mas[j * 2], attachment_type=allure.attachment_type.TEXT)
        else:
          allure.attach("Балансировка IP трафика в %s превосходная т.к. отклонение меньше 15%% и равно - %d%%, этап %d"%(mas[j * 2],delta_send[j], i),"Процент отклонения в %s"%mas[j * 2], attachment_type=allure.attachment_type.TEXT)
    
    else:
      assert_that(number_of_elements==step, "Кол-во элементов в списке processed_result не соответствует ожидаемым 4, а равно - %d" %number_of_elements)

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
      assert_that(int3_name=="te0/0/3","В выводе команды %s имя третьего интерфейса не равно ожидаемому значению te0/0/2, а равно - %s"%(cmd,int3_name))
      assert_that(int4_name=="te0/0/4","В выводе команды %s имя четвёртого интерфейса не равно ожидаемому значению te0/0/2, а равно - %s"%(cmd,int4_name))

      assert_that(int(int1_send)>10,"%s: На интерфейсе %s отсутствует исходящий трафик тест закончился на этапе 4"%(DUT.host_ip,int1_name))
      assert_that(int(int2_send)>10,"%s: На интерфейсе %s отсутствует исходящий трафик тест закончился на этапе 4"%(DUT.host_ip,int2_name))
      assert_that(int(int3_send)>10,"%s: На интерфейсе %s отсутствует исходящий трафик тест закончился на этапе 4"%(DUT.host_ip,int3_name))
      assert_that(int(int4_send)>10,"%s: На интерфейсе %s отсутствует исходящий трафик тест закончился на этапе 4"%(DUT.host_ip,int4_name))

      delta1_send=round((abs((int(int1_send) / (int(int1_send) + int(int2_send) + int(int3_send) + int(int4_send))) - 0.25))*100)
      delta2_send=round((abs((int(int2_send) / (int(int1_send) + int(int2_send) + int(int3_send) + int(int4_send))) - 0.25))*100)
      delta3_send=round((abs((int(int3_send) / (int(int1_send) + int(int2_send) + int(int3_send) + int(int4_send))) - 0.25))*100)
      delta4_send=round((abs((int(int4_send) / (int(int1_send) + int(int2_send) + int(int3_send) + int(int4_send))) - 0.25))*100)

      assert_that(delta1_send<=50,"%s: Балансировка IP трафика в %s очень плохая т.к. отклонение равно или превысило 50%% и равно - %d%% тест закончился на этапе 4"%(DUT.host_ip,int1_name,delta1_send))
      assert_that(delta1_send<=40,"%s: Балансировка IP трафика в %s плохая т.к. отклонение равно или превысило 40%% и равно - %d%% тест закончился на этапе 4"%(DUT.host_ip,int1_name,delta1_send))
      #assert_that(delta1_send<=30,"%s: Балансировка IP трафика в %s средняя т.к. отклонение равно или превысило 30%% и равно - %d%% тест закончился на этапе 4"%(DUT.host_ip,int1_name,delta1_send))
      #assert_that(delta1_send<=20,"%s: Балансировка IP трафика в %s нормальная т.к. отклонение равно или превысило 20%% и равно - %d%% тест закончился на этапе 4"%(DUT.host_ip,int1_name,delta1_send))
      #assert_that(delta1_send<=15,"%s: Балансировка IP трафика в %s приемлемая т.к. отклонение равно или превысило 15%% и равно - %d%% тест закончился на этапе 4"%(DUT.host_ip,int1_name,delta1_send))

      assert_that(delta2_send<=50,"%s: Балансировка IP трафика в %s очень плохая т.к. отклонение равно или превысило 50%% и равно - %d%% тест закончился на этапе 4"%(DUT.host_ip,int2_name,delta2_send))
      assert_that(delta2_send<=40,"%s: Балансировка IP трафика в %s плохая т.к. отклонение равно или превысило 40%% и равно - %d%% тест закончился на этапе 4"%(DUT.host_ip,int2_name,delta2_send))
      #assert_that(delta2_send<=30,"%s: Балансировка IP трафика в %s средняя т.к. отклонение равно или превысило 30%% и равно - %d%% тест закончился на этапе 4"%(DUT.host_ip,int2_name,delta2_send))
      #assert_that(delta2_send<=20,"%s: Балансировка IP трафика в %s нормальная т.к. отклонение равно или превысило 20%% и равно - %d%% тест закончился на этапе 4"%(DUT.host_ip,int2_name,delta2_send))
      #assert_that(delta2_send<=15,"%s: Балансировка IP трафика в %s приемлемая т.к. отклонение равно или превысило 15%% и равно - %d%% тест закончился на этапе 4"%(DUT.host_ip,int2_name,delta2_send))

      assert_that(delta3_send<=50,"%s: Балансировка IP трафика в %s очень плохая т.к. отклонение равно или превысило 50%% и равно - %d%% тест закончился на этапе 4"%(DUT.host_ip,int3_name,delta3_send))
      assert_that(delta3_send<=40,"%s: Балансировка IP трафика в %s плохая т.к. отклонение равно или превысило 40%% и равно - %d%% тест закончился на этапе 4"%(DUT.host_ip,int3_name,delta3_send))
      #assert_that(delta3_send<=30,"%s: Балансировка IP трафика в %s средняя т.к. отклонение равно или превысило 30%% и равно - %d%% тест закончился на этапе 4"%(DUT.host_ip,int3_name,delta3_send))
      #assert_that(delta3_send<=20,"%s: Балансировка IP трафика в %s нормальная т.к. отклонение равно или превысило 20%% и равно - %d%% тест закончился на этапе 4"%(DUT.host_ip,int3_name,delta3_send))
      #assert_that(delta3_send<=15,"%s: Балансировка IP трафика в %s приемлемая т.к. отклонение равно или превысило 15%% и равно - %d%% тест закончился на этапе 4"%(DUT.host_ip,int3_name,delta3_send))

      assert_that(delta4_send<=50,"%s: Балансировка IP трафика в %s очень плохая т.к. отклонение равно или превысило 50%% и равно - %d%% тест закончился на этапе 4"%(DUT.host_ip,int4_name,delta4_send))
      assert_that(delta4_send<=40,"%s: Балансировка IP трафика в %s плохая т.к. отклонение равно или превысило 40%% и равно - %d%% тест закончился на этапе 4"%(DUT.host_ip,int4_name,delta4_send))
      #assert_that(delta4_send<=30,"%s: Балансировка IP трафика в %s средняя т.к. отклонение равно или превысило 30%% и равно - %d%% тест закончился на этапе 4"%(DUT.host_ip,int4_name,delta4_send))
      #assert_that(delta4_send<=20,"%s: Балансировка IP трафика в %s нормальная т.к. отклонение равно или превысило 20%% и равно - %d%% тест закончился на этапе 4"%(DUT.host_ip,int4_name,delta4_send))
      #assert_that(delta4_send<=15,"%s: Балансировка IP трафика в %s приемлемая т.к. отклонение равно или превысило 15%% и равно - %d%% тест закончился на этапе 4"%(DUT.host_ip,int4_name,delta4_send))

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
