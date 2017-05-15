# User : vinaykumaran
# Pass : ustglobal@123

import pymongo
from bson import json_util
from github import Github

from bitbucket.bitbucket import Bitbucket

import requests
import json
from datetime import datetime
from datetime import time
from datetime import date
from subprocess import call
from pprint import pprint

class Payload(object):
    def __init__(self, j):
        self.__dict__ = json.loads(j)

#Deleete contents of folder where we download the repoository for running CLOC
def CleanupSrc():
    REPO_TEMP = 'rd /s /q  .\src'
    call(REPO_TEMP,shell=True)
    call('mkdir .\src',shell=True)

#Clone Repository and run CLOC
def CloneGitRepo(Type, RepoName,CloneURL):
    #Clone Repository locally
    if Type=="GITHUB":
        PROC_PATH='.\Git\cmd\git.exe -C .\src clone ' + CloneURL + ' --progress --recursive '
        call(PROC_PATH, shell=True)
    else:
        PROC_PATH = '.\Git\cmd\git.exe -C .\src clone ' + CloneURL + ' --progress --recursive '

        #call(PROC_PATH, shell=True)

    #pathTree='rd /s /q  .\src'+'\\'+RepoName
    #call(pathTree, shell=True)

    #Run CLOC on local Repository and return JSON data.
    if Type == "GITHUB":
        CLOC_PATH = '.\\bin\\cloc172.exe .\\src\\' + RepoName + ' --json > .\\src\\' + RepoName + '.clo'
    else:
        CLOC_PATH = '.\\bin\\cloc172.exe .\\bbucket\\' + RepoName + ' --json > .\\src\\' + RepoName + '.clo'
    call(CLOC_PATH,shell=True) #Run CLOC and write output to file

    #Read JSON from file
    with open('.\\src\\'+RepoName+'.clo') as json_data:
        data = json.load(json_data)
    return data #Contains JSON string data

###################################################################################################################

# AUTH_USER='bijualappatt'
# AUTH_PASS='Password@123'

AUTH_USER='vinaykumaran'
AUTH_PASS='ustglobal@123'

MONGODB_SERVER = 'localhost'
MONGODB_PORT = 27017

client = pymongo.MongoClient(MONGODB_SERVER, MONGODB_PORT) #Initialize MongoClient
db = client.TMobile
RepoData={}

github = Github(AUTH_USER, AUTH_PASS)

#   TODO: Get Full Path of each file in the repository

#Loop through all repositories belongs to the logged-in user
print('Getting GitHub Repository Information and updating database...please wait')

CleanupSrc()

