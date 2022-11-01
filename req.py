from bs4 import BeautifulSoup
import requests, math,flask
from art import tprint
import maskpass

# app = Flask(__name__)
# app.secret_key = '' #ENV

def return_attendance(username,pwd):
    try:
        session = requests.Session()
        r = session.get('https://ecampus.psgtech.ac.in/studzone2/')
        loginpage = session.get(r.url)
        soup = BeautifulSoup(loginpage.text,"html.parser")
        viewstate = soup.select("#__VIEWSTATE")[0]['value']
        eventvalidation = soup.select("#__EVENTVALIDATION")[0]['value']
        viewstategen = soup.select("#__VIEWSTATEGENERATOR")[0]['value']
        item_request_body  = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': viewstategen,
            '__EVENTVALIDATION': eventvalidation,
            'rdolst': 'S',
            'txtusercheck': username,
            'txtpwdcheck': pwd,
            'abcd3': 'Login',
        }
        response = session.post(url=r.url, data=item_request_body, headers={"Referer": r.url})

        if response.status_code == 200:
            defaultpage = 'https://ecampus.psgtech.ac.in/studzone2/AttWfPercView.aspx'
            page = session.get(defaultpage)
            soup = BeautifulSoup(page.text,"html.parser")
            data = []
            column = []
            table = soup.find('table', attrs={'class':'cssbody'})
            if table == None:
                message = str(soup.find('span', attrs={'id':'Message'}))
                if "On Process" in message:
                    return "Table is being updated"
            try:
                rows = table.find_all('tr')
                for index,row in enumerate(rows):
                    cols = row.find_all('td')
                    cols = [ele.text.strip() for ele in cols]
                    data.append([ele for ele in cols if ele])
                return data,session
            except:
                return "Invalid password"
        else:
            return "Try again after some time"
    
    except:
        return "Try again after some time"


def return_timetable(session):
    defaultpage = 'https://ecampus.psgtech.ac.in/studzone2/AttWfStudTimtab.aspx'
    page = session.get(defaultpage)
    soup = BeautifulSoup(page.text,"html.parser")
    data = []
    table = soup.find('table', attrs={'id':'TbCourDesc'})
    if table == None:
        return {"error" : "no data"}
    try:
        rows = table.find_all('tr')
        for index,row in enumerate(rows):
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            data.append([ele for ele in cols if ele]) 
        class_id = {}
        for i in range(1,len(data)):
            class_id[data[i][0]] = data[i][1]
        return class_id
    except:
        return {"error" : "no data"}

def data_json(data):
    index_required = [0,1,2,4,7,8,9]
    response_data = []
    threshold = 0.75
    for item in range(1,len(data)):
        item = data[item]
        temp = {}
        temp['Course Code'] = item[index_required[0]]
        j = 1
        temp['Total Hours'] = int(item[index_required[j]]) #1
        j += 1
        temp['Exemption Hours'] = int(item[index_required[j]]) #2
        j += 1
        temp['Total Present'] = int(item[index_required[j]]) #4
        temp['Total Present'] += temp['Exemption Hours']
        j += 1
        temp['Attendance Percentage'] = int(item[index_required[j]]) 
        if temp['Attendance Percentage'] <= 75: temp['To Attend'] = math.ceil((threshold*temp['Total Hours'] - temp['Total Present'])/(1-threshold))
        else: temp['Can Bunk'] = math.floor((temp['Total Present']-(threshold*temp['Total Hours']))/(threshold))
        j += 1
        temp['From'] = (item[index_required[j]])
        j += 1
        temp['To'] = (item[index_required[j]])
        response_data.append(temp)
    return response_data

if __name__ == "__main__":
    tprint("Welcome    to    the    CLI    Chatbot")
    print("Logging In")
    username, pwd = '', ''
    with open('ENV.txt', 'r') as f:
        credE = f.readline().split()
        username, pwd = credE[0], credE[1]
    username = input("What is your username?\n")
    print("What is your password?")
    pwd = maskpass.askpass(mask = "*")
    try:
        table,session = return_attendance(username,pwd)
    except:
        table = return_attendance(username,pwd)
    print("Logged in. Starting table view.")
    tprint("What  would  you  like  to  see?")
    userChoice = int(input("1. Attendance\n2. TimeTable\n"))
    if(userChoice == 1):
        if table != "Invalid password" and table != "Try again after some time" and table != "Table is being updated":        
            res = data_json(table)
            super_dict = {}
            for d in res:
                for k, v in d.items():
                    super_dict.setdefault(k, []).append(v)
            for k, v in super_dict.items():
                itList = [0] * 8
                for i in range(len(v)):
                    itList[i] = str(v[i])
                print("{:<30} {:<20} {:<20} {:<20} {:<20} {:<20} {:<20} {:<20} {:<20}".format(k, itList[0], itList[1], itList[2], itList[3], itList[4], itList[5], itList[6], itList[7]))
        else: print("Error!", table)
    elif(userChoice == 2):
        time_table = return_timetable(session)
        for i, j in time_table.items():
            print(i, '\t:\t', j)