#--------------------------------------------------IMPORT LIBRARIES
import requests, json, urllib
import urllib.request
import yaml
import csv

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
        
    #GET /dashboards #gets all dashboards, API call returns an array of dashboard objects
    def get_all_dashboards(self,fields = ''):
        url = '{}{}'.format(self.host,'dashboards')
        params = {"fields":fields}
        response = self.session.get(url,params=params) #call getting the fields
        
        if response.status_code == requests.codes.ok:
            response_list = response.json()
        
        dashboards = []
        
        for list_item in response_list:
            for key in list_item:
                if key == 'id':
                    dashboards.append(str(list_item['id']))           
        return dashboards
    
    #GET /dashboards/search #searches a dashboard , API call returns an array of dashboard objects
    def search_dashboard(self,dashID,fields =''):
        url = '{}dashboards/search?id={}'.format(self.host,dashID)
        params = {"fields":fields}
        response = self.session.get(url,params=params) #call getting the fields
        
        if response.status_code == requests.codes.ok:
            response_list = response.json()
            
        looks_and_dashboards = []
        
        for dash_obj in response_list:
            for dictionary in dash_obj['dashboard_elements']: #iterating through dashboard_elements which is a list
                if dictionary['look_id'] != None:
                    looks_and_dashboards.append({'dashID':dashID, 'look_id':dictionary['look_id'],'title':dash_obj['title']})
#                     looks_and_dashboards.update({'dashID':dashID, 'look_id':dictionary['look_id'],'title':dash_obj['title']})

        return looks_and_dashboards
    
    #GET /spaces #gets all the spaces
    def get_all_spaces(self,fields=''):
        url = '{}{}'.format(self.host,'spaces')
        params = {"fields":fields}
        response = self.session.get(url,params=params) #call getting the fields
        
        if response.status_code == requests.codes.ok:
            response_list = response.json()
        
        spaces = []
        
        for list_item in response_list:
            for key in list_item:
                if key == 'id' and list_item['is_personal']==False:
                    spaces.append(list_item['id'])           
        return spaces
    
    #GET /spaces/{space_id}/looks 
    def get_looks_in_a_space(self,space_id,fields=''): #returns a list of all looks in a space
        #Building the url that will direct the API
        url = '{}{}/{}/looks'.format(self.host,'spaces',space_id)
        params = {"fields":fields}
        response = self.session.get(url,params=params) #call getting the fields   
        
        if response.status_code == requests.codes.ok:
            response_list = response.json()
            
        #Array meant to store look ids
        looks = []
        
        for list_item in response_list:
            for key in list_item: #the list items are of type dict
                if key == 'id' and list_item['deleted']==False:
                    looks.append(list_item['id'])
        
        return looks
        
    #GET /looks/{look_id}
    def get_look_info(self,look_id,fields=''):
        url = '{}/{}/{}'.format(self.host,'looks',look_id)
        #print(url)
        params = {"fields":fields}
        response = self.session.get(url,params=params) #call getting the fields
        
        if response.status_code == requests.codes.ok:
            response_dict = response.json()
        
        if str(response_dict['space']['name']) not in ['EX: NAME OF SPACE','EX: NAME OF SPACE','EX: NAME OF SPACE','EX: NAME OF SPACE']:
            final_data =[str(response_dict['title']),str(response_dict['description']), str(response_dict['query']['vis_config']['type']),
                        str(response_dict['created_at']), str(response_dict['last_accessed_at']), 'https://aclu.looker.com'+str(response_dict['short_url']), 
                        str(response_dict['space']['name']), str(response_dict['model']['label'])]
        
            #To get the explore for a look
            look_url = response_dict['url'].split('?',1)
            look_url2 = look_url[0]
            look_url3 = look_url2.split('/',3)
            explore = look_url3[3]
            final_data.append(explore)
        
    #         #GET users/{user_id}
    #         #To get user information, make a call to the USER API method based on the user ID of the look
    #         user_url = '{}/{}/{}'.format(self.host,'users',response_dict['user']['id'])
    #         response = self.session.get(user_url)

    #         if response.status_code == requests.codes.ok:
    #             response_dict = response.json()

    #         created_user_name = response_dict['first_name']+" "+response_dict['last_name']
    #         final_data.append(created_user_name)
    
            return final_data
        
        
    def write_fields(file_,list_of_wanted_fields={}): #Meant to write data to the file on look level not overall level 
        
        for item in list_of_wanted_fields:
            file_.write(item+'\t')
        file_.write('\n')
            

