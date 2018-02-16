from multiprocessing import Pool
from multiprocessing import cpu_count
import json
import re
import time
import os
import sys
from itertools import repeat
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from datetime import datetime
from xvfbwrapper import Xvfb

errors =  []
total_progress = 0
instance_status = {}
use_xvfb = False

def run_inputs(instance_id, base_name, base_page):
    instance_status = {}
    lp_status = 0
    instance_status[str(base_name+str(instance_id))] = {}
    instance_status[str(base_name+str(instance_id))]['timestamps'] = {}
    instance_status[str(base_name+str(instance_id))]['timestamps']['0_instance_born'] = str(datetime.utcnow())
    try:
        if sys.platform != 'darwin' and use_xvfb:
            print('Starting Xvfb')
            vdisplay = Xvfb(width=1280, height=740)
            vdisplay.start()

        chrome_options = webdriver.ChromeOptions()
        if sys.platform != 'darwin':
            chrome_options.add_argument('headless')
        chrome_options.add_argument('no-sandbox')
        # chrome_options.add_argument('window-size=1200x700')
        print('Will create driver')
        driver = webdriver.Chrome(chrome_options=chrome_options)
        print('driver:'+str(driver))
        # os.environ['MOZ_HEADLESS'] = '1'
        # driver = webdriver.Firefox()
    except BaseException as e:
        instance_status[str(base_name+str(instance_id))]['status'] = 'could_not_open'
        instance_status[str(base_name+str(instance_id))]['status_message'] = str(e)
        try:
            if sys.platform != 'darwin' and use_xvfb:
                print('Closing Xvfb')
                vdisplay.stop()
        except BaseException as e:
            print(e)
        return instance_status
    try:

        driver.get(base_page)
        instance_status[str(base_name+str(instance_id))]['timestamps']['1_requested_website'] = str(datetime.utcnow())

        # Wait for chat launcher
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, 'nds-chat-launcher')))
        # Click on chat launcher
        instance_status[str(base_name+str(instance_id))]['timestamps']['2_chat_became_available'] = str(datetime.utcnow())
        sign_in_button = driver.find_element_by_id('nds-chat-launcher').click()
        # Move to iframe
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, 'nds-chat-iframe')))
        iframe = driver.find_elements_by_tag_name('iframe')[0]
        driver.switch_to_frame(iframe)
        # Wait for segmento
        WebDriverWait(driver, 30, poll_frequency=0.1).until(EC.visibility_of_element_located((By.ID, 'nds-chatbot-message-3')))
        WebDriverWait(driver, 15, poll_frequency=0.1).until(EC.text_to_be_present_in_element((By.XPATH, '//*[@id="nds-chatbot-message-3"]/div[1]/div'),'¿A qué segmento perteneces?'))
        instance_status[str(base_name+str(instance_id))]['timestamps']['3_segmento_cliente_available'] = str(datetime.utcnow())
        # Click on segmento
        driver.execute_script(""" (function(e,s){e.src=s;e.onload=function(){jQuery.noConflict();console.log('jQuery 2.2.4 injected');jQuery('#nds-chatbot-message-3 > div.nds-chat-comment-option-wrap > div:nth-child(3)').click()};document.head.appendChild(e);})(document.createElement('script'),'//code.jquery.com/jquery-2.2.4.min.js') """)
        instance_status[str(base_name+str(instance_id))]['timestamps']['4_segmento_cliente_selected'] = str(datetime.utcnow())
        time.sleep(10)
        # Wait for name question
        WebDriverWait(driver, 15, poll_frequency=0.1).until(EC.visibility_of_element_located((By.ID, 'nds-chatbot-message-4')))
        WebDriverWait(driver, 15, poll_frequency=0.1).until(EC.text_to_be_present_in_element((By.XPATH, '//*[@id="nds-chatbot-message-4"]/div/div'),'¿Cómo te llamas?'))
        instance_status[str(base_name+str(instance_id))]['timestamps']['5_como_te_llamas_prompted'] = str(datetime.utcnow())
        # Get text input field and send name
        input_field = driver.find_element_by_id('txMessage')
        instance_name = base_name + str(instance_id)
        input_field.send_keys(instance_name, Keys.ENTER)
        instance_status[str(base_name+str(instance_id))]['timestamps']['6_instance_name_sent'] = str(datetime.utcnow())
        # Wait for "¿Qué puedo hacer por ti?" prompt
        WebDriverWait(driver, 15, poll_frequency=0.1).until(EC.visibility_of_element_located((By.ID, 'nds-chatbot-message-5')))
        # Ask for agent
        input_field.send_keys('agente', Keys.ENTER)
        requested_agent_time = datetime.utcnow()
        instance_status[str(base_name+str(instance_id))]['timestamps']['7_requested_agent'] = str(requested_agent_time)
        # Live person status;
        # lp_status = 1 No Agents Available (last_element_text equals no_agents_available_text);
        # lp_status = 2 Connected to LivePerson (last_element_text equals connected_to_lp_text);
        no_agents_available_text_sub_1 = "Por el momento no hay agentes disponibles"
        no_agents_available_text_sub_2 = "Por favor comunícate a nuestro centro de contacto al (01 55) 5721-3390"
        no_agents_available_text = "Por el momento no hay agentes disponibles.Por favor comunícate a nuestro centro de contacto al (01 55) 5721-3390."
        connected_to_lp_text = "¡Buen día! Bienvenido al Chat de HSBC."
        time_out = 0
        while lp_status == 0:
            chat_nds_bubbles = driver.execute_script("""
            var z = document.getElementsByClassName('nds-chat-comment-by-nds-chat');
            var arr = Array.prototype.slice.call(z);
            t = arr.map(function(e){return e.innerText});
            return t
            """)
            last_element_text = ''
            for index, el in enumerate(chat_nds_bubbles):
                if connected_to_lp_text in el or (no_agents_available_text_sub_1 in el and no_agents_available_text_sub_2 in el):
                    last_element_text = el
                    break

            # Test if last_element_text equals no_agents_available_text
            if no_agents_available_text.replace(' ','').replace('\n','') in last_element_text.replace(' ','').replace('\n',''):
                lp_status = 1
                no_agents_available_time = datetime.utcnow()
                instance_status[str(base_name+str(instance_id))]['timestamps']['8_no_agents_available'] = str(no_agents_available_time)
                instance_status[str(base_name+str(instance_id))]['timestamps']['delta_since_agent_requested'] = str(no_agents_available_time - requested_agent_time)
                instance_status[str(base_name+str(instance_id))]['timestamps']['chatbot_history'] = str(chat_nds_bubbles)
                break
            elif connected_to_lp_text in last_element_text:
                connected_to_lp_time = datetime.utcnow()
                instance_status[str(base_name+str(instance_id))]['timestamps']['8_connected_to_lp_time'] = str(connected_to_lp_time)
                instance_status[str(base_name+str(instance_id))]['timestamps']['delta_since_agent_requested'] = str(connected_to_lp_time - requested_agent_time)
                instance_status[str(base_name+str(instance_id))]['timestamps']['chatbot_history'] = str(chat_nds_bubbles)
                lp_status = 2
                instance_status[str(base_name+str(instance_id))]['sent'] = []
                instance_status[str(base_name+str(instance_id))]['received'] = []
                # send first message
                try:
                    initial_input = 'hola!'
                    input_field = driver.find_element_by_id('txMessage')
                    input_field.send_keys(initial_input, Keys.ENTER)
                    sent_time = str(datetime.utcnow())
                    instance_status[str(base_name+str(instance_id))]['sent'].append({sent_time: initial_input})
                except BaseException as e:
                    print('Problems while sending initial_input '+str(instance_id))
                    print(e)
                    if 'lp_errors' in instance_status[str(base_name+str(instance_id))]: # Concatenate previous errors
                        instance_status[str(base_name+str(instance_id))]['lp_errors'] += str(e)
                    else:
                        instance_status[str(base_name+str(instance_id))]['lp_errors'] = str(e)
                break
            time.sleep(1)
            time_out += 1
            if time_out > 60*3.5:
                timed_out_timestamp = datetime.utcnow()
                instance_status[str(base_name+str(instance_id))]['timestamps']['8_timed_out_timestamp'] = str(timed_out_timestamp)
                instance_status[str(base_name+str(instance_id))]['timestamps']['delta_since_agent_requested'] = str(timed_out_timestamp - requested_agent_time)
                instance_status[str(base_name+str(instance_id))]['timestamps']['chatbot_history'] = str(chat_nds_bubbles)
                break

    except BaseException as e:
        print('Problems with instance '+str(instance_id))
        print(e)
        if 'other_errors' in instance_status[str(base_name+str(instance_id))]: # Concatenate previous errors if they exists
            instance_status[str(base_name+str(instance_id))]['other_errors'] += str(e)
        else:
            instance_status[str(base_name+str(instance_id))]['other_errors'] = str(e)


    if lp_status == 1:
        print(base_name+str(instance_id)+' got no agents available message')
        instance_status[str(base_name+str(instance_id))]['status'] = 'no_agents'
    elif lp_status == 2:
        print(base_name+str(instance_id)+' contacted liveperson')
        instance_status[str(base_name+str(instance_id))]['status'] = 'contacted_liveperson'

        time_in_lp = 60*3.5 + 1;
        finish_lp = 1
        time_to_send_next_batch = 0
        number_of_batches_to_send = 5
        current_send_batch = 0
        time_between_batches = int(int(time_in_lp / number_of_batches_to_send) - 1)
        last_nds_chatbubble_included = 0
        while finish_lp < time_in_lp:
            if finish_lp > time_to_send_next_batch and current_send_batch < number_of_batches_to_send:
                current_send_batch += 1
                time_to_send_next_batch += time_between_batches
                inputs_to_send = ['hola.. '+str(current_send_batch), 'como estas.. '+str(current_send_batch), 'quiero ayuda.. '+str(current_send_batch)]
                try:
                    input_field = driver.find_element_by_id('txMessage')
                    for input_ in inputs_to_send:
                        input_field.send_keys(input_, Keys.ENTER)
                        sent_time = str(datetime.utcnow())
                        instance_status[str(base_name+str(instance_id))]['sent'].append({sent_time: input_})
                except BaseException as e:
                    print('Problems during LivePerson with instance '+str(instance_id))
                    print(e)
                    if 'lp_errors' in instance_status[str(base_name+str(instance_id))]: # Concatenate previous errors
                        instance_status[str(base_name+str(instance_id))]['lp_errors'] += str(e)
                    else:
                        instance_status[str(base_name+str(instance_id))]['lp_errors'] = str(e)
            try: # Get received messages
                chat_nds_bubbles = driver.execute_script("""
                var z = document.getElementsByClassName('nds-chat-comment-by-nds-chat');
                var arr = Array.prototype.slice.call(z);
                t = arr.map(function(e){return e.innerText});
                return t
                """)
                if last_nds_chatbubble_included == 0: # Initiate last_nds_chatbubble_included to the index where the text contains '¡Buen día! Bienvenido al Chat de HSBC. ¿En qué le puedo ayudar?'
                    for index, el in enumerate(chat_nds_bubbles):
                        if connected_to_lp_text in el:
                            last_nds_chatbubble_included = index
                            break

                while last_nds_chatbubble_included < len(chat_nds_bubbles)-1:
                    last_nds_chatbubble_included += 1
                    new_m = chat_nds_bubbles[last_nds_chatbubble_included].replace('Justo ahora','').replace('\n','').replace('1 minuto antes','').replace('2 minutos antes','')
                    new_m_timestamp = str(datetime.utcnow())
                    instance_status[str(base_name+str(instance_id))]['received'].append({new_m_timestamp: new_m})
            except BaseException as e:
                print('Problems during LivePerson with instance '+str(instance_id))
                print(e)
                if 'lp_errors' in instance_status[str(base_name+str(instance_id))]: # Concatenate previous errors
                    instance_status[str(base_name+str(instance_id))]['lp_errors'] += str(e)
                else:
                    instance_status[str(base_name+str(instance_id))]['lp_errors'] = str(e)
            time.sleep(1)
            finish_lp += 1
    else:
        print(base_name+str(instance_id)+' timed out')
        instance_status[str(base_name+str(instance_id))]['status'] = 'timed_out'

    instance_status[str(base_name+str(instance_id))]['timestamps']['9_closing_instance'] = str(datetime.utcnow())
    print('Closing '+base_name+str(instance_id))
    try:
        driver.close()
        if sys.platform != 'darwin' and use_xvfb:
            vdisplay.stop()

    except BaseException as e:
        instance_status[str(base_name+str(instance_id))]['closing_error'] = str(e)

    return instance_status

def execute_lps(total_instances = 5, base_name = 'Luis', endpoint='https://chat-container.mybluemix.net/'):
    print('Initializing '+str(total_instances)+' instances..')
    print('Available CPUs: '+str(cpu_count()))
    print('LivePerson stress test...')
    total_instances = total_instances
    pool = Pool(total_instances) # Create process pool
    results = pool.starmap(run_inputs, zip(list(range(total_instances)), repeat(base_name), repeat(endpoint)))
    pool.close()
    pool.join() # Bookeeping for Pool

    print('\n\nFinished:\n')
    # print(results)

    results = {k:v for d in results for k,v in d.items()}
    print(json.dumps(results, indent=1, sort_keys=True))

    return results

if __name__ == "__main__":
    execute_lps()
