import os
from instapy import InstaPy
from instapy import set_workspace
from instapy import Settings
from instapy.database_engine import get_database
import sqlite3
import pandas as pd
import numpy as np
import datetime


#Parametrização
path_script = '/home/fm/Documents/clinstapy'
wsinstapy_folder = r'/home/fm/Documents/clinstapy/instapy_ws'
dbinstapy_folder = r'/home/fm/Documents/clinstapy/instapy_db'
browser_profile_path = r'/home/fm/Documents/clinstapy/firefox_clin_profile'
path_net_profiles = r'/home/fm/Documents/clinstapy/profiles_network.db'
                     
insta_acc_id = #databasename
insta_user = #youruser
insta_psw = #password
user_stalk = #someone you wanna stalk

set_workspace(os.path.join(path_script,wsinstapy_folder))
Settings.db_location = os.path.join(path_script,dbinstapy_folder)

#login
session = InstaPy(username=insta_user,
                  password=insta_psw,
                  headless_browser=False,
                  split_db=True,
                  multi_logs=True)#,
                  #browser_profile_path=browser_profile_path)
try:
    session.login()
except:
    print("esses erros foram porque o login foi feito por cookies")

#conexões
path_instapy_db = get_database(make=True)[0]
con_instapy = sqlite3.connect(path_instapy_db)
con_net_prof = sqlite3.connect(path_net_profiles)

p = r'/home/fm/Documents/clinstapy/profiles_network.db'
c = sqlite3.connect(p)
pd.read_sql_query(sql="SELECT * from connections", con = con_net_prof)


#recuperação de cache judas
try:
    judas_users = pd.read_pickle(r'/home/fm/Documents/clinstapy/InstaPy_ws/judas_users_cache.pck')
except FileNotFoundError:
    #consulta
    seguem_clinica = pd.read_sql_query(sql=f"SELECT connections.seguidor FROM connections where usuario={insta_user}",con = con_net_prof)['seguidor'].to_list()
    clinica_segue = pd.read_sql_query(sql=f"SELECT usuario FROM connections where seguidor={insta_user}",con = con_net_prof)['usuario'].to_list()

    #Passiveis de darmos unfollow
    judas_users =  [following for following in clinica_segue if (following not in seguem_clinica)]

    pd.Series(judas_users).to_pickle(r'/home/fm/Documents/clinstapy/InstaPy_ws/judas_users_cache.pck')

#recuperação de cache targets
try:
    em_debito = pd.read_pickle(r'/home/fm/Documents/clinstapy/InstaPy_ws/em_debito_cache.pck')
    seguidores_userstalk = pd.read_pickle(r'/home/fm/Documents/clinstapy/InstaPy_ws/seguidores_userstalk_cache.pck')
except FileNotFoundError:
    #consulta
    seguem_clinica = set(pd.read_sql_query(sql=f"SELECT seguidor FROM connections where usuario={insta_user};",con = con_net_prof)['seguidor'].to_list())
    clinica_segue = set(pd.read_sql_query(sql=f"SELECT usuario FROM connections where seguidor={insta_user}",con = con_net_prof)['usuario'].to_list())

    #passiveis de seguirmos
    #seguem a gente e não seguimos de volta
    em_debito = [user for user in seguem_clinica if user not in clinica_segue]
    #seguem o userstalk
    seguidores_userstalk = pd.read_sql_query(sql=f"SELECT seguidor FROM connections where usuario='{user_stalk}'",con = con_net_prof)['seguidor'].to_list()

#configurações da sessão para evitar block do instagram
session.set_quota_supervisor( 
    enabled = True,
    sleep_after = ["likes", "comments_d", "follows", "unfollows", "server_calls_h"],
    sleepyhead = True,
    stochastic_flow = True,
    notify_me = True,
    peak_likes_hourly = 45,
    peak_likes_daily = 300,
    peak_comments_hourly = 10,
    peak_comments_daily = 100,
    peak_follows_hourly = 40,
    peak_follows_daily = 150,
    peak_unfollows_hourly = 15,
    peak_unfollows_daily = 70,
    peak_server_calls_hourly = ["server_calls_h", 'unfollows_d','follows_h'],
    peak_server_calls_daily = 2500
    )

session.set_user_interact(amount=3,
				 percentage=80,
                  randomize=True,
                   media='Photo')

session.set_skip_users(skip_private=True,
                       private_percentage=100,
                       skip_no_profile_pic=True,
                       no_profile_pic_percentage=100,
                       skip_business=True,
                       skip_non_business=False)


#funções que atualizam o cache


def seguir_us():
    global seguidores_userstalk


    session.follow_by_list(followlist=seguidores_userstalk, times=2, sleep_delay=600, interact=True)
    seguidores_userstalk = seguidores_userstalk[2:]
    pd.Series(seguidores_userstalk).to_pickle(r'/home/fm/Documents/clinstapy/InstaPy_ws/seguidores_userstalk_cache.pck')

def seguir_debito():
    global em_debito

    session.follow_by_list(followlist=em_debito, times=1, sleep_delay=600, interact=True)
    em_debito = em_debito[1:]
    pd.Series(em_debito).to_pickle(r'/home/fm/Documents/clinstapy/InstaPy_ws/em_debito_cache.pck')

def tchau_judas():
    global judas_users

    session.unfollow_users(amount=1, custom_list_enabled=True, custom_list=judas_users, custom_list_param="all", style="RANDOM", unfollow_after=55*60*60, sleep_delay=600)
    judas_users = judas_users[1:]
    pd.Series(judas_users).to_pickle(r'/home/fm/Documents/clinstapy/InstaPy_ws/judas_users_cache.pck')

#Aquisição de dados de follow para banco (analise grafo futura)
def grab_seguindo_cache(session,insta_user,con_net_prof):
    global seguem_clinica
    #pega online
    user_stalk = seguem_clinica[0]

    session.grab_following(username=user_stalk, amount="full", live_match=True, store_locally=True)

    seguem_clinica = seguem_clinica[1:]

    pd.Series(seguem_clinica).to_pickle(r'/home/fm/Documents/clinstapy/InstaPy_ws/seguem_clinica.pck')
    #salva resultados no banco
    path_json = f"/home/fm/Documents/clinstapy/InstaPy_ws/logs/{insta_user}//relationship_data/{user_stalk}/following"
    arquivos_log = os.listdir(path_json)
    data_arquivo_recente = max(datetime.strptime(arquivo[:10], '%d-%m-%Y') for arquivo in arquivos_log)
    nome_arquivo_recente = [arquivo for arquivo in arquivos_log if arquivo.startswith(data_arquivo_recente.strftime('%d-%m-%Y'))][0]
    path_arquivo_recente = os.path.join(path_json, nome_arquivo_recente)
    with open(path_arquivo_recente) as json_file:
        data = json.load(json_file)
    df1 = pd.DataFrame({'usuario':data, 'seguidor':user_stalk, 'data_informacao':datetime.now()})
    df1.to_sql(name = 'connections', con = con_net_prof, if_exists='append', index=False)

funcoes = [seguir_us, seguir_debito,tchau_judas,grab_seguindo_cache]

seguir_us()

np.random.choice(funcoes, p=[0.4,0.3,0.2,0.1])()
