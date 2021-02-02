from flask.helpers import url_for
from application import app
from application.imports import apology, session, render_template, os, request, json, re
from werkzeug.middleware.shared_data import SharedDataMiddleware
from flask import send_file, after_this_request, send_from_directory
from werkzeug.utils import redirect, secure_filename
import io
import pandas as pd
import nltk

@app.route("/", methods=["GET", "POST"])
@app.route("/<alert>", methods=["GET", "POST"])
@app.route("/home", methods=["GET", "POST"])
@app.route("/index.html", methods=["GET", "POST"])
def home(alert=None):
    if request.method == "POST":
        key = ""
        input = ""
        if not request.files:
            # print(request.get_json())
            key = next(iter(request.get_json().keys()))
            input = request.get_json()[key]

        def create_tag_html(tag_data):
            tags_html = ""
            for tag_index in tag_data["tags"]:
                tag_name = tag_data["tags"][tag_index]["name"]
                tag_color = tag_data["tags"][tag_index]["color"]

                radio_button = '''<label class="radio-container"><input type="radio" checked="checked" name="radio" value="''' + str(tag_index) + '''"><span class="checkmark ''' + tag_color + ''' "></span></label>'''
                tags_html += "<div class='tag-container'>" + radio_button + "<div class='tag'><div class='tag-name'>" + tag_name + "</div><div class='delete' data-index='" + str(tag_index) + "'>X</div></div></div>"
            
            if tags_html == "": tags_html = '''<div class="tag no-tags"><div class="tag-name">No Tags</div></div>'''
            return tags_html
        


        if key=="new_tag":
            tag_name = input[0]
            tag_color = input[1] 
            tag_data = {"index": 0, "tags": {}} #create index counter and empty dict for tags
            user_data = {"sentences": [], "sentence_tags": [], "tag_data": []}
        
            file_path = "application/data/data.json"
            if os.path.isfile(file_path):
                with open(file_path) as json_file:
                    user_data = json.load(json_file)
                    tag_data = user_data["tag_data"]

            new_tag = {"name": tag_name, "color": tag_color}
            if new_tag not in tag_data["tags"].values() and tag_color != "" and tag_name != "":
                tag_index = tag_data["index"] + 1 #create next tag index
                tag_data["index"] += 1 #increment index counter
                tag_data["tags"][tag_index] = new_tag #add new tag by index

            with open(file_path, 'w') as outfile:
                user_data["tag_data"] = tag_data
                json.dump(user_data, outfile)

            return create_tag_html(tag_data)



        if key=="delete_tag":
            tag_index = input
            file_path = "application/data/data.json"
            if os.path.isfile(file_path):
                user_data = None
                with open(file_path) as json_file:
                    user_data = json.load(json_file)

                tag_data = user_data["tag_data"]
                sentence_tags = user_data["sentence_tags"]
                tag_data["tags"].pop(str(tag_index)) #remove key-value pair from dict
                
                for sentence_index, sentence in enumerate(sentence_tags):
                    for word_index, word in enumerate(sentence):
                        if word == int(tag_index):
                            sentence_tags[sentence_index][word_index] = 0

                user_data["tag_data"] = tag_data
                user_data["sentence_tags"] = sentence_tags

                with open(file_path, 'w') as json_file:
                    json.dump(user_data, json_file)



        def create_sentence_html(user_data, selected_sentece = 0, selected_word = 0):
            sentences_html = ""
            sentences = user_data["sentences"]
            sentence_tags = user_data["sentence_tags"]
            tag_data = user_data["tag_data"]

            if sentences != {} and sentence_tags != {}:
                for sentence_index, sentence in enumerate(sentences):
                    sentences_html += "<div class='sentence-area' data-index='" + str(sentence_index) + "'>"
                    for word_index, word in enumerate(sentence.split()):
                        word_tag_index = sentence_tags[sentence_index][word_index]
                        tag_html = "<button class='btn2 select-tag-button'>tag</button>"
                        
                        if word_tag_index != 0:
                            word_tag_name = tag_data["tags"][str(word_tag_index)]["name"]
                            word_tag_color = tag_data["tags"][str(word_tag_index)]["color"]
                            tag_html = "<div class='sentence-tag tag'><div class='tag-color " + word_tag_color + "'></div><div class='tag-name'>" + word_tag_name + "</div><div class='delete'>X</div></div>"
                        
                        word_class = "word" #the standard word should have a class as just 'word'

                        if sentence_index == selected_sentece and word_index == selected_word: #always load the page with the first word of the first sentence selected, unless the vars are passed in
                            word_class += " selected"

                        sentences_html += "<div class='" + word_class + "' data-index='" + str(word_index) + "'> <div class='word-text'>" + word + "</div> " + tag_html + " </div> "

                    sentences_html += "</div>"

            return sentences_html

                
        def create_sentences(text):
            sentences = []
            sentence_tags = []
            user_data = {"sentences": [], "sentence_tags": [], "tag_data": []}

            if text != "": #dont do nothin if they put nothin in
                d = ".!?"
                sentence = ""
                leading_space = False
                for char in text:
                    if not leading_space:
                        sentence += char
                    leading_space = False
                    if char == "." or char =="?" or char == "!":
                        sentences.append(sentence)
                        sentence = ""
                        leading_space = True

                for sentence in sentences:
                    tags = []
                    for word in sentence.split():
                        tag = 0
                        tags.append(tag)
                    sentence_tags.append(tags)

            file_path = "application/data/data.json"
            if os.path.isfile(file_path):
                with open(file_path) as json_file:
                    # print(json_file)
                    user_data = json.load(json_file)
                    # print(user_data)
                    
            if text != "": #dont do nothin if they put nothin in
                user_data["sentences"] += sentences
                user_data["sentence_tags"] += sentence_tags

            return user_data


        if key=="run_manual":
            text = input
            user_data = create_sentences(text)
            file_path = "application/data/data.json"
            with open(file_path, 'w') as outfile:
                json.dump(user_data, outfile)

            return create_sentence_html(user_data)

        if key=="run_corrections":
            text = input
            user_data = create_sentences(text)
            #modify user_data here with AI
            file_path = "application/data/data.json"
            with open(file_path, 'w') as outfile:
                json.dump(user_data, outfile)

            return create_sentence_html(user_data) #add param, change fn so that AI learns of any changes made to tags

        if key=="run_automatic":
            text = input
            user_data = create_sentences(text)
            #modify user_data here with AI
            file_path = "application/data/data.json"
            with open(file_path, 'w') as outfile:
                json.dump(user_data, outfile)

            return create_sentence_html(user_data)



        if key=="tag_word":
            indices = input
            sentence_index = int(indices[0])
            word_index = int(indices[1])
            tag_index = int(indices[2])

            user_data = {}

            file_path = "application/data/data.json"
            if os.path.isfile(file_path):
                with open(file_path) as json_file:
                    user_data = json.load(json_file)

            sentence_tags = user_data["sentence_tags"]
                    
            if tag_index >= 0: #if adding tag to word     
                sentence_tags[sentence_index][word_index] = tag_index #set tag by index
            
            elif tag_index == -1: #if removing tag from word
                sentence_tags[sentence_index][word_index] = 0
            
            with open(file_path, 'w') as outfile:
                json.dump(user_data, outfile)

            return create_sentence_html(user_data, sentence_index, word_index)


        if key=="clear_all":
            file_path = "application/data/data.json"
            if os.path.isfile(file_path):
                os.remove(file_path)

            return redirect(url_for("home"))

        if key=="clear_tags":
            file_path = "application/data/data.json"
            if os.path.isfile(file_path):
                user_data = None
                with open(file_path) as json_file:
                    user_data = json.load(json_file)

                user_data["tag_data"] = {"index": 0, "tags": {}} #create index counter and empty dict for tags

                for sentence_index, sentence in enumerate(user_data["sentence_tags"]):
                    for word_index, word in enumerate(sentence):
                        user_data["sentence_tags"][sentence_index][word_index] = 0

                with open(file_path, 'w') as json_file:
                    json.dump(user_data, json_file)

                return redirect(url_for("home"))

        if key=="clear_sentences":
            file_path = "application/data/data.json"
            if os.path.isfile(file_path):
                user_data = None
                with open(file_path) as json_file:
                    user_data = json.load(json_file)

                user_data["sentences"] = []
                user_data["sentence_tags"] = []

                with open(file_path, 'w') as json_file:
                    json.dump(user_data, json_file)

                return create_sentence_html(user_data)

        if key=="download_all":
            # file = send_file("data/data.json", as_attachment=True)
            file = None
            file_path = "application/data/data.json"
            with open(file_path) as json_file:
                file = json.load(json_file)
            return {"file": file, "name": input, "extension": "json"}

        if key=="download_tags":
            file_path = "application/data/data.json"
            # new_file_path = "application/data/download/tag_data.json"
            tag_data = None
            with open(file_path) as json_file:
                user_data = json.load(json_file)
            tag_data = user_data["tag_data"]
            file = {"tag_data": tag_data}
            # return send_file("data/download/tag_data.json", as_attachment=True) #why does this need application removed???
            return {"file": file, "name": input, "extension": "json"}

        
        if key=="download_sentences":
            file_path = "application/data/data.json"
            # new_file_path = "application/data/download/sentences.txt"
            text = ""
            with open(file_path) as json_file:
                user_data = json.load(json_file)
                sentences = user_data["sentences"]
                for sentence in sentences:
                    text += sentence + " "

            return {"file": text, "name": input, "extension": "txt"}
            # return send_file("data/download/sentences.txt", as_attachment=True) #why does this need application removed???

    




        if request.files:
            #if there are files to upload from request
            upload_folder = "application/data/upload"
            allowed_extensions = {'txt', 'json', 'csv'}
            file = request.files["file"]
            filename = secure_filename(file.filename)
            if filename != "":
                file_extension = filename.rsplit('.', 1)[1].lower()
                if '.' in filename and file_extension in allowed_extensions:
                    file.save(os.path.join(upload_folder, filename))

                    if file_extension == "json":
                        new_data = None
                        with open(upload_folder + "/" + filename) as json_file:
                            new_data = json.load(json_file)

                        keys = new_data.keys()
                        user_data = None
                        with open("application/data/data.json") as json_file2:
                            user_data = json.load(json_file2)

                        if len(keys) == 3: #uploaded all
                            user_data = new_data
                        elif len(keys) == 1: #uploaded tags
                            user_data["tag_data"] = new_data["tag_data"]

                        with open("application/data/data.json", 'w') as json_file2:
                            json.dump(user_data, json_file2)

                    elif file_extension == "txt":
                        text = ""
                        with open(upload_folder + "/" + filename) as txt_file:
                            text = txt_file.read()
                        user_data = create_sentences(text)
                        file_path = "application/data/data.json"
                        with open(file_path, 'w') as outfile:
                            json.dump(user_data, outfile)

                        # return create_sentence_html(user_data)
                        # return render_template("index.html")

                    elif file_extension == "csv":
                        filelist = [f for f in os.listdir("application/data/upload")] #delete after implementation
                        for f in filelist:
                            os.remove(os.path.join("application/data/upload", f))

                        return render_template("index.html", alert="implement csv upload")

                    filelist = [f for f in os.listdir("application/data/upload")] #remove upload files
                    for f in filelist:
                        os.remove(os.path.join("application/data/upload", f))

                    # return render_template("index.html", alert="file upload successful")
                    return redirect(url_for("home", alert="file upload successful"))

            return render_template("index.html", alert="error uploading files")



    return render_template("index.html", alert=alert)
   





