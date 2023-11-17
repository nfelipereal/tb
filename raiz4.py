from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from telegram import Bot
import datetime 
import time
import re

def percent_to_emojis(percent):
    if percent < 30:
        return "🟥" * ((percent // 10) + 1)
    elif percent < 70:
        return "🟧" * (((percent - 30) // 8) + 4)
    else:
        return "🟩" * (((percent - 70) // 6) + 7)

def generate_horarios_message(minutos_str):
    pagantes = [int(x) for x in minutos_str.split(',')]
    next_times = []
    time_counter = datetime.datetime.now()
    while len(next_times) < 8:
        if time_counter.minute % 10 in pagantes:
            next_times.append(time_counter.strftime('%H:%M'))
        time_counter += datetime.timedelta(minutes=1)
    formatted_times_line1 = ' | '.join(next_times[:4])
    formatted_times_line2 = ' | '.join(next_times[4:])
    caption = f"*Oportunidade identificada!*\n\n*Total de jogadas*: 10\n\n5x Normal / 5x Turbo\n\n*Horários*:\n{formatted_times_line1} \n{formatted_times_line2}"
    return caption

def extract_graph_data(wait, game):
    progress_data = {}
    progress_types = [('Bet seguindo o padrão', 'Bet follow default'), ('Bet mínima', 'Bet minimum'), ('Bet máxima', 'Bet maximum')]
    for p_type, bet_text in progress_types:
        progress_bar_xpath = f"//div[@class='progress-section']//div[text()='{bet_text}']/following-sibling::div//div[contains(@class, 'ant-progress-bg')]"
        progress_bar = wait.until(EC.presence_of_element_located((By.XPATH, progress_bar_xpath)))
        style = progress_bar.get_attribute('style')
        percent = re.search('width: (\d+)%', style).group(1)
        progress_data[p_type] = int(percent)
    return progress_data

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920x1080")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

TOKEN = '6647029854:AAHndW-FyDoueUuy_4mT-JtXKS0FnTYaqMY'
bot = Bot(TOKEN)
GROUP_CHAT_ID = '-1002121175446'

games_info = [
     {'cod': '103', 'nome': 'Fortune Rabbit', 'minutos': '1,2,3,7,8,9', 'imagem': 'https://uploaddeimagens.com.br/images/004/664/967/original/rabbit.jpg?1700012925'},
    {'cod': '17', 'nome': 'Fortune Tiger', 'minutos': '0,5,2,8', 'imagem': 'https://uploaddeimagens.com.br/images/004/665/034/full/23456.jpg?1700025649'},
     {'cod': '52', 'nome': 'Fortune Mouse', 'minutos': '0,5,7,6', 'imagem': 'https://uploaddeimagens.com.br/images/004/665/035/full/1695335019-fortune-mouse-sacar-dinheiro.jpg?1700025699'},
      {'cod': '58', 'nome': 'The Great Icescape', 'minutos': '0,1,2,4,6', 'imagem': 'https://uploaddeimagens.com.br/images/004/665/033/full/pg-slot-cover-34-1.png?1700025628'},
       {'cod': '7', 'nome': 'Fortune Ox', 'minutos': '2,6,5,8,9', 'imagem': 'https://uploaddeimagens.com.br/images/004/665/036/original/IMG_3634.jpeg?1700025838'}
    
]

wait = WebDriverWait(driver, 10)

while True:
    driver.get('https://slot-pg-soft.prodevreal.com/')
    wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, 'app-loading')))

    message_ids = []
    captions = {}  # Armazene as legendas das mensagens aqui
    for game in games_info:
        all_games_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[text()='All Games']")))
        all_games_button.click()
        time.sleep(5)

        game_element = wait.until(EC.element_to_be_clickable((By.XPATH, f"//b[contains(text(), '{game['cod']}')]/ancestor::div[contains(@class, 'game-card')]")))
        game_element.click()
        time.sleep(5)

        progress_data = extract_graph_data(wait, game)
        graph_message = "\n".join(f"{p_type}\n{percent_to_emojis(percent)}{percent}%" for p_type, percent in progress_data.items())
        horarios_message = generate_horarios_message(game['minutos'])
        full_message = f"*{game['nome']}*\n\n{graph_message}\n\n{horarios_message}"

        try:
            sent_message = bot.send_photo(chat_id=GROUP_CHAT_ID, photo=game['imagem'], caption=full_message, parse_mode='Markdown')
            message_ids.append(sent_message.message_id)
            captions[sent_message.message_id] = full_message  # Armazene a legenda da mensagem
        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")

        driver.get('https://slot-pg-soft.prodevreal.com/')
        wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, 'app-loading')))

        time.sleep(20)

    start_time = time.time()
    while time.time() - start_time < 1200:
        for i, game in enumerate(games_info):
            driver.get('https://slot-pg-soft.prodevreal.com/')
            wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, 'app-loading')))
            all_games_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[text()='All Games']")))
            all_games_button.click()
            time.sleep(5)
            game_element = wait.until(EC.element_to_be_clickable((By.XPATH, f"//b[contains(text(), '{game['cod']}')]/ancestor::div[contains(@class, 'game-card')]")))
            game_element.click()
            time.sleep(5)

            new_progress_data = extract_graph_data(wait, game)
            new_graph_message = "\n".join(f"{p_type}\n{percent_to_emojis(percent)}{percent}%" for p_type, percent in new_progress_data.items())
             
            # Obtenha a legenda existente
            existing_caption = captions[message_ids[i]]
            # Substitua a parte da legenda que você deseja alterar
            # A expressão regular agora captura desde o nome do jogo até "Oportunidade identificada!"
            pattern = r"(\*{}\*\n\n).*?(\n\n\*Oportunidade identificada!\*)".format(game['nome'].replace('*', '\*'))
            new_graph_section = r"\1" + new_graph_message + r"\2"
            new_caption = re.sub(pattern, new_graph_section, existing_caption, flags=re.DOTALL)
                     
            # Adicione a hora da última atualização
            now = datetime.datetime.now()
            last_updated = now.strftime("%H:%M")
            new_caption = f"Última atualização {last_updated}\n\n" + new_caption
            
            # Verifique se a nova legenda é diferente da existente
            if new_caption != existing_caption:
                # Edite a legenda da mensagem
                try:
                    bot.edit_message_caption(chat_id=GROUP_CHAT_ID, message_id=message_ids[i], caption=new_caption, parse_mode='Markdown')
                except Exception as e:
                    print(f"Erro ao editar mensagem: {e}")

        time.sleep(60)
       # Deletar mensagens antigas antes de enviar novas
    for message_id in message_ids:
        try:
            bot.delete_message(chat_id=GROUP_CHAT_ID, message_id=message_id)
            print(f"Mensagem {message_id} deletada.")
        except Exception as e:
            print(f"Erro ao deletar mensagem {message_id}: {e}")

    message_ids = []


driver.quit()
