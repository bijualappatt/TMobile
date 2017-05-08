import pymongo
from github import Github

#from pybitbucket import bitbucket

MongoDBServer = 'localhost'
MongoDBPort = 27017

client = pymongo.MongoClient(MongoDBServer, MongoDBPort)
db = client.testDB

github = Github('bijualappatt', 'Password@123')
# user = github.get_user()

for repo in github.get_user().get_repos():
    print(repo.id)
    print(repo.name)
    print(repo.full_name)
    print(repo.description)
    print(repo.clone_url)
    print(repo.downloads_url)
    print(repo.owner)

    # db.RepositoryInfo.insert_one(
    #     {"RepositoryID": repo.id,
    #      "RepositoryName": repo.name,
    #      "RepoFullName": repo.full_name,
    #      "RepoDescription": repo.description,
    #      "CloneURL": repo.clone_url,
    #      "DownloadURL": repo.downloads_url
    #      }
    # )




