from flask import Flask, jsonify ,render_template , request , redirect
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client ["devops_dashboard"]

projects_collections = db["projects"]
deployments_collections = db["deployments"]


if projects_collections.count_documents({}) == 0:

    projects_collections.insert_many([
        {
            "id": 1,
            "name": "DevOps Dashboard",
            "status": "Running",
            "environment": "Development"
        },
        {
            "id": 2,
            "name": "Cloud Deployment",
            "status": "Completed",
            "environment": "Production"
        }
    ])


if deployments_collections.count_documents({}) == 0:

    deployments_collections.insert_one({
        "version": "v1.0.0",
        "environment": "Production",
        "status": "Successful"
    })



@app.route("/")
def home():
    projects = list(projects_collections.find({},{"_id":0}))
    deployments = list(deployments_collections.find({},{"_id":0}))
    total_projects = projects_collections.count_documents({})
    total_deployments = deployments_collections.count_documents({})
    successful_deployments = deployments_collections.count_documents({
        "status":"Successful"
    })
    failed_deployments = deployments_collections.count_documents({
            "status":"Failed"
        })
                                                
    return render_template ("index.html", projects = projects , deployments = deployments , 
                            total_projects = total_projects, total_deployments = total_deployments,
                            successful_deployments= successful_deployments,failed_deployments= failed_deployments)

 

@app.route("/health")
def health():
    return jsonify({
        "status": "Healthy"
    })


@app.route("/projects")
def get_projects():
    projects = list(projects_collections.find({},{"_id":0}))
    return jsonify(projects)


@app.route("/deployments")
def get_deployments():
     deployments = list(deployments_collections.find({},{"_id":0}).sort("deployed_at", -1))
     return jsonify(deployments)


@app.route("/create_project", methods = ["POST"])
def create_project() :
    name = request.form["name"]
    environment = request.form ["environment"]
    new_project= {
        
        "name" : name,
        "status": "Created",
        "environment": environment,

    }
    projects_collections.insert_one(new_project)

    return redirect("/")

@app.route("/deploy", methods = ["POST"])
def deploy():
    project_name = request.form ["project_name"]
    environment = request.form ["environment"]
    version = request.form ["version"]
    status = request.form["status"]

    deployment = {
        "project_name" : project_name ,
        "environment" : environment ,
        "version" : version ,
        "status" : status ,
        "deployed_at": datetime.now()

         
    }

    deployments_collections.insert_one(deployment)

    if status == "Successful":

      projects_collections.update_one({
        "name": project_name,
        "environment": environment
       },
     {
        "$set":{
            "status": "Deployed"
        }

      })

    else:
         projects_collections.update_one({
                "name": project_name,
                "environment": environment
               },
             {
                "$set":{
                    "status": "Deployment Failed"
                }
        
              })
        

    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug = True )