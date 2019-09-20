#--------------------------------------------------IMPORT LIBRARIES
import requests, json, urllib
import urllib.request
import yaml
from pprint import pprint as pp
# import logging, time
# import re
# import pandas as pd
# from io import StringIO
# import io as stringIOModule
# from datetime import datetime

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#-------------------------------------------------------METHODS
class LookerApi(object):
    def __init__(self, token, secret, host):
            
            self.token = token
            self.secret = secret
            self.host = host

            self.session = requests.Session()
            self.session.verify = False
            self.session.trust_env = False

            self.auth()

    def auth(self):
        url = '{}{}'.format(self.host,'login')
        params = {'client_id':self.token,
                  'client_secret':self.secret}
        r = self.session.post(url,params=params)
        access_token = r.json().get('access_token')
        # print(access_token)
        head = {'Authorization': 'token {}'.format(access_token)}
        self.head = head
        self.session.headers.update(head)
   
    # GET /lookml_models
    def get_all_models(self,fields=''):
        url = '{}{}'.format(self.host,'lookml_models')
        params = {"fields":fields}
        response = self.session.get(url,params=params) #call getting the fields
        if response.status_code == requests.codes.ok:
            return response.json()  
        
    # GET /lookml_models/{{NAME}}
    def get_model(self,model_name=None,fields=''):
        url = '{}{}/{}'.format(self.host,'lookml_models', model_name)
        params = {"fields":fields}
        response = self.session.get(url,params=params) #call getting the fields
        if response.status_code == requests.codes.ok:
            return response.json()  
        
    #API call to pull in metadata about fields in a particular explore    
    def get_explore(self,lookml_model_name,explore_name,fields=''):
        #Building the url that will direct the API
        url = '{}{}/{}/{}/{}?'.format(self.host,'lookml_models',lookml_model_name,'explores',explore_name)
        params = {"fields":fields}
        response = self.session.get(url,params=params) #call getting the fields
        if response.status_code == requests.codes.ok:
            return response.json()
        
    def insert_fields(self,explore,fields,model_name=''):
        #explore is the json file created by the get_explore method
        #fields is the filter
        
        #List of the fields we are interested in pulling
        wanted_fields = ['hidden','view_label','description','label_short',
                         'name','field_group_label','type','primary_key','sql','suggest_exlpore']
        
        explore_fields = explore['fields'] #explore_fields is "fields": {"dimensions": [{'align': 'right',..}], "measures":[]
        
        try:
            connection_name = explore["allowed_db_connection_names"]
        except:
            connection_name = ''
            
        for item_dict in explore_fields[fields]: #for item in either dimensions or measures
            print(explore['name']+' '+model_name)
            print(item_dict)
#             for metadata in item_dict:
#                 return item_dict[metadata]


#-----------------------------------------------------Opening the conig file and extracting login info
f = open('config.yml')
params = yaml.safe_load(f)
f.close()

my_host = params['hosts']['localhost']['host']
my_secret = params['hosts']['localhost']['secret']
my_token = params['hosts']['localhost']['token']

#----------------------------------------------------instant of the API
looker = LookerApi(my_token,my_secret,my_host)
#------------------------------------------------------Get all models
models = looker.get_all_models() 
# pp(models) #pretty print the models

for model in models:
    model_name = model['name'] 
    
    #-------------------------------------------------json of explores in a model
    model_def = looker.get_model(model_name) 
    #pp(model_def)
    
    #-------------------------------------------------Get single explore
    for explore_def in model_def['explores']: 
        explore = looker.get_explore(model_name,explore_def['name']) #json of metadata of an explore
        
        #pp(explore)
        
    #------------------------------------------------parse data
        try:
            print(looker.insert_fields(explore,'measures',model_name))
        except:
            print("Problem measure fields in "+explore_def['name'])