for repo in github.get_user().get_repos():
    BranchData=[]
    CommitsData=[]
    Contributors=[]
    IssuesData=[]

    #Get all Branches in the repository and create a Separate JSON object
    for branch in repo.get_branches():
        SingleBranch={} #Initialize a JSON string which holds a single Branch
        SingleBranch["BranchName"]=branch.name
        BranchData.append(SingleBranch) #Add the Branch to the Branches Arrary for the current repository

    #Get all commits in the repository and create a Separate JSON object
    for commit in repo.get_commits():
        Comm={} #Initialize a JSON string which holds single commit.
        Comm["hash"]=commit.sha
        # Comm["committerid"]=commit.committer.login
        Comm["committerid"] = commit.commit.committer.email
        Comm["name"] = commit.commit.committer.name
        Comm["email"] = commit.commit.committer.email
        #Comm["date"] = commit.last_modified
        Comm["date"] = datetime.now()
        #print(commit.last_modified)
        #datestr=datetime.strftime(commit.last_modified,'%a, %d %b %H:%M:%S %Z')
        #print(datetime.strptime(commit.last_modified, '%y-%m-%d %M:%H%S'))
        Comm["message"] = commit.commit.message
        CommitsData.append(Comm) # Add the commit to the Commits Array for the current repository

    #Get Language information
    LangData={}
    LangData=repo.get_languages()

    for contrib in repo.get_contributors():
        Contrib={}
        Contrib["id"]=contrib.id
        Contrib["login"] = contrib.login
        #Contrib["type"] = contrib.type
        Contributors.append((Contrib))

    if(repo.has_issues==True): #If Issues feature is activated on repository
        for issue in repo.get_issues():
            #print (issue)
            Issue={}
            Issue["id"]=issue.id
            Issue["title"] = issue.title
            Issue['CreatedON']=issue.created_at
            #Issue["user"] = issue.user.login
            IssuesData.append(Issue)
    else:
        Issues=[]

    RepoData["_id"]=repo.id #Generate Unique ID and use it instead of RepoID
    RepoData["RepositoryID"] = repo.id
    RepoData["RepositoryName"] = repo.name
    RepoData["FullName"] = repo.full_name
    RepoData["Description"] = repo.description
    RepoData["OwnerID"] = repo.owner.id
    RepoData["OwnerUserName"] = repo.owner.login
    RepoData["OwnerType"] = repo.owner.type
    RepoData["RepositoryURL"] = repo.url
    RepoData["Branch"] = BranchData     # Branches Array
    RepoData["Commits"] = CommitsData       #Commits Array
    RepoData["LanguagesURL"] = repo.languages_url
    RepoData["CommitsURL"] = repo.commits_url
    RepoData["IssuesURL"] = repo.issues_url
    RepoData["GitURL"] = repo.git_url
    RepoData["CloneURL"] = repo.clone_url
    RepoData["CreatedAt"] = repo.created_at
    RepoData["UpdatedAt"] = repo.updated_at
    RepoData["Size"] = repo.size
    RepoData["Language"] = repo.language
    RepoData["DefaultBranch"] = repo.default_branch
    RepoData["HasIssues"] = repo.has_issues
    RepoData["IsPrivate"] = repo.private
    RepoData["vcs"]='GITHUB' #Version Control System Used - GitHub/BitBucket
    RepoData["LanguageExtInfo"]=LangData
    RepoData["Contributors"]=Contributors

    LangJSON=CloneGitRepo('GITHUB', repo.name, RepoData["CloneURL"])
    RepoData['LanguageMetrics']=LangJSON
    # RepoData["Issues"] = IssuesData
    # Replace the RepositoryData if exists, otherwise inserts
    #db.RepositoryInfo.update({'_id':RepoData["_id"]},RepoData,upsert=True)
    db.RepositoryInfo.update({'RepositoryID': RepoData["RepositoryID"]}, RepoData, upsert=True)
    #db.RepositoryInfo.insert_one(RepoData)

# Repo Iteration Loop Ends Here
print('Done!')


# BitBucket Integration
print('Getting BitBucket Repository Information and updating database...please wait')
# AUTH_USER='bijualappatt'
# AUTH_PASS='Password#123'

AUTH_USER='vinaynanabala@gmail.com'
AUTH_PASS='ustglobal@123'