# @app.route("/upload", methods=["GET", "POST"])
# def upload_file():
#     if request.method == "POST":
#         pass






   
UPLOAD_FOLDER = "application/data"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
@app.route('/success', methods = ['GET','POST'])
def uploaded_file():
    if request.method == 'POST':  
        print(request.files)
        if request.files:
            f = request.files['file']  
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))
            path = [x for x in os.walk(app.config['UPLOAD_FOLDER'])]
            subpath = path[0][2][0]
            dataset = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'],subpath))
            data = dataset.iloc[:,0]

            if str(data) == "Series([], Name: Unnamed: 0, dtype: object)":
                print("INVALID FILE")
                # return render_template("index.html") 
                return apology("Invalid File Type", 10, "index")

            data = data[0]

            sentence_data = {"sentences": [], "sentence_tags": []}
            sentences = []
            sentence_tags = []
            d = ".!?"
            sentence = ""
            leading_space = False
            for char in data:
                if not leading_space:
                    sentence += char
                leading_space = False
                if char == "." or char =="?" or char == "!":
                    sentences.append(sentence)
                    sentence = ""
                    leading_space = True

            for sentence in sentences:
                tags = []
                for word in sentence.split():
                    tag = 0
                    tags.append(tag)
                sentence_tags.append(tags)

            file_path = "application/data/sentence_data.json"
            if os.path.isfile(file_path):
                with open(file_path) as json_file:
                    sentence_data = json.load(json_file)

            sentence_data = {"sentences": sentences, "sentence_tags": sentence_tags}
            out_file = open("application/data/sentence_data.json", "w")
            json.dump(sentence_data, out_file, indent=6)
            out_file.close()  
            # os.remove(os.path.join(app.config['UPLOAD_FOLDER'], subpath))
       
            # return render_template("index.html", name = f.filename) 
            return render_template("index.html") 
    





##### DATA STRUCTURE: #####
# JSON file --> user_data
# One dictionary: "sentences", "sentence_tags", "tag_data"
# user_data["sentences"] = a list of strings, each string is one sentence fully intact
# user_data["sentence_tags"] = a list of lists of integers, each child list represents a sentence, each number represents a word's tag index number
# the sentences and sentence_tags data can be correlated by list[i]
# user_data["tag_data"] = a dictionary: "index", "tags"
# user_data["tag_data"]["index"] = running index (integer) of how many tags have ever been created, so each new tag has a unique index ID number
# user_data["tag_data"]["tags"] = a dictionary: keys = tag ID numbers (strings), values = dictionary: "name", "color"
# user_data["tag_data"]["tags"][tag ID number]["name"] = name of tag (string)
# user_data["tag_data"]["tags"][tag ID number]["color"] = color of tag (string)