from flask import Flask, request, jsonify, abort
from flask import send_from_directory, render_template
from io import BytesIO
from werkzeug.utils import secure_filename
import os
from vane import config, vane_cli
import shutil
from flask_cors import CORS
import contextlib
import json
import glob
import time


# create and configure the app
app = Flask(__name__, template_folder="templates", static_folder="assets")
CORS(app)

app.config["UPLOAD_FOLDER"] = "workspace"
app.config["TEST_DIRECTORY"] = "test"

# global variables for saving the temporary path of the uploaded test files
DEFINITION_FILE_PATH = ""
DUTS_FILE_PATH = ""
# global variables for saving the temporary path of the workspace and its name
CUR_WORKSPACE_NAME = ""
CUR_WORKSPACE_PATH = ""


# A page (an endpoint) to show report.html from current workspace test
# http://127.0.0.1:5000/
@app.route("/")
def index():
    return render_template("report.html")


# Endpoint for create a workspace (called when frontend submits a create form)
@app.route("/work_space", methods=["POST"])
def worksapce():
    global CUR_WORKSPACE_NAME
    global CUR_WORKSPACE_PATH

    name = request.form.get("work-space")
    CUR_WORKSPACE_NAME = name

    workspace_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), app.config["UPLOAD_FOLDER"], name
    )
    CUR_WORKSPACE_PATH = workspace_path
    # create a directory for the workspace
    try:
        if os.path.exists(workspace_path) == False:
            os.mkdir(workspace_path)
            print("Current Workspace Path: ", CUR_WORKSPACE_PATH)
            return "Create workspace successfully"
    except:
        # what if a workspace has already existed
        print("Folder %s already exists" % workspace_path)
        CUR_WORKSPACE_PATH = ""
        return abort(409, "Folder already exists")


# Endpoint for save the current created workspace in vane page
# write the saved workspace name in 'workspace.json' file
@app.route("/save_work_space", methods=["PUT"])
def save_workspace():
    global CUR_WORKSPACE_NAME
    global CUR_WORKSPACE_PATH

    with open("workspace.json", "r+") as file:
        # load existing data into a dict
        file_data = json.load(file)
        # add the workspace name to the json file
        if CUR_WORKSPACE_NAME in file_data["name"]:
            # if the user clicked the save button twice
            print("workspace has already been saved!")
            return jsonify("Workspace has already been saved before!")
        else:
            print("Current workspace saved: ", CUR_WORKSPACE_NAME)
            file_data["name"].append(CUR_WORKSPACE_NAME)
            # Sets file's current position at offset
            file.seek(0)
            json.dump(file_data, file)
            # clear all global variables related to this saved workspace
            CUR_WORKSPACE_NAME, CUR_WORKSPACE_PATH = "", ""
            DEFINITION_FILE_PATH, DUTS_FILE_PATH = "", ""
            return jsonify("Save Workspace sucessfully!")


# Endpoint for return the workspace.json including the all saved workspace name.
@app.route("/get_work_space", methods=["GET"])
def get_work_space():
    try:
        root_dir = os.path.dirname(os.path.abspath(__file__))
        return send_from_directory(directory=root_dir, path="workspace.json", mimetype=None)
    except FileNotFoundError:
        abort(404)


# Endpoint for delete a workspace, used when user go to a new test without saving the current workspace.
# Also used to refresh page: clear the global CUR_WORKSPACE_PATH, CUR_WORKSPACE_NAME
@app.route("/delete_work_space", methods=["DELETE"])
def delete_workspace():
    global CUR_WORKSPACE_PATH
    global CUR_WORKSPACE_NAME

    path = CUR_WORKSPACE_PATH

    try:
        # clear global variables related to current workspace
        CUR_WORKSPACE_NAME = ""
        CUR_WORKSPACE_PATH = ""
        shutil.rmtree(path)
        print("Directory removed successfully")
        return jsonify("Workspace removed sucessfully!")
    except OSError as o:
        # ths happens when user click the refresh button without saving the workspace
        print(f"Error: {o.strerror}: saved before")
        return jsonify("No Workspace saved")


