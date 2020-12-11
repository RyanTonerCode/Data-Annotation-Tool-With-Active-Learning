from application import app
from application.imports import apology, session, render_template, os, request, json, re
from werkzeug.middleware.shared_data import SharedDataMiddleware
from flask import send_file, after_this_request, send_from_directory
from werkzeug.utils import secure_filename
import io
import pandas as pd
import nltk

@app.route("/", methods=["GET", "POST"])
@app.route("/home", methods=["GET", "POST"])
@app.route("/index.html", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # print(request.get_json())
        key = next(iter(request.get_json().keys()))
        data = request.get_json()[key]

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
            tag_name = data[0]
            tag_color = data[1] 
            tag_data = {"index": 0, "tags": {}} #create index counter and empty dict for tags
        
            jsonFile = "application/data/tag_data.json"
            if os.path.isfile(jsonFile):
                with open(jsonFile) as json_data:
                    tag_data = json.load(json_data)

            new_tag = {"name": tag_name, "color": tag_color}
            if new_tag not in tag_data["tags"].values() and tag_color != "" and tag_name != "":
                tag_index = tag_data["index"] + 1 #create next tag index
                tag_data["index"] += 1 #increment index counter
                tag_data["tags"][tag_index] = new_tag #add new tag by index

            with open(jsonFile, 'w') as outfile:
                json.dump(tag_data, outfile)

            return create_tag_html(tag_data)



        if key=="delete_tag":
            tag_index = data
            jsonFile = "application/data/tag_data.json"
            if os.path.isfile(jsonFile):
                with open(jsonFile) as json_data:
                    tag_data = json.load(json_data)
                    tag_data["tags"].pop(str(tag_index)) #remove key-value pair from dict
                    
                with open(jsonFile, 'w') as outfile:
                    json.dump(tag_data, outfile)

            jsonFile = "application/data/sentence_data.json"
            if os.path.isfile(jsonFile):
                with open(jsonFile) as json_data:
                    sentence_data = json.load(json_data)
                    
                    for sentence_index, sentence in enumerate(sentence_data["sentence_tags"]):
                        for word_index, word in enumerate(sentence):
                            if word == int(tag_index):
                                sentence_data["sentence_tags"][sentence_index][word_index] = 0

                with open(jsonFile, 'w') as outfile:
                    json.dump(sentence_data, outfile)



        def create_sentence_html(sentence_data, selected_sentece = 0, selected_word = 0):
            sentences_html = ""
            if sentence_data != {}:

                tag_data = {}
                jsonFile = "application/data/tag_data.json"
                if os.path.isfile(jsonFile):
                    with open(jsonFile) as json_data:
                        tag_data = json.load(json_data)

                for sentence_index, sentence in enumerate(sentence_data["sentences"]):
                    sentences_html += "<div class='sentence-area' data-index='" + str(sentence_index) + "'>"
                    for word_index, word in enumerate(sentence.split()):
                        word_tag_index = sentence_data["sentence_tags"][sentence_index][word_index]
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
            sentence_data = {"sentences": [], "sentence_tags": []}

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

            jsonFile = "application/data/sentence_data.json"
            if os.path.isfile(jsonFile):
                with open(jsonFile) as json_data:
                    sentence_data = json.load(json_data)
                    
            if text != "": #dont do nothin if they put nothin in
                sentence_data["sentences"] += sentences
                sentence_data["sentence_tags"] += sentence_tags

            return sentence_data


        if key=="run_manual":
            text = data
            sentence_data = create_sentences(text)
            jsonFile = "application/data/sentence_data.json"
            with open(jsonFile, 'w') as outfile:
                json.dump(sentence_data, outfile)

            return create_sentence_html(sentence_data)

        if key=="run_corrections":
            text = data
            sentence_data = create_sentences(text)
            #modify sentence_data here with AI
            jsonFile = "application/data/sentence_data.json"
            with open(jsonFile, 'w') as outfile:
                json.dump(sentence_data, outfile)
            return create_sentence_html(sentence_data) #add param, change fn so that AI learns of any changes made to tags

        if key=="run_automatic":
            text = data
            sentence_data = create_sentences(text)
            #modify sentence_data here with AI
            jsonFile = "application/data/sentence_data.json"
            with open(jsonFile, 'w') as outfile:
                json.dump(sentence_data, outfile)
            return create_sentence_html(sentence_data)



        if key=="tag_word":
            indices = data
            sentence_index = int(indices[0])
            word_index = int(indices[1])
            tag_index = int(indices[2])

            sentence_data = {}

            jsonFile = "application/data/sentence_data.json"
            if os.path.isfile(jsonFile):
                with open(jsonFile) as json_data:
                    sentence_data = json.load(json_data)
                    
            if tag_index >= 0: #if adding tag to word     
                tag_data = {}

                jsonFile2 = "application/data/tag_data.json"
                if os.path.isfile(jsonFile2):
                    with open(jsonFile2) as json_data2:
                        tag_data = json.load(json_data2)

                sentence_data["sentence_tags"][sentence_index][word_index] = tag_index #set tag by index
            
            elif tag_index == -1: #if removing tag from word
                sentence_data["sentence_tags"][sentence_index][word_index] = 0
            
            with open(jsonFile, 'w') as outfile:
                json.dump(sentence_data, outfile)

            return create_sentence_html(sentence_data, sentence_index, word_index)




        if key=="clear_tags":
            jsonFile = "application/data/tag_data.json"
            if os.path.isfile(jsonFile):
                os.remove(jsonFile)


        if key=="clear_sentences":
            jsonFile = "application/data/sentence_data.json"
            if os.path.isfile(jsonFile):
                os.remove(jsonFile)

        if key=="download_tags":
            return send_file("data/tag_data.json", as_attachment=True)
        
        if key=="download_sentences":
            return send_file("data/sentence_data.json", as_attachment=True)



    return render_template("index.html")
   







   
UPLOAD_FOLDER = "application/data"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
@app.route('/success', methods = ['GET','POST'])
def uploaded_file():
    if request.method == 'POST':  
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

            jsonFile = "application/data/sentence_data.json"
            if os.path.isfile(jsonFile):
                with open(jsonFile) as json_data:
                    sentence_data = json.load(json_data)

            sentence_data = {"sentences": sentences, "sentence_tags": sentence_tags}
            out_file = open("application/data/sentence_data.json", "w")
            json.dump(sentence_data, out_file, indent=6)
            out_file.close()  
            # os.remove(os.path.join(app.config['UPLOAD_FOLDER'], subpath))
       
            # return render_template("index.html", name = f.filename) 
            return render_template("index.html") 
        

@app.route('/downloads/tags',methods = ['GET','POST'])  
def download_file_labels():
    return send_file("data/tag_data.json", as_attachment=True)
    
@app.route('/downloads/labels',methods = ['GET','POST'])  
def download_file_annotation():
    return send_file("data/sentence_data.json", as_attachment=True)
