import pymongo
from bson import json_util
import json
from github import Github

from bitbucket.bitbucket import  Bitbucket

AUTH_USER='bijualappatt'
AUTH_PASS='Password@123'

MONGODB_SERVER = 'localhost'
MONGODB_PORT = 27017

client = pymongo.MongoClient(MONGODB_SERVER, MONGODB_PORT) #Initialize MongoClient
db = client.testDB
RepoData={}

github = Github(AUTH_USER, AUTH_PASS)

#Loop through all repositories belongs to the logged-in user
print('Getting Repository Information and updating database...please wait')
for repo in github.get_user().get_repos():
    BranchData=[]
    CommitsData=[]

    #   TODO: Get CommitterID correctly and replace
    #   TODO: Get Language details
    #   TODO: Get Number of Colloaborators
    #   TODO: Get Full Path of each file in the repository

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

    LangData={}
    LangData=repo.get_languages()

    RepoData["_id"]=repo.id #Generate Unique ID and use it instead of RepoID
    RepoData["RepositoryID"] = repo.id
    RepoData["RepositoryName"] = repo.name
    RepoData["FullName"] = repo.full_name
    RepoData["Description"] = repo.description
    RepoData["OwnerID"] = repo.owner.id
    RepoData["OwnerUserName"] = repo.owner.login
    RepoData["OwnerType"] = repo.owner.type
    RepoData["RepositoryURL"] = repo.url
    RepoData["BranchName"] = BranchData     # Branches Array
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

    # Replace the RepositoryData if exists, otherwise inserts
    #db.RepositoryInfo.update({'_id':RepoData["_id"]},RepoData,upsert=True)
    db.RepositoryInfo.update({'RepositoryID': RepoData["RepositoryID"]}, RepoData, upsert=True)
    #db.RepositoryInfo.insert_one(RepoData)


# Repo Iteration Loop Ends Here
print('Done!')


#TODO : BitBucket Integration