# Endpoint for upload the test files
@app.route("/upload_file", methods=["POST"])
def upload_file():
    global DEFINITION_FILE_PATH
    global DUTS_FILE_PATH
    global CUR_WORKSPACE_PATH
    """Handles the upload of a file."""

    file = request.files["file"]
    file_name = secure_filename(file.filename)
    # test
    print(f"Uploading file {file_name}")
    # read file
    file_bytes = file.read()
    file_content = BytesIO(file_bytes).read().decode("utf-8")

    # Case: in update workspace page, CUR_WORKSPACE_PATH(an empty string) will be updated after creating the temporary workspace folder
    if CUR_WORKSPACE_PATH == "":
        temp_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            app.config["UPLOAD_FOLDER"],
            "temp_workspace",
        )
        worksapce_path = temp_path
        # create the temporary workspace foleder if it's not exist
        if os.path.exists(worksapce_path) == False:
            os.mkdir(worksapce_path)
    # Case: in vane page after user creates the workspace successfully
    else:
        worksapce_path = CUR_WORKSPACE_PATH
    # create file path in the Vane backend
    file_path = worksapce_path + "/" + file_name
    if file_name == "definitions.yaml":
        DEFINITION_FILE_PATH = file_path
    else:
        DUTS_FILE_PATH = file_path

    # store the file in the workspace
    f = open(file_path, "w")
    f.write(file_content)
    f.close()
    print("File upload successfully: ", file_path)

    return jsonify({"name": file_name, "status": "success"})


# Endpoint for delete the uploaded test files based on the CUR_WORKSPACE_PATH
@app.route("/delete_file", methods=["DELETE"])
def delete_file():
    global CUR_WORKSPACE_PATH
    global DEFINITION_FILE_PATH
    global DUTS_FILE_PATH

    name = request.data.decode("utf-8")
    print("Delete file: ", name)
    if name == "definitions.yaml":
        DEFINITION_FILE_PATH = ""
    else:
        DUTS_FILE_PATH = ""
    if CUR_WORKSPACE_PATH == "":
        workspace_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            app.config["UPLOAD_FOLDER"],
            "temp_workspace",
        )
        file_path = workspace_path + "/" + name
    else:
        file_path = CUR_WORKSPACE_PATH + "/" + name
    print("Deleted File Path: ", file_path)
    # delete the file
    os.remove(file_path)
    return jsonify("Delete " + name + " successfully")


# Endpoint for running vane
@app.route("/vane", methods=["GET", "POST"])
def vane():
    global CUR_WORKSPACE_PATH
    workspace_path = CUR_WORKSPACE_PATH

    # run vane using the test files
    print("Running Vane in:", workspace_path)

    config.DEFINITIONS_FILE = workspace_path + "/definitions.yaml"
    config.DUTS_FILE = workspace_path + "/duts.yaml"
    print("FINISH SET UP CONFIG")

    try:
        # Capture the vane output in terminal
        with open("help_page.txt", "w+") as f:
            print("Open file")
            with contextlib.redirect_stdout(f):
                vane_cli.run_tests(config.DEFINITIONS_FILE, config.DUTS_FILE)
                vane_cli.write_results(config.DEFINITIONS_FILE)
                vane_cli.download_test_results()

        #  the directory of the script being run
        root_dir = os.path.dirname(os.path.abspath(__file__))

        old_html_path = root_dir + "/reports/report.html"
        old_json_path = root_dir + "/reports/report.json"

        shutil.copy2(old_html_path, workspace_path + "/report.html")
        shutil.copy2(old_json_path, workspace_path + "/report.json")

        # update report.html in templates
        temp_html_path = root_dir + "/templates/report.html"
        os.remove(temp_html_path)
        shutil.copy2(old_html_path, temp_html_path)

        # find the latest report.doc
        doc_dir = root_dir + "/reports/*.docx"
        list_of_files = glob.glob(doc_dir)
        latest_file = max(list_of_files, key=os.path.getctime)
        print("Latest Report File: ", latest_file)
        old_doc_path = latest_file
        shutil.copy2(old_doc_path, workspace_path + "/report.docx")

        # find the latest report.zip
        zip_dir = root_dir + "/reports/TEST RESULTS ARCHIVES/*"
        list_of_zips = glob.glob(zip_dir)  # * means all if need specific format then *.csv
        latest_zip = max(list_of_zips, key=os.path.getctime)
        print("Latest Zip File: ", latest_zip)
        old_zip_path = latest_zip
        shutil.copy2(old_zip_path, workspace_path + "/report.zip")

        print("Run vane successfully")
        print("After Run vane, CUR_WORKSPACE_PATH: ", CUR_WORKSPACE_PATH)
        with open("help_page.txt", "r") as f:
            content = f.read()
        return content

    except:
        print("Run vane failed")
        return abort(500, "Run vane failed")


# Endpoint for show the pytest output (can be used in the future)
@app.route("/show_pytest", methods=["GET"])
def show_pytest():
    with open("help_page.txt", "r") as f:
        content = f.read()
    return content


# Endpoint for download reports
@app.route("/download/<filename>", methods=["GET", "POST"])
def download(filename):
    global CUR_WORKSPACE_PATH

    name = request.data.decode("utf-8")
    print("Workspace Name in Tab download section: ", name)
    try:
        # check the file
        print("Download File: ", filename)
        root_dir = os.path.dirname(os.path.abspath(__file__))
        if filename.split(".")[1] == "log":
            return send_from_directory(directory=root_dir, path=filename, mimetype=None)
        else:
            # from Tab 'POST' request
            if len(name) > 0:
                saved_worksapce_path = root_dir + "/workspace/" + name
                # print(saved_worksapce_path)
                return send_from_directory(
                    directory=saved_worksapce_path, path=filename, mimetype=None
                )
            # from Button 'GET' request
            else:
                return send_from_directory(
                    directory=CUR_WORKSPACE_PATH, path=filename, mimetype=None
                )
    except FileNotFoundError:
        abort(404)


# -----------------------------------Endpoints related to UPDATE Workspace Page------------------------------------
# A temporary workspace folder would be created automatically while user go to the update workspace page.
# and this temp_workspace folder will include the previous uploaded test files (definitions.yaml and duts.yaml)
# Before clicking the Update button, any update like delete previous test file, upload new file, build reports after runing vane,
# will be happend and stored in the temp_workspace folder.
# The global variable CUR_WORKSPACE_PATH would change to the path of temp_workspace, and then change back after finishing update the workspace.


# Endpoint for show the content of test files in Tabs
@app.route("/get_file/<filename>", methods=["POST"])
def get_file(filename):
    worksapce_name = request.data.decode("utf-8")
    print("Get file from workspace: ", worksapce_name)
    root_dir = os.path.dirname(os.path.abspath(__file__))
    worksapce_path = root_dir + "/workspace/" + worksapce_name
    file_path = worksapce_path + "/" + filename
    print(file_path)
    with open(file_path, "r") as f:
        content = f.read()
    return content


# 1. when go to the update workspace page:
# The global variable will be set: CUR_WORKSPACE_PATH = '/workspace/temp_workspace'
# 2. CUR_WORKSPACE_PATH will be cleared after clicking do back button
# (call '/delete_temporary_work_space') API


# Create a temporary workspace for update
@app.route("/add_temporary_work_space", methods=["POST"])
def add_temporary_work_space():
    global CUR_WORKSPACE_PATH
    temp_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), app.config["UPLOAD_FOLDER"], "temp_workspace"
    )
    # create the temporary workspace foleder if it's not exist
    if os.path.exists(temp_path) == False:
        os.mkdir(temp_path)

    # update the current workspace
    CUR_WORKSPACE_PATH = temp_path

    return jsonify("create a temporary workspace folder in backend")


# Endpoint for delete the temporary workspace, it used when user clicks the 'go back' button in the update workspace page.
@app.route("/delete_temporary_work_space", methods=["DELETE"])
def delete_temporary_work_space():
    global CUR_WORKSPACE_PATH
    temp_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), app.config["UPLOAD_FOLDER"], "temp_workspace"
    )

    # delete the temporary workspace foleder if it's exist
    try:
        shutil.rmtree(temp_path)
        # clear the current workspace path
        CUR_WORKSPACE_PATH = ""
        return jsonify("Delete a temporary workspace folder in backend")
    except OSError as o:
        print(f"Error, {o.strerror}: {temp_path}")
        return jsonify(f"Error, {o.strerror}: {temp_path}")