bb = Bitbucket(AUTH_USER, AUTH_PASS)
success, repositories = bb.repository.all()
#LangJSON = {}
if(success):
    for repo in repositories:
        BranchData.clear()
        CommitsData.clear()
        Contributors.clear()
        IssuesData.clear()

        Resp = requests.get('https://api.bitbucket.org/2.0/user',
                            auth=(AUTH_USER, AUTH_PASS),
                            headers={'content-type': 'application/json'})

        if (Resp.status_code == 200):
            u=json.loads(Resp.text)

            bbUser=u['username']
            Resp = requests.get('https://api.bitbucket.org/2.0/repositories/' + bbUser + '/' + repo['slug'],
                                auth=(AUTH_USER, AUTH_PASS),
                                headers={'content-type': 'application/json'})
            if(Resp.status_code==200):
                pl = Payload(Resp.text)
                ow = Payload(json.dumps(pl.owner)) #Get owner information json and serialize
                ln = Payload(json.dumps(pl.links))
                br = Payload(json.dumps(pl.mainbranch))

                #Get Branch information by calling the REST api
                BranchesJSONArray = requests.get(ln.branches['href'],
                                            auth=(AUTH_USER, AUTH_PASS),
                                            headers={'content-type': 'application/json'})
                if(BranchesJSONArray.status_code==200):
                    BranchJSON=json.loads(BranchesJSONArray.text)
                    for BranchDet in BranchJSON['values']:
                        SingleBranch = {}  # Initialize a JSON string which holds a single Branch
                        SingleBranch["BranchName"] = BranchDet['name']
                        BranchData.append(SingleBranch)  # Add the Branch to the Branches Arrary for the current repository

                RepoData["_id"] = pl.uuid
                RepoData["RepositoryID"] = pl.uuid
                RepoData["RepositoryName"] = repo['slug']
                RepoData["FullName"] = repo['name']
                RepoData["Description"] = repo['description']
                RepoData["OwnerID"] = repo['owner']
                RepoData["OwnerUserName"] = ow.display_name
                RepoData["OwnerType"] = ow.type
                RepoData["RepositoryURL"] = ln.self['href']
                RepoData["Branch"] = BranchData  # Branches Array

                # Get Commit information by calling the REST api
                CommitsJSONArray = requests.get(ln.commits['href'],
                                            auth=(AUTH_USER, AUTH_PASS),
                                            headers={'content-type': 'application/json'})

                if(CommitsJSONArray.status_code==200):
                    CommitJSON=json.loads(CommitsJSONArray.text)
                    for CommitDet in CommitJSON['values']:

                        Comm = {}  # Initialize a JSON string which holds single commit.
                        #print(CommitDet)
                        Comm["hash"] = CommitDet['hash']
                        try:
                            Comm["committerid"] = CommitDet['author']['user']['username']
                        except:
                            Comm["committerid"] = 'Unknown'
                        try:
                            Comm["name"] = CommitDet['author']['user']['display_name']
                        except:
                            Comm["name"] = "Not Available"
                        Comm["email"] = CommitDet['author']['raw']
                        #Comm["date"] = CommitDet['date']
                        Comm["date"] = datetime.now()
                        Comm["message"] = CommitDet['message']
                        CommitsData.append(Comm)  # Add the commit to the Commits Array for the current repository

                        Contrib = {}
                        try:
                            Contrib["id"] = CommitDet['author']['user']['uuid']
                        except:
                            Contrib["id"] = 'Unknown'
                        try:
                            Contrib["login"] = CommitDet['author']['user']['username']
                        except:
                            Contrib["login"] = 'Unknown'

                        # Contrib["type"] = contrib.type
                        Contributors.append((Contrib)) #All committors considered as contributors.

                    #Remove duplicate committers to make it a contributor list
                    Contribs=[] #Holds unique Contributors
                    for element in Contributors:
                        if element not in Contribs:
                            Contribs.append(element)

                RepoData["Commits"] = CommitsData  # Commits Array
                RepoData["LanguagesURL"] = ''
                RepoData["CommitsURL"] = ln.commits['href']
                RepoData["IssuesURL"] = ln.self['href'] +'/issues'
                RepoData["GitURL"] = ln.clone[1]['href']
                RepoData["CloneURL"] = ln.clone[0]['href']

                RepoData["CreatedAt"] = repo['created_on']
                RepoData["UpdatedAt"] = repo['last_updated']
                #RepoData["CreatedAt"] = cro
                #RepoData["UpdatedAt"] = cro

                Issues=[]
                if(repo['has_issues']==True): #If Issues feature is activated on repository
                    # Get iSSUE information by calling the REST api
                    IssuesJSONArray = requests.get(RepoData["IssuesURL"],
                                            auth=(AUTH_USER, AUTH_PASS),
                                            headers={'content-type': 'application/json'})
                    if(IssuesJSONArray.status_code==200):
                        IssueJSON = json.loads(IssuesJSONArray.text)
                        for IssueDet in IssueJSON['values']:
                            Issue = {}
                            Issue["Id"] = IssueDet['id']
                            Issue["Title"] = IssueDet['title']
                            Issue["CreateOn"] = IssueDet['created_on']
                            #Issue["CreatedBy"] = 'Not Available'
                            IssuesData.append(Issue)  # Add the commit to the Commits Array for the current repository

                RepoData["Size"] = repo['size']
                RepoData["Language"] = repo['language']
                RepoData["DefaultBranch"] = br.name
                RepoData["HasIssues"] = repo['has_issues']
                RepoData["IsPrivate"] = repo['is_private']
                RepoData["vcs"] = 'BITBUCKET'  # Version Control System Used - GitHub/BitBucket
                #RepoData["LanguageExtInfo"] = LangData #TODO : Get Language Info
                RepoData["Contributors"] = Contribs

                #LangJSON = CloneGitRepo('BITBUCKET', repo['slug'], RepoData["GitURL"])
                LangJSON = CloneGitRepo('BITBUCKET', 'BBTMobile', RepoData["GitURL"])

                RepoData['LanguageMetrics'] = LangJSON
                # RepoData["Issues"] = IssuesData
                db.RepositoryInfo.update({'RepositoryID': RepoData["RepositoryID"]}, RepoData, upsert=True)
            else:
                print('Failed getting BitBucket data...')
        else:
            print('Login Failed')
else:
    print('Failed getting BitBucket data...')
print("Done!")
