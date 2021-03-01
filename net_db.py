import os
from instapy import InstaPy
from instapy import set_workspace
from instapy import Settings
from instapy.database_engine import get_database
import sqlite3
import pandas as pd
from datetime import datetime
from dateutil.parser import parse
import json
import networkx as nx

#Parametrização
path_script = '/home/fm/Documents/clinstapy'
wsinstapy_folder = 'instapy_ws'
dbinstapy_folder = 'instapy_db'
browser_profile_path = r'/home/fm/Documents/clinstapy/firefox_clin_profile'
insta_acc_id = 'clinica''
insta_user = #yourinstauser
insta_psw = #yourinstapassword
user_stalk = #useryouwanna follow
set_workspace(os.path.join(path_script,wsinstapy_folder))
Settings.db_location = os.path.join(path_script,dbinstapy_folder)

#login
session = InstaPy(username=insta_user,password=insta_psw,headless_browser=False,split_db=True,multi_logs=True,browser_profile_path=browser_profile_path)
try:
    session.login()
except:
    print("If your credentials aren't save in cookies you need to write them manually")

#conexões
path_instapy_db = get_database(make=True)[0]
path_net_profiles = 'profiles_network.db'
con_instapy = sqlite3.connect(path_instapy_db)
con_net_prof = sqlite3.connect(path_net_profiles)

#configurações - Set of configurations to avoid serverblock from instagram
session.set_quota_supervisor(enabled=True, sleep_after=["likes", "comments_d", "follows", "unfollows", "server_calls_h"], sleepyhead=True, stochastic_flow=True, notify_me=True,
                              peak_likes_hourly=56,
                              peak_likes_daily=584,
                               peak_comments_hourly=20,
                               peak_comments_daily=181,
                                peak_follows_hourly=30,
                                peak_follows_daily=200,
                                 peak_unfollows_hourly=10,
                                 peak_unfollows_daily=100,
                                  peak_server_calls_hourly=None,
                                  peak_server_calls_daily=2000)

#Aquisição de dados de follow para banco
def grab_seguidores(session,user_stalk,insta_user,con_net_prof):
    #pega online
    us_followers = session.grab_followers(username=user_stalk, amount="full", live_match=True, store_locally=True)
    
    #salva resultados no banco
    path_json = f"/home/fm/Documents/clinstapy/InstaPy_ws/logs/{insta_user}//relationship_data/{user_stalk}/followers" #path to save followers names
    arquivos_log = os.listdir(path_json)
    data_arquivo_recente = max(datetime.strptime(arquivo[:10], '%d-%m-%Y') for arquivo in arquivos_log)
    nome_arquivo_recente = [arquivo for arquivo in arquivos_log if arquivo.startswith(data_arquivo_recente.strftime('%d-%m-%Y'))][0]
    path_arquivo_recente = os.path.join(path_json, nome_arquivo_recente)
    with open(path_arquivo_recente) as json_file:
        data = json.load(json_file)
    df1 = pd.DataFrame({'usuario':user_stalk, 'seguidor':data, 'data_informacao':datetime.now()})
    df1.to_sql(name = 'connections', con = con_net_prof, if_exists='append', index=False)

def grab_seguindo(session,user_stalk,insta_user,con_net_prof):
    #pega online
    us_following = session.grab_following(username=user_stalk, amount="full", live_match=True, store_locally=True)

    #salva resultados no banco
    path_json = f"/home/fm/Documents/clinstapy/InstaPy_ws/logs/{insta_user}//relationship_data/{user_stalk}/following" #path to save who you follow
    arquivos_log = os.listdir(path_json)
    data_arquivo_recente = max(datetime.strptime(arquivo[:10], '%d-%m-%Y') for arquivo in arquivos_log)
    nome_arquivo_recente = [arquivo for arquivo in arquivos_log if arquivo.startswith(data_arquivo_recente.strftime('%d-%m-%Y'))][0]
    path_arquivo_recente = os.path.join(path_json, nome_arquivo_recente)
    with open(path_arquivo_recente) as json_file:
        data = json.load(json_file)
    df1 = pd.DataFrame({'usuario':data, 'seguidor':user_stalk, 'data_informacao':datetime.now()})
    df1.to_sql(name = 'connections', con = con_net_prof, if_exists='append', index=False)

#grab_seguidores(session,insta_user,insta_user,con_net_prof)
    
"""

judas_users =  [following for following in own_following if following not in own_followers] #users that you follow but don't follow you back
target_users = [follower for follower in us_followers if follower not in own_following] #user that don't follow you, but follow the user you are stalking

#configurações sessão
session.set_do_like(enabled=True, percentage=32)

session.set_user_interact(amount=4,
				 percentage=80,
                  randomize=True,
                   media='Photo')

"""
