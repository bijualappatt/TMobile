import pymongo
from bson import json_util
from github import Github

from bitbucket.bitbucket import Bitbucket

import requests
import json


class Payload(object):
    def __init__(self, j):
        self.__dict__ = json.loads(j)

AUTH_USER='bijualappatt'
AUTH_PASS='Password@123'

MONGODB_SERVER = 'localhost'
MONGODB_PORT = 27017

client = pymongo.MongoClient(MONGODB_SERVER, MONGODB_PORT) #Initialize MongoClient
db = client.testDB
RepoData={}

github = Github(AUTH_USER, AUTH_PASS)

#   TODO: Get Full Path of each file in the repository

#Loop through all repositories belongs to the logged-in user
print('Getting GitHub Repository Information and updating database...please wait')
for repo in github.get_user().get_repos():
    BranchData=[]
    CommitsData=[]
    Contributors=[]

    #Get all Branches in the repository and create a Separate JSON object
    for branch in repo.get_branches():
        SingleBranch={} #Initialize a JSON string which holds a single Branch
        SingleBranch["BranchName"]=branch.name
        BranchData.append(SingleBranch) #Add the Branch to the Branches Arrary for the current repository

    #Get all commits in the repository and create a Separate JSON object
    for commit in repo.get_commits():
        Comm={} #Initialize a JSON string which holds single commit.
        Comm["hash"]=commit.sha
        Comm["committerid"]=commit.commit.committer.name
        Comm["name"] = commit.commit.committer.name
        Comm["email"] = commit.commit.committer.email
        Comm["date"] = commit.last_modified
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
    RepoData["HassIssues"] = repo.has_issues
    RepoData["IsPrivate"] = repo.private
    RepoData["vcs"]='GITHUB' #Version Control System Used - GitHub/BitBucket
    RepoData["LanguageExtInfo"]=LangData
    RepoData["Contributors"]=Contributors

    # Replace the RepositoryData if exists, otherwise inserts
    #db.RepositoryInfo.update({'_id':RepoData["_id"]},RepoData,upsert=True)
    db.RepositoryInfo.update({'RepositoryID': RepoData["RepositoryID"]}, RepoData, upsert=True)
    #db.RepositoryInfo.insert_one(RepoData)

# Repo Iteration Loop Ends Here
print('Done!')


# BitBucket Integration
print('Getting BitBucket Repository Information and updating database...please wait')
bb = Bitbucket(AUTH_USER, AUTH_PASS)
success, repositories = bb.repository.all()
if(success):
    for repo in repositories:
        BranchData.clear()
        CommitsData.clear()
        Contributors.clear()

        Resp = requests.get('https://api.bitbucket.org/2.0/repositories/bijualappatt/' + repo['slug'],
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
                    #print(CommitDet['author']['user']['username'])

                    Comm = {}  # Initialize a JSON string which holds single commit.
                    Comm["hash"] = CommitDet['hash']
                    Comm["committerid"] = CommitDet['author']['user']['username']
                    Comm["name"] = CommitDet['author']['user']['display_name']
                    Comm["email"] = CommitDet['author']['raw']
                    Comm["date"] = CommitDet['date']
                    Comm["message"] = CommitDet['message']
                    CommitsData.append(Comm)  # Add the commit to the Commits Array for the current repository

            RepoData["Commits"] = CommitsData  # Commits Array
            RepoData["LanguagesURL"] = ''
            RepoData["CommitsURL"] = ln.commits['href']
            RepoData["IssuesURL"] = ln.self['href'] +'/issues'
            RepoData["GitURL"] = ln.clone[0]['href']
            RepoData["CloneURL"] = ln.clone[0]['href']
            RepoData["CreatedAt"] = repo['created_on']
            RepoData["UpdatedAt"] = repo['last_updated']
            RepoData["Size"] = repo['size']
            RepoData["Language"] = repo['language']
            RepoData["DefaultBranch"] = br.name
            RepoData["HassIssues"] = repo['has_issues']
            RepoData["IsPrivate"] = repo['is_private']
            RepoData["vcs"] = 'BITBUCKET'  # Version Control System Used - GitHub/BitBucket
            #RepoData["LanguageExtInfo"] = LangData
            #RepoData["Contributors"] = Contributors

            db.RepositoryInfo.update({'RepositoryID': RepoData["RepositoryID"]}, RepoData, upsert=True)
        else:
            print('Failed getting BitBucket data...')
else:
    print('Failed getting BitBucket data...')
print("Done!")
