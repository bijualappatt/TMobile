import pymongo
from github import Github
from bitbucket.bitbucket import  Bitbucket

AUTH_USER='bijualappatt'
AUTH_PASS='Password@123'

MONGODB_SERVER = 'localhost'
MONGODB_PORT = 27017

client = pymongo.MongoClient(MONGODB_SERVER, MONGODB_PORT)
db = client.testDB

github = Github(AUTH_USER, AUTH_PASS)

for repo in github.get_user().get_repos():

    #   TODO: Check for duplication
    #   TODO: Get Branch and Commit details
    #   TODO: Get Language details
    #   TODO: Get Number of Colloaborators

    db.RepositoryInfo.insert_one(
        {"RepositoryID": repo.id,
         "RepositoryName": repo.name,
         "FullName": repo.full_name,
         "Description": repo.description,
         "OwnerID":repo.owner.id,
         "OwnerUserName":repo.owner.login,
         "OwnerType":repo.owner.type,
         "RepositoryURL":repo.url,
         "BranchesURL":repo.branches_url,

         "LanguagesURL":repo.languages_url,
         "CommitsURL":repo.commits_url,
         "IssuesURL": repo.issues_url,
         "GitURL": repo.git_url,
         "CloneURL": repo.clone_url,
         "CreatedAt": repo.created_at,
         "UpdatedAt":repo.updated_at,
         "Size":repo.size,
         "Language":repo.language,
         "DefaultBranch":repo.default_branch,
         "HassIssues":repo.has_issues,
         "IsPrivate":repo.private,
         #"IsPrivate": repo.private
         }
    )

#TODO : BitBucket Integration


