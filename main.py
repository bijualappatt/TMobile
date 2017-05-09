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

#Loop through all repositories of the logged-in user
for repo in github.get_user().get_repos():
    BranchData=[]
    CommitsData=[]

    #   TODO: Check for duplication
    #   TODO: Get Branch and Commit details
    #   TODO: Get Language details
    #   TODO: Get Number of Colloaborators

    #Get all Branches in the repository and create a Separate JSON object
    for branch in repo.get_branches():
        SingleBranch={}
        SingleBranch["BranchName"]=branch.name
        BranchData.append(SingleBranch)

    #Get all commits in the repository and create a Separate JSON object
    for commit in repo.get_commits():
        Comm={}
        Comm["sha"]=commit.sha
        Comm["committerid"]=commit.commit.committer.name
        Comm["name"] = commit.commit.committer.name
        Comm["email"] = commit.commit.committer.email
        Comm["date"] = commit.last_modified
        Comm["message"] = commit.commit.message
        CommitsData.append(Comm)

    RepoData["_id"]=repo.id
    RepoData["RepositoryID"] = repo.id
    RepoData["RepositoryName"] = repo.name
    RepoData["FullName"] = repo.full_name
    RepoData["Description"] = repo.description
    RepoData["OwnerID"] = repo.owner.id
    RepoData["OwnerUserName"] = repo.owner.login
    RepoData["OwnerType"] = repo.owner.type
    RepoData["RepositoryURL"] = repo.url
    RepoData["BranchName"] = BranchData
    RepoData["Commits"] = CommitsData
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
    RepoData["vcs"]='GitHub' #Version Control System Used - GitHub/BitBucket

    db.RepositoryInfo.insert(RepoData)
    #db.RepositoryInfo.insert_one(RepoDataJSON)

# Repo Iteration Loop Ends Here


#TODO : BitBucket Integration