# Endpoint for get the list of yaml files from the workspace(which will be updated)
# this list will shown as a series of card below the upload-file box
# and add these files to the temporary workspace folder
@app.route("/get_test_files_list", methods=["POST"])
def get_test_files_list():
    global CUR_WORKSPACE_PATH
    worksapce_name = request.data.decode("utf-8")
    # handle the vane page at the beginnning, no workspace created and saved before
    if worksapce_name == "None":
        return []
    # handle the workspace page
    else:
        print("Get file from workspace: ", worksapce_name)
        root_dir = os.path.dirname(os.path.abspath(__file__))
        workspace_path = root_dir + "/workspace/" + worksapce_name
        print(workspace_path)
        dir_list = os.listdir(workspace_path)

        test_files_list = []
        for x in dir_list:
            if x.endswith(".yaml"):
                # get only yaml file in the current workspace
                test_files_list.append(x)
                print(x)
                # copy this 2 test files in a temporary folder
                shutil.copy2(workspace_path + "/" + x, CUR_WORKSPACE_PATH + "/" + x)

        return test_files_list


# Endpoint for save the workspace in update page
@app.route("/save_update", methods=["PUT"])
def save_update():
    global CUR_WORKSPACE_PATH
    print("save_update: ", CUR_WORKSPACE_PATH)

    # get the target workspace name
    worksapce_name = request.data.decode("utf-8")
    print(worksapce_name)
    root_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_path = root_dir + "/workspace/" + worksapce_name
    print(workspace_path)

    # delete the original target workspace
    shutil.rmtree(workspace_path)
    time.sleep(1)

    # replace the target workspace with the temporary workspace
    os.rename("workspace/temp_workspace", "workspace/" + worksapce_name)

    # Create the temperoray workspace for the next update
    temp_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), app.config["UPLOAD_FOLDER"], "temp_workspace"
    )
    # create the temporary workspace foleder if it's not exist
    if os.path.exists(temp_path) == False:
        os.mkdir(temp_path)

    # Add the test files in the temporary workspace
    print("Get file from workspace: ", worksapce_name)
    root_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_path = root_dir + "/workspace/" + worksapce_name
    print(workspace_path)
    dir_list = os.listdir(workspace_path)

    test_files_list = []
    for x in dir_list:
        if x.endswith(".yaml"):
            # get only yaml file in the current workspace
            test_files_list.append(x)
            print(x)
            # copy this 2 test files in a temporary folder
            shutil.copy2(workspace_path + "/" + x, CUR_WORKSPACE_PATH + "/" + x)

    return jsonify("Update Workspace sucessfully!")


# This function is used to create the folders and files before run the flaks app.
# The folders and files include the workspace folder, workspace.json, templates folder within a report.html inside.
def initialization():
    # create a workspace folder automatically if it not exist
    root_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.join(root_dir, "workspace")
    if os.path.exists(workspace_dir) == False:
        os.mkdir(workspace_dir)

    # create a workspace.json file if it is not exist
    root_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists(root_dir + "/workspace.json") == False:
        worksapce_list = {"name": []}
        json_object = json.dumps(worksapce_list, indent=4)
        with open("workspace.json", "w") as outfile:
            outfile.write(json_object)

    # create a templates folder automatically
    templates_dir = os.path.join(root_dir, "templates")
    if os.path.exists(templates_dir) == False:
        os.mkdir(templates_dir)

    # create a report.html(temporary placeholder) inside the templates folder
    report_html_path = os.path.join(root_dir, "templates", "report.html")
    # print(report_path)
    if os.path.exists(report_html_path) == False:
        html_template = ""
        with open(report_html_path, "w") as outfile:
            outfile.write(html_template)
    print("END OF INITIALIZATION")


# check the workspace folder, templates folder(within report.html), workspace.json
initialization()