#Opening the conig file and instantiating API
f = open('config.yml')
params = yaml.safe_load(f)
f.close()

my_host = params['hosts']['localhost']['host']
my_secret = params['hosts']['localhost']['secret']
my_token = params['hosts']['localhost']['token']
looker = LookerApi(my_token,my_secret,my_host)

csvfile = open('List_Of_Looks_In_All_Spaces.txt','w') 
csvfile.write("Name\tDescription\tType\tCreated At\tLast Accessed At\tLook URL\tIn Space\tIn Model\tIn Explore\tIn Dashboard\tDashboard Link\n")

#GETTING ALL SPACES AND ALL LOOKS
all_looks = []
all_spaces = LookerApi.get_all_spaces(looker)

for space in all_spaces:
    list_of_looks = LookerApi.get_looks_in_a_space(looker,space)
    for look in list_of_looks:
        if list_of_looks != []:
            all_looks.append(look)
            
#GETTING ALL DASHBOARDS AND THEIR LOOKS           
dash_ids = LookerApi.get_all_dashboards(looker)
dash_and_looks = []

for ID in dash_ids:
    if LookerApi.search_dashboard(looker,ID) != []:
        dash_and_looks.append(LookerApi.search_dashboard(looker,ID))  
# print(dash_and_looks)

#FAST SOLUTION FOR CREATING A DATA STRUCTURE ON A LOOK ID LVL. DATA LOOKS LIKE: 
new_dict = dict()
for dash in dash_and_looks:
    for tuple_ in dash: 
        new_dict.setdefault(tuple_['look_id'], set()).add((tuple_['title'],'https://aclu.looker.com/dashboards/'+tuple_['dashID']))

# #-------------------------LONG SOLUTION FOR GETTING INFO IN THIS FORMAT (45 in this ex is a look id) {{45: {'dash_ids': {'14'}, 'title': 'Action form performance'},..}
# #the key 'dash_ids' contains a set meaning no dash_ids added will be repeated. 'title' is of type string

# #1. CREATING SET OF UNIQUE LOOK IDS
# look_set = set([])

# for dash in dash_and_looks:
#     for tuple_ in dash:
#         if tuple_['look_id'] not in look_set:
#             look_set.add(tuple_['look_id'])
# # print(look_set)

# #2. TRANSPOSING INFO FROM DASH_AND_LOOKS
# new_table={}
# for look_id in look_set:
#     new_table[look_id] = {'dash_ids':set([]),'title':''}
    
# # print(new_table)

# #3. POPULATING EMPTY DATA STRUCTURE WITH INFO
# for dash in dash_and_looks:
#     for tuple_ in dash:
# #         print(tuple_['look_id'])
# #         print(new_table[tuple_['look_id']]['dash_ids'])
#         if tuple_['dashID'] not in new_table[tuple_['look_id']]['dash_ids']:
#             new_table[tuple_['look_id']]['dash_ids'].add(tuple_['dashID'])
#             new_table[tuple_['look_id']]['title']=tuple_['title']

# print(new_table)
#--------------------------------------------------------------------------------------------------------------------------

#WRITING THE LOOKS INTO THE FILE
for look in all_looks:
    data = LookerApi.get_look_info(looker,look)
    if data != None:
        if look in new_dict.keys():
            for tuple_ in new_dict[look]:
                for item in tuple_:
                    data.append(item)     
                LookerApi.write_fields(csvfile,data)
        else:
            LookerApi.write_fields(csvfile,data)    
    else:
        if data == None:
            pass
        else:
            print('Error')

csvfile.close()

print('done')