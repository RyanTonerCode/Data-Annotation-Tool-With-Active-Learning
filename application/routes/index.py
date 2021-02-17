from application import app
from application.imports import apology, session, render_template, os, request, json, redirect, secure_filename, time, send_file, after_this_request, send_from_directory, url_for, SharedDataMiddleware
import pandas as pd
import cv2
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.model_selection import train_test_split
from application.routes.train_ai import train_ai


@app.route("/", methods=["GET", "POST"]) #standard path url
@app.route("/<alert>", methods=["GET", "POST"]) #for redirect with alert
@app.route("/index.html", methods=["GET", "POST"]) #second standard path url
def home(alert = None):
    if request.method == "POST":
        key = ""
        input = ""
        if not request.files: #get JSON object key and value if not an upload, otherwise skip to bottom in upload section
            # print(request.get_json())
            key = next(iter(request.get_json().keys()))
            input = request.get_json()[key]



        def create_tag_html(tag_data): #from tag_data in user_data, create the HTML tag bar below the main textarea
            tags_html = ""
            for tag_index in tag_data["tags"]:
                tag_name = tag_data["tags"][tag_index]["name"]
                tag_color = tag_data["tags"][tag_index]["color"]

                radio_button = '''<label class="radio-container"><input type="radio" checked="checked" name="radio" value="''' + str(tag_index) + '''"><span class="checkmark ''' + tag_color + ''' "></span></label>'''
                tags_html += "<div class='tag-container'>" + radio_button + "<div class='tag'><div class='tag-name'>" + tag_name + "</div><div class='delete' data-index='" + str(tag_index) + "'>X</div></div></div>"
            
            if tags_html == "": 
                tags_html = '''<div class="tag no-tags"><div class="tag-name">No Tags</div></div>'''
            
            return tags_html
        


        if key=="new_tag": #create a new tag with a name and color, and a unique ID -- then return a new HTML tag bar
            tag_name = input[0]
            tag_color = input[1] 
            tag_data = {"index": 0, "tags": {}} #create index counter and empty dict for tags
            user_data = {"sentences": [], "sentence_tags": [], "tag_data": tag_data}
        
            file_path = "application/data/data.json"
            if os.path.isfile(file_path):
                with open(file_path) as json_file:
                    user_data = json.load(json_file) #retrieve user_data if availible

            tag_data = user_data["tag_data"]
            new_tag = {"name": tag_name, "color": tag_color}
            if new_tag not in tag_data["tags"].values() and tag_color != "" and tag_name != "": #if tag is valid and unique
                tag_index = tag_data["index"] + 1 #create next tag index, beginning at 1
                tag_data["index"] += 1 #increment index counter
                tag_data["tags"][tag_index] = new_tag #add new tag by index

            user_data["tag_data"] = tag_data
            with open(file_path, 'w') as outfile:
                json.dump(user_data, outfile) #save file changes

            return create_tag_html(tag_data)



        if key=="delete_tag": #delete a tag from the tag bar and from all words with that tag
            tag_index = input
            user_data = None
            file_path = "application/data/data.json"
            with open(file_path) as json_file:
                user_data = json.load(json_file) #retrieve user_data

            sentence_tags = user_data["sentence_tags"]
            user_data["tag_data"]["tags"].pop(str(tag_index)) #remove key-value pair from dict
            
            for sentence_index, sentence in enumerate(sentence_tags): #remove all tags from words with that tag's index ID 
                for word_index, word in enumerate(sentence):
                    if word == int(tag_index):
                        sentence_tags[sentence_index][word_index] = 0 #indicates no tag

            user_data["sentence_tags"] = sentence_tags

            with open(file_path, 'w') as json_file:
                json.dump(user_data, json_file) #save file changes

            return create_tag_html(user_data["tag_data"])



        def create_sentence_html(user_data, selected_sentece = 0, selected_word = 0): #create HTML for sentences area from user data, and set the selected sentence
            sentences_html = ""
            sentences = user_data["sentences"]
            sentence_tags = user_data["sentence_tags"]
            tag_data = user_data["tag_data"]

            if sentences != {} and sentence_tags != {}: #if there is any information to display
                for sentence_index, sentence in enumerate(sentences):
                    sentences_html += "<div class='sentence-area' data-index='" + str(sentence_index) + "'>"
                    for word_index, word in enumerate(sentence.split()):
                        word_tag_index = sentence_tags[sentence_index][word_index] #see what the word's tag is
                        tag_html = "<button class='btn2 select-tag-button'>tag</button>"
                        
                        if word_tag_index != 0: #if the word is tagged, add it here
                            word_tag_name = tag_data["tags"][str(word_tag_index)]["name"]
                            word_tag_color = tag_data["tags"][str(word_tag_index)]["color"]
                            tag_html = "<div class='sentence-tag tag'><div class='tag-color " + word_tag_color + "'></div><div class='tag-name'>" + word_tag_name + "</div><div class='delete'>X</div></div>"
                        
                        #if the word we're on should be selected per fn params, add selected class (otherwise keep it at word class)
                        word_class = "word selected" if sentence_index == selected_sentece and word_index == selected_word else "word"

                        sentences_html += "<div class='" + word_class + "' data-index='" + str(word_index) + "'> <div class='word-text'>" + word + "</div> " + tag_html + " </div> "

                    sentences_html += "</div>"

            return sentences_html



        def create_sentences(text): #from raw text, create a JSON file with dict data for application, return that data
            sentences = []
            sentence_tags = []
            tag_data = {"index": 0, "tags": {}} #create index counter and empty dict for tags
            user_data = {"sentences": [], "sentence_tags": [], "tag_data": tag_data}

            file_path = "application/data/data.json"
            if os.path.isfile(file_path): 
                time.sleep(0.01) #because JavaScript client requests initialization of both tags and sentences at the same time, conflicts can arise...
                with open(file_path) as json_file:
                    user_data = json.load(json_file) #retrieve existing user data, only if availible

            if text != "": #dont do nothin if they put nothin in
                delimiters = ".!?"
                sentence = "" #current sentence, gets reset at delimeter char
                leading_space = False #don't add spaces to the start of sentences
                for char in text:
                    if not leading_space: #skip spaces at the start of sentences (ie between sentences)
                        sentence += char
                    leading_space = False
                    if char in delimiters:
                    # if char == "." or char =="?" or char == "!":
                        sentences.append(sentence)
                        sentence = "" #reset current sentence
                        leading_space = True #next time, skip over the space between sentences

                for sentence in sentences: #create empty tag IDs for every word in every sentence
                    tags = [0 for x in sentence.split()]
                    # for word in sentence.split():
                    #     tags.append(0)
                    sentence_tags.append(tags)
   
                user_data["sentences"] += sentences #if there's existing data, append the new sentences and don't tamper with the existing tags
                user_data["sentence_tags"] += sentence_tags

            return user_data



        def ai(user_data, corrections=False):

                #load model here
                new_user_data = user_data
                #format new user data for AI
                #make predictions for tags using model, make threshold
                #apply predictions to new user data

                #decide how to implement corrections -- are we re-training the model here? ealier? later? never? who knows! where the wind blows...
                #use train_ai function?
                return new_user_data



        if "run" in key: #if text is submitted, add it to the data, and regardless, return HTML for sentences area
            text = input
            user_data = create_sentences(text) #if text empty, get user_data, if not empty, get user_data with new text implemented
            if key=="run_corrections" or key=="run_automatic":
                pass #modify user data here with AI

            file_path = "application/data/data.json"
            with open(file_path, 'w') as outfile:
                json.dump(user_data, outfile) #save user_data

            return create_sentence_html(user_data) #for corrections: add param, change fn so that AI learns of any changes made to tags



        if key=="tag_word": #tag a word or remove its tag and return updated sentence HTML
            indices = input
            sentence_index = int(indices[0])
            word_index = int(indices[1])
            tag_index = int(indices[2])
            user_data = None

            file_path = "application/data/data.json"
            with open(file_path) as json_file:
                user_data = json.load(json_file) #retrieve user_data
                    
            user_data["sentence_tags"][sentence_index][word_index] = tag_index #set tag by index
                        
            with open(file_path, 'w') as outfile:
                json.dump(user_data, outfile) #save user_data

            return create_sentence_html(user_data, sentence_index, word_index)



        if key=="clear_all": #delete all data. new empty file will be created after requests from client
            file_path = "application/data/data.json"
            if os.path.isfile(file_path):
                os.remove(file_path)

            # return redirect(url_for("home"))



        if key=="clear_tags": #remove tags from tag bar and all words/data
            file_path = "application/data/data.json"
            if os.path.isfile(file_path):
                user_data = None
                with open(file_path) as json_file:
                    user_data = json.load(json_file) #retrieve user data

                user_data["tag_data"] = {"index": 0, "tags": {}} #create index counter and empty dict for tags

                for sentence_index, sentence in enumerate(user_data["sentence_tags"]): #remove tags from all words in data
                    for word_index, word in enumerate(sentence):
                        user_data["sentence_tags"][sentence_index][word_index] = 0

                with open(file_path, 'w') as json_file:
                    json.dump(user_data, json_file) #save user_data

                # return redirect(url_for("home"))



        if key=="clear_sentences": #remove only sentence data
            file_path = "application/data/data.json"
            if os.path.isfile(file_path):
                user_data = None
                with open(file_path) as json_file:
                    user_data = json.load(json_file) #retrieve user_data

                user_data["sentences"] = [] #make empty data
                user_data["sentence_tags"] = []

                with open(file_path, 'w') as json_file:
                    json.dump(user_data, json_file) #save user_data

                # return create_sentence_html(user_data)



        if key=="download_all": #download data.json file (user_data) in its entirety
            file = None
            file_path = "application/data/data.json"
            with open(file_path) as json_file:
                file = json.load(json_file)

            return {"file": file, "name": input, "extension": "json"}



        if key=="download_tags": #download tags as a JSON, as if the sentence data were deleted, prserving the title
            user_data = None
            file_path = "application/data/data.json"
            with open(file_path) as json_file:
                user_data = json.load(json_file)

            file = {"tag_data": user_data["tag_data"]}
            return {"file": file, "name": input, "extension": "json"}

        

        if key=="download_sentences": #download all sentence data as TXT, essentially original format
            user_data = None
            file_path = "application/data/data.json"
            with open(file_path) as json_file:
                user_data = json.load(json_file)

            file = ""
            for sentence in user_data["sentences"]:
                file += sentence + " "

            return {"file": file, "name": input, "extension": "txt"}



        if key=="download_csv": #download a CSV of all data (both words and their tags), in format: word░{"name":"tag_name"+"color":"tag_color"},
            user_data = None
            file_path = "application/data/data.json"
            with open(file_path) as json_file:
                user_data = json.load(json_file)
            
            file = ""
            for sentence_index, sentence in enumerate(user_data["sentences"]):
                for word_index, word in enumerate(sentence.split()):
                    tag_index = str(user_data["sentence_tags"][sentence_index][word_index]) #get tag index ID number from current word
                    tag_info = user_data["tag_data"]["tags"][tag_index] if int(tag_index) > 0 else "no_tag" #retrieve tag data only if there's a tag
                    # print(tag_info)
                    tag_info = json.dumps(tag_info).replace(",", "+") #replace commas inside the tag data with this
                    # print(tag_info)
                    word_ = word.replace(",", "¬") #replace commas inside the word with this
                    new_item =  word_ + "░" + tag_info #separate word and tag data with special char                      
                    file += new_item + "," #add comma between values

            file = file[:-1] #remove trailing comma
            return {"file": file, "name": input, "extension": "csv"}



        if request.files: #if there are files to upload from request
            upload_folder = "application/data/upload"
            allowed_extensions = {'txt', 'json', 'csv'}
            file = request.files["file"]
            filename = secure_filename(file.filename) #convert filename to secure form for some reason
            if filename != "": #ensure file is real
                file_extension = filename.rsplit('.', 1)[1].lower()
                if '.' in filename and file_extension in allowed_extensions:
                    file.save(os.path.join(upload_folder, filename)) #save uploaded file on server

                    if file_extension == "json": #replace all data or replace all tag data
                        new_data = None
                        with open(upload_folder + "/" + filename) as json_file:
                            new_data = json.load(json_file)

                        keys = new_data.keys()
                        user_data = None
                        with open("application/data/data.json") as json_file:
                            user_data = json.load(json_file)

                        if len(keys) == 3: #uploaded all data
                            user_data = new_data
                        elif len(keys) == 1: #uploaded only tag data
                            user_data["tag_data"] = new_data["tag_data"]

                        with open("application/data/data.json", 'w') as json_file:
                            json.dump(user_data, json_file) #save user_data

                    elif file_extension == "txt": #if uploaded txt file, treat similar to text entered in textarea and run_manual
                        text = ""
                        with open(upload_folder + "/" + filename) as txt_file:
                            text = txt_file.read()
                        user_data = create_sentences(text)
                        file_path = "application/data/data.json"
                        with open(file_path, 'w') as outfile:
                            json.dump(user_data, outfile)

                    elif file_extension == "csv": #not implemented
                        csv = ""
                        with open(upload_folder + "/" + filename) as csv_file:
                            csv = csv_file.read() #read in csv file

                        words = [x for x in csv.split(",")] #separate each value into word-tag pairs by the commas
                        sentences = []
                        sentence_tags = []
                        tag_data = {"index": 0, "tags": {}} #create index counter and empty dict for tags
                        user_data = {"sentences": [], "sentence_tags": [], "tag_data": tag_data}
                        delimiters = ".!?" #sentence-ending delimeters

                        sentence = "" #current sentence
                        word_tags = [] #current sentence's tags
                        for pair in words: #for each word-tag pair
                            pair_ = pair.split("░") #split by the special delimeter
                            word = pair_[0]
                            tag = pair_[1]

                            word = word.replace("¬",",") #replace special char with comma from conversion
                            tag = tag.replace("+",",")
                            sentence += word #add the word to the sentence

                            if tag != '"no_tag"': #bc it was jsonified on conversion, the quotes are included in the string
                                tag = json.loads(tag) #convert string to json object
                                if tag not in tag_data["tags"].values():
                                    tag_data["index"] += 1 #increment tag index with each new one we see
                                    tag_data["tags"][tag_data["index"]] = tag #and create the data entry

                                word_tags.append(int(list(tag_data["tags"].keys())[int(list(tag_data["tags"].values()).index(tag))])) #get tag ID from tag value we have
                            else:
                                word_tags.append(0) #value is 0 for no tag

                            if word[-1] in delimiters: #if end of sentence, add and clear for next sentence
                                sentences.append(sentence) 
                                sentence_tags.append(word_tags)
                                sentence = ""
                                word_tags = []
                            else:
                                sentence += " " #add spaces between words but not between sentences

                        user_data["sentences"] = sentences
                        user_data["sentence_tags"] = sentence_tags
                        user_data["tag_data"] = tag_data

                        file_path = "application/data/data.json"
                        with open("application/data/data.json", 'w') as json_file:
                            json.dump(user_data, json_file) #save user_data

                    filelist = [f for f in os.listdir("application/data/upload")] #remove upload files after use
                    for f in filelist:
                        os.remove(os.path.join("application/data/upload", f))

                    return redirect(url_for("home", alert="file upload successful"))

            return render_template("index.html", alert="error uploading files")

    return render_template("index.html", alert=alert) #if request method is GET or POST function does not return
   






######## DEPRECATED ########

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
# one dictionary: "sentences", "sentence_tags", "tag_data"
# user_data["sentences"] = a list of strings, each string is one sentence fully intact
# user_data["sentence_tags"] = a list of lists of integers, each child list represents a sentence, each number represents a word's tag index number
# the sentences and sentence_tags data can be correlated by list[i]
# user_data["tag_data"] = a dictionary: "index", "tags"
# user_data["tag_data"]["index"] = running index (integer) of how many tags have ever been created, so each new tag has a unique index ID number
# user_data["tag_data"]["tags"] = a dictionary: keys = tag ID numbers (strings), values = dictionary: "name", "color"
# user_data["tag_data"]["tags"][tag ID number]["name"] = name of tag (string)
# user_data["tag_data"]["tags"][tag ID number]["color"] = color of tag (string)

# export all --> JSON of original data.json file on server
# export tags --> JSON of tag_data in dict with key "tag_data"
# export sentences --> TXT of raw sentences
# export CSV --> combines user_data
#   format: word░{"name":"name"+"color":"color"},