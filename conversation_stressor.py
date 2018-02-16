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
    print('Got bp: '+str(base_page))
    instance_status = {}
    lp_status = 0
    entered_chat = False
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
        WebDriverWait(driver, 45).until(EC.visibility_of_element_located((By.ID, 'nds-chat-launcher')))
        # Click on chat launcher
        instance_status[str(base_name+str(instance_id))]['timestamps']['2_chat_became_available'] = str(datetime.utcnow())
        # print('will open chat')
        sign_in_button = driver.find_element_by_id('nds-chat-launcher').click()
        # print('flag 0')
        # Move to iframe
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, 'nds-chat-iframe')))
        iframe = driver.find_element_by_id('nds-chat-iframe')
        driver.switch_to_frame(iframe)
        # Wait for segmento
        # print('flag 1')
        WebDriverWait(driver, 30, poll_frequency=0.1).until(EC.visibility_of_element_located((By.ID, 'nds-chatbot-message-3')))
        # print('flag 2')
        WebDriverWait(driver, 15, poll_frequency=0.1).until(EC.text_to_be_present_in_element((By.XPATH, '//*[@id="nds-chatbot-message-3"]/div[1]/div'),'¿A qué segmento perteneces?'))
        # print('flag 3')
        instance_status[str(base_name+str(instance_id))]['timestamps']['3_segmento_cliente_available'] = str(datetime.utcnow())
        # Click on segmento
        driver.execute_script(""" (function(e,s){e.src=s;e.onload=function(){jQuery.noConflict();console.log('jQuery 2.2.4 injected');jQuery('#nds-chatbot-message-3 > div.nds-chat-comment-option-wrap > div:nth-child(3)').click()};document.head.appendChild(e);})(document.createElement('script'),'//code.jquery.com/jquery-2.2.4.min.js') """)
        # print('will click segmento')
        #clck_s = driver.find_element_by_xpath('//*[@id="nds-chatbot-message-3"]/div[2]/div[3]').click()
        # print('Did click segmento')
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
        time.sleep(2)
        # Send inputs and test responses:
        inputs_to_send = {

        'por que soy cliente advance':"HSBC Advance es una propuesta para clientes distinguidos, enfocada a solucionar sus necesidades financieras, ofreciéndole productos y servicios con condiciones preferentes que te ayudarán a lograr tus metas de vida, así como la administración y construcción de tu patrimonio.",

        'que significa hsbc':"HSBC recibe su nombre de Hong Kong and Shanghai Banking Corporation Limited, compañía que se creó en 1865 para financiar el creciente comercio entre Europa, India y China.",

        'cual es el telefono de empresarial':'Para cualquier duda sobre productos o servicios empresariales por favor comunícate a nuestra Línea de Servicios Empresariales:'

        } # Finish inputs_to_send
        # 'tengo un afore':'HSBC y Principal Afore unen fuerzas para que al término de tu vida laboral tengas la mejor recompensa.',
        entered_chat = True
        for i_key in inputs_to_send:
            input_field.send_keys(i_key, Keys.ENTER)
            print('Sent '+str(i_key))
            input_time = datetime.utcnow()
            instance_status[str(base_name+str(instance_id))]['timestamps']['sent_'+str(i_key.replace(' ','_'))] = str(input_time)

            waiting_for_res = True
            time_out = 0
            while waiting_for_res:
                chat_nds_bubbles = driver.execute_script("""
                var z = document.getElementsByClassName('nds-chat-comment-by-nds-chat');
                var arr = Array.prototype.slice.call(z);
                t = arr.map(function(e){return e.innerText});
                return t
                """)
                for index, el in enumerate(chat_nds_bubbles):
                    if inputs_to_send[i_key] in el:
                        print('Got response for '+str(i_key))
                        res_time = datetime.utcnow()
                        instance_status[str(base_name+str(instance_id))]['timestamps']['got_response_for_'+str(i_key.replace(' ','_'))] = str(res_time)
                        waiting_for_res = False
                        break

                time.sleep(1)
                time_out += 1
                if time_out > 60*3:
                    timed_out_timestamp = datetime.utcnow()
                    instance_status[str(base_name+str(instance_id))]['status'] = 'timed_out'
                    instance_status[str(base_name+str(instance_id))]['timestamps']['8_timed_out_timestamp'] = str(timed_out_timestamp)
                    instance_status[str(base_name+str(instance_id))]['timestamps']['chatbot_history'] = str(chat_nds_bubbles)
                    break

    except BaseException as e:
        print('Problems with instance '+str(instance_id))
        print(e)
        if 'other_errors' in instance_status[str(base_name+str(instance_id))]: # Concatenate previous errors if they exists
            instance_status[str(base_name+str(instance_id))]['other_errors'] += str(e)
        else:
            instance_status[str(base_name+str(instance_id))]['other_errors'] = str(e)

    if 'status' in instance_status[str(base_name+str(instance_id))]:
        if instance_status[str(base_name+str(instance_id))]['status'] != 'timed_out':
            instance_status[str(base_name+str(instance_id))]['status'] += '_correct*'
    elif entered_chat:
        instance_status[str(base_name+str(instance_id))]['status'] = 'correct'
    else:
        instance_status[str(base_name+str(instance_id))]['status'] = 'timed_out_2'

    instance_status[str(base_name+str(instance_id))]['timestamps']['9_closing_instance'] = str(datetime.utcnow())
    print('Closing '+base_name+str(instance_id))
    try:
        driver.close()
        if sys.platform != 'darwin' and use_xvfb:
            vdisplay.stop()

    except BaseException as e:
        instance_status[str(base_name+str(instance_id))]['closing_error'] = str(e)

    return instance_status

def execute_cs(total_instances = 5, base_name = 'Luis', endpoint='https://chat-container.mybluemix.net/'):
    print('Initializing '+str(total_instances)+' instances..')
    print('Available CPUs: '+str(cpu_count()))
    print('Conversation stress test...')

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
    execute_cs()
