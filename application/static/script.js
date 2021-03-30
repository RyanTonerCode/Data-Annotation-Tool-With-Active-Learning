$(document).ready(function() 
{

    // var ai_model = false;
    function initialize() 
    {
        ajax("/", JSON.stringify({ "run_manual": "" }), initialize_return);
    }
    function initialize_return(data) 
    {
        update_tags(data["tag_data"]);
        update_sentences(data["sentence_data"]);
        $(".tags-area-overlay, .clear-model, .save-model-block, .run-update-model, .run-model").toggle(data["ai"]); //show/hide AI-related buttons, disabling tags too (based on whether there is a model path even if empty)
        // ai_model = data["ai"];
    }
    initialize();




    /* TAGS BAR */
    $(document).on("click", ".new-tag", function() //when we click new tag (+) button
    {
        $(".create-tag").toggle();
    });
    $(document).on("click", ".color-selector-button", function() //when we click SELECT COLOR... button
    {
        $(".color-selector-options").toggle();
    });
    $(document).on("click", ".color-selector-option", function(e) //when we click a color option button
    {
        $(".color-selector-options").toggle(); //hide the menu
        var color_html = e.target;
        if (color_html.className != "color-selector-option") //if we clicked on the content inside the button, get the data from the encapsulating button
        {
            color_html = color_html.parentElement;
        }
        color_html = color_html.firstElementChild.className.replace('tag-color ', ''); //get the color from inside the button
        // color_html = color_html.firstElementChild.dataset.color;
        $(".color-selector-button").css("background-color", color_html); //set background color of button to color we chose
        $(".color-selector-button").attr("color", color_html); //set color data attribute (not affect appearance) to color we chose for later reference... bg-color uses RGB not text
        $(".color-selector-button").html(color_html); //set text inside button to color we chose
    });
    $(document).on("click", ".submit-new-tag", function() //when we click DONE (for new tag) button
    {
        $(".create-tag").hide(); //hide tag creator
        var tag_name = $(".new-tag-input").val();
        var tag_color = $(".color-selector-button").attr("color");
        var tag_index = $(".submit-new-tag").data("index");
        var new_tag = [tag_name, tag_color, tag_index];
        $(".new-tag-input").val(""); //clear tag creator textbox
        $(".color-selector-button").first().css("background-color", "goldenrod").html("Select Color..."); //reset tag creator color selector
        $(".submit-new-tag").data("index", 0); //reset index so we dont replace other tags next time by accident
        ajax("/", JSON.stringify({ new_tag }), initialize_return);
    });
    $(document).on("click", ".tag-overlay", function(e) //when we click edit button on a tag
    {
        $(e.target).next().toggle();
    });
    $(document).on("click", ".tag-edit-menu-item", function(e) //when we click a menu item for a tag after clicking edit
    {
        $(e.target).parent().hide();
    });
    $(document).on("click", ".tag-edit-menu-item.modify", function(e) //when we click modify tag
    {
        var tag_name = $(e.target).parent().parent().children(".tag-name").html();
        var tag_color = $(e.target).parent().parent().parent().children("label").children("span").attr("class").split(" ")[1]; //get color from class name of tag icon color
        var tag_index = $(e.target).parent().parent().children(".tag-overlay").data("index");
        $(".new-tag-input").val(tag_name); //set up so textbox has current name
        $(".color-selector-button").css("background-color", tag_color).html(tag_color); //set up so color selector has current color and title is current color
        $(".submit-new-tag").data("index", tag_index); //set the tag index so it knows which to replace, and 0 means new tag
        $(".create-tag").show(); //show to tag creator that we just set up
    });
    $(document).on("click", ".tag-edit-menu-item.delete", function(e) //when we click delete tag
    {
        var tag_index = $(e.target).parent().parent().children(".tag-overlay").data("index");
        ajax("/", JSON.stringify({ "delete_tag": tag_index }), initialize_return);
    });

    function update_tags(data) 
    {
        if (data != "") 
        {
            $(".tags-area .tags").html(data);
        }
    }



    /* RUN BUTTONS & ADD TEXT */
    $(document).on("click", ".run", function() //when we click RUN AI... button
    {
        $(".run-options").toggle();
    });
    $(document).on("click", ".run-options button", function() //when we click a RUN AI... menu button
    {
        $(".run-options").hide();
    });
    $(document).on("click", ".add-text", function() //when we click ADD TEXT button
    {
        var text = $("#text-box-field").val();
        $("#text-box-field").val("");
        ajax("/", JSON.stringify({ "run_manual": text }), initialize_return);
    });
    $(document).on("click", ".create-model", function() //when we click CREATE-MODEL button
    {
        //Running the AI means that tags can no longer be modified, because the model will only be trained on those tags
        $(':focus').blur();
        $(".search-box").removeClass("top");
        var content = "Running the AI entails that tags cannot be modified again. Click continue if you are satisfied with your current set of tags. <br><br>";
        content += "But first, give your new model a filename: <br><br> <input type='text' name='model-name' placeholder='Filename' id='model-name' class='new-tag-input' autofocus> <br><br>";
        var button = "<button id='ai-continue-button' class='form-button'>CONTINUE</button>";
        showAlert(content, button);

        $(document).on("click", "#ai-continue-button", function(e) 
        {
            start_ai(0)
        });
    });
    $(document).on("click", ".run-update-model", function() //when we click RUN-MODEL button
    {
        start_ai(1)
    });
    $(document).on("click", ".run-model", function() //when we click RUN-MODEL button
    {
        start_ai(2)
    });
    function start_ai(create_model) 
    {
        var test_sentences = $(".sentences-area .checkbox-container input:checked").parent().parent().parent().map(function() { return $(this).data('index'); }).get();
        // var filename = $("#model-name").is(":visible") ? $("#model-name").val() : "model"
        var query = create_model == 0 ? { "run_create_model": $("#model-name").val() } : create_model == 1 ? { "run_update_model": "" } : { "run_model": test_sentences };

        $("#loading").show();
        ajax("/", JSON.stringify(query), update_sentences);
        $(".tags-area-overlay, .clear-model, .save-model-block, .run-update-model, .run-model").show(); //show AI-related buttons, disabling tags too
        $("#alert").css("display", "none");
        $("#alert-stuff").html("");
    }
    function update_sentences(data) 
    {
        $(".sentences-area").html(data);
        $("#loading").hide();
    }



    /* ADD OR REMOVE TAG FROM WORD */
    $(document).on("click", ".select-tag-button", function(e) //when we click TAG button below a word
    {
        var tag_index = $("input[name=radio]:checked").val();
        change_tag(e, tag_index);
    });
    $(document).on("click", ".sentences-area .delete", function(e) //when we click delete tag word
    {
        change_tag(e, 0);
    });
    function change_tag(e, tag_index)
    {
        var sentence_index = $(e.target).closest(".sentence-area").data("index");
        var word_index = $(e.target).closest(".word").data("index");
        if (selected_sentence != sentence_index)
        {
            entire_sentence_selected = false;
        }
        var tag_word = [sentence_index, word_index, entire_sentence_selected, tag_index];
        selected_sentence = sentence_index;
        selected_word = word_index;
        ajax("/", JSON.stringify({ tag_word }), update_sentences);
    }



    /* KEYDOWN - SENTENCE NAV, TAGGING */
    var selected_sentence = 0;
    var selected_word = 0;
    var entire_sentence_selected = false; 

    $(document).keydown(function(e) 
    {
        var number_of_sentences = document.getElementsByClassName("sentence-area").length;
        if ($("input").is(":focus") || $("textarea").is(":focus") || number_of_sentences == 0) { return; }
        //dont do stuff from keys if typing somewhere (text field) or if there arent any sentences yet
        var words_in_sentence = document.getElementsByClassName("sentence-area")[selected_sentence].children[1].children.length;
        document.getElementsByClassName("sentence-area")[selected_sentence].children[1].children[selected_word].classList.remove("selected")
        
        var shifty_mc_shift_face = e.shiftKey && e.code == "KeyA"
        var bow_and_arrow = ["ArrowRight", "ArrowLeft", "ArrowUp", "ArrowDown"].includes(e.key);
        if (bow_and_arrow || shifty_mc_shift_face)
        {
            get_selected_sentence = document.getElementsByClassName("sentence-area")[selected_sentence];
            Array.from(get_selected_sentence.children[1].children).forEach(
                (x) => 
                {
                    if (!entire_sentence_selected && shifty_mc_shift_face)
                    {
                        x.classList.add("selected");
                    }
                    else
                    {
                        x.classList.remove("selected");
                    }
                }
            );
            entire_sentence_selected = bow_and_arrow ? false : !entire_sentence_selected;
        }

        function advance_right() //in a function so it can be called in other places
        {
            if (selected_word < words_in_sentence - 1) //if there is at least one more word to right
            {
                selected_word++;
            }
            else if (selected_sentence < number_of_sentences - 1) //if there is at least one more sentence to below, at end of line go to next sentence
            {
                selected_sentence++;
                selected_word = 0; //go to first word in next sentence below
            }
        }

        if (e.key == "ArrowRight") 
        {
            advance_right();
        }
        else if (e.key == "ArrowLeft") 
        {
            if (selected_word > 0) //if there is at least one more word to left
            {
                selected_word--;
            }
            else if (selected_sentence > 0) //if there is at least one more sentence to above, at beginning of line go to previous sentence's end
            {
                selected_sentence--;
                words_in_sentence = document.getElementsByClassName("sentence-area")[selected_sentence].children[1].children.length; //get wordcount of sentence above
                selected_word = words_in_sentence - 1; //go to end of that sentence above
            }
        }
        else if (e.key == "ArrowUp") 
        {
            if (selected_sentence > 0) //if there is at least one more sentence to above
            {
                selected_sentence--;
                words_in_sentence = document.getElementsByClassName("sentence-area")[selected_sentence].children[1].children.length; //get wordcount of sentence above
                words_in_sentence >= selected_word + 1 ? selected_word = selected_word : selected_word = words_in_sentence - 1; //move straight up if possible, otherwise go to end
            }
        }
        else if (e.key == "ArrowDown") 
        {
            if (selected_sentence < number_of_sentences - 1) //if there is at least one more sentence to below
            {
                selected_sentence++;
                words_in_sentence = document.getElementsByClassName("sentence-area")[selected_sentence].children[1].children.length; //get wordcount of sentence below
                words_in_sentence >= selected_word + 1 ? selected_word = selected_word : selected_word = words_in_sentence - 1; //move straight down if possible, otherwise go to end
            }
        }
        else if (["1", "2", "3", "4", "5", "6", "7", "8", "9"].includes(e.key)) //tag a word when we click a number, that number in line on the tag bar will be what it is
        {
            var tag_index = parseInt(e.key) - 1; //in what place on the tag bar is the tag we want? nothing to do with its unique ID number
            var number_of_tags = document.getElementsByClassName("tag-container").length;
            
            if (tag_index <= number_of_tags - 1) //if we are within the number of tags
            {
                var sentence_index = selected_sentence;
                var word_index = selected_word;    
                var tag_id = document.getElementsByClassName("tag-container")[tag_index].children[1].children[1].dataset.index;
                advance_right(); //get coordinates of next word to select and pass to backend to be put in html
                var new_sentence_index = selected_sentence;
                var new_word_index = selected_word;    
                var tag_word = [sentence_index, word_index, entire_sentence_selected, tag_id, new_sentence_index, new_word_index];
                ajax("/", JSON.stringify({ tag_word }), update_sentences);
            }
        }
        else if (e.key == "x" || e.key == "0") //when we click x, delete tag from selected word
        {
            var sentence_index = selected_sentence;
            var word_index = selected_word;
            advance_right(); //get coordinates of next word to select and pass to backend to be put in html
            var new_sentence_index = selected_sentence;
            var new_word_index = selected_word;    
            var tag_word = [sentence_index, word_index, entire_sentence_selected, 0, new_sentence_index, new_word_index];
            ajax("/", JSON.stringify({ tag_word }), update_sentences);
        }

        document.getElementsByClassName("sentence-area")[selected_sentence].children[1].children[selected_word].classList.add("selected");
    });

    /* CHECKBOXES */
    var lastChecked = null;
    $(document).on("click", ".sentence-area input[type=checkbox]", function(e) 
    {
        if (lastChecked) 
        {
            if (e.shiftKey) 
            {
                var from = $('.sentence-area .checkbox-container input').index(e.target);
                var to = $('.sentence-area .checkbox-container input').index(lastChecked);
                var start = Math.min(from, to);
                var end = Math.max(from, to) + 1;
                $('.sentence-area .checkbox-container input').slice(start, end).filter(':not(:disabled)').prop('checked', lastChecked.checked);
            }
            else if (e.altKey) 
            {
                $('.sentence-area .checkbox-container input').each(function() 
                {
                    this.checked = !this.checked;
                });
                e.target.checked = !e.target.checked;
            }
        }

        if (e.metaKey || e.key == "Control") 
        {
            var checkboxes = $('.sentence-area .checkbox-container input').length;
            var number_checked = $('.sentence-area .checkbox-container input:checked').length;
            var check_uncheck = !(checkboxes == number_checked + 1)
            $('.sentence-area .checkbox-container input').prop('checked', check_uncheck);
        }

        lastChecked = this;
    });



    /* CLEAR BUTTONS */
    $(document).on("click", ".clear-all", function() //when we click CLEAR ALL
    {
        are_you_sure_clear("data", { "clear_all": "" })
    });
    $(document).on("click", ".clear-tags", function() //when we click CLEAR TAGS
    {
        are_you_sure_clear("tags, annotation labels, and model data", { "clear_tags": "" })
    });
    $(document).on("click", ".clear-sentences", function() //when we click CLEAR SENTENCES
    {
        are_you_sure_clear("sentence text and annotation labels", { "clear_sentences": "" })
    });
    $(document).on("click", ".clear-model", function() //when we click CLEAR SENTENCES
    {
        are_you_sure_clear("AI model data", { "clear_model": "" })
    });
    function are_you_sure_clear(message, query) 
    {
        var content = `Are you sure you'd like to clear all ${message}? You cannot undo this action. <br><br>`;
        var button = "<button class='form-button' id='clear-continue-button'>YES</button>";
        showAlert(content, button);

        $(document).on("click", "#clear-continue-button", function() 
        {
            ajax("/", JSON.stringify(query), initialize_return);
            $("#alert").css("display", "none");
            $("#alert-stuff").html("");
        });
    }




    var upload_after_download = false; //set as flag, so that upload form is submitted after download is requested

    /* UPLOAD BUTTONS */
    document.getElementById("file-upload").onchange = function() //when a file is chosen to upload
    {
        filename = $("#file-upload").val();
        const lastDot = filename.lastIndexOf('.');
        const ext = filename.substring(lastDot + 1);
        if (ext == "txt" || $(".sentences-area").html() == "") //only ask to save file if there is something to save or adding txt
        {
            document.getElementById("file-upload-form").submit();
            initialize();
            return;
        }

        //Uploading a full dataset (JSON or CSV) will overwrite any existing data. To save your data, enter a filename before clicking continue. 
        var content = "If you would like to save data before overwriting, enter a name below. Either way, click continue to import your file. JSON tag data and TXT files do not overwrite any data. <br><br>";
        content += "<input type='text' name='download-name' placeholder='Filename' id='download-name' class='new-tag-input' autofocus>";
        var button = "<button class='form-button' id='upload-continue-button'>CONTINUE</button>";
        showAlert(content, button);

        $(document).on("click", "#upload-continue-button", async function() //need async?
        {
            if ($("#download-name").val() != "") //if they would like to download...
            {
                // console.log("Requesting download...");
                upload_after_download = true; //set flag for later
                request_file({ download_all: $("#download-name").val() }); //request download, and later it will do the upload (in download function)
            }
            else //only submit if there's nothing to download first
            {
                document.getElementById("file-upload-form").submit();
                initialize();
            }
        });
    };



    /* DOWNLOAD BUTTONS */
    $(document).on("click", ".download-all", function() //when we click save ALL DATA (JSON)
    {
        choose_filename(1);
        $(document).on("click", "#download-button.id-1", function() 
        {
            request_file({ "download_all": $("#download-name").val() });
        });
    });
    $(document).on("click", ".download-tags", function() //when we click save TAGS
    {
        choose_filename(2);
        $(document).on("click", "#download-button.id-2", function() 
        {
            request_file({ "download_tags": $("#download-name").val() });
        });
    });
    $(document).on("click", ".download-sentences", function() //when we click export TEXT
    {
        choose_filename(3);
        $(document).on("click", "#download-button.id-3", function() 
        {
            request_file({ "download_sentences": $("#download-name").val() });
        });
    });
    $(document).on("click", ".download-csv", function() //when we click export CSV
    {
        choose_filename(4);
        $(document).on("click", "#download-button.id-4", function() 
        {
            request_file({ "download_csv": $("#download-name").val() });
        });
    });

    $(document).on("click", ".save-model", function() //when we click SAVE MODEL
    {
        $("#loading").show();
        ajax("/", JSON.stringify({ "save_model": "" }), done_loading);
    });
    function done_loading()
    {
        $("#loading").hide();
    }

    function choose_filename(id_num) //show a popup giving the user a chance to choose a filename
    {
        $(':focus').blur()
        $(".search-box").removeClass("top");
        var content = "<input type='text' name='download-name' placeholder='Filename' id='download-name' class='new-tag-input' autofocus>";
        var button = "<button class='form-button id-" + id_num + "' id='download-button'>DOWNLOAD</button>";
        showAlert(content, button);
    }
    function request_file(query) //request the file from the server with type and name specified in the query... it will download on callback
    {
        ajax("/", JSON.stringify(query), download);
        $("#alert").css("display", "none");
        $("#alert-stuff").html("");
    }
    function download(dict) 
    {
        var fileName = dict["name"] + "." + dict["extension"]; //create filename
        var data = dict["file"]; //retrieve file data
        var element = document.createElement("a"); //create invisible link to click to download
        element.style = "display: none";
        document.body.appendChild(element);

        if (dict["extension"] == "json") 
        {
            var json = JSON.stringify(data);
            var blob = new Blob([json], { type: "octet/stream" });
            var url = window.URL.createObjectURL(blob);
        }
        // else if (dict["extension"] == "txt")
        // {
        //     var url = "data:text/plain;charset=utf-8," + encodeURIComponent(data);
        // }
        // else if (dict["extension"] == "csv")
        // {
        //     var url = "data:text/plain;charset=utf-8," + encodeURIComponent(data);
        // }
        else 
        {
            var url = "data:text/plain;charset=utf-8," + encodeURIComponent(data);
        }


        element.href = url;
        element.download = fileName;
        element.click(); //download the file
        window.URL.revokeObjectURL(url); //I think this means: don't actually open a new window?

        if (upload_after_download) //if there is something waiting to upload
        {
            setTimeout(function() //wait 100ms to give enough time to download (is this reliable?)
            {
                upload_after_download = false; //reset flag
                document.getElementById("file-upload-form").submit(); //submit file upload form
                initialize();
            }, 100);
        }
    }



    /* MENU BUTTON (MOBILE) */
    $(document).on("click", "#menu-dropdown-button", function() //when we click menu
    {
        if (document.getElementsByClassName("menu-items")[0].style.height > "0px") 
        {
            $("#menu-items").animate({ 'height': "0" });
            $("body").animate({ 'margin-top': "100" });
        }
        else 
        {
            $("#menu-items").animate({ 'height': "50" });
            $("body").animate({ 'margin-top': "150" });
        }
    });
    $(document).click(function(e) //click out of menu
    {
        if (!e.target.className.includes("menu-dropdown-button") && document.getElementsByClassName("menu-items")[0].style.height == "50px") 
        {
            $("#menu-items").animate({ 'height': "-=50" });
            $("body").animate({ 'margin-top': "-=50" });
        }
    });



    /* ALERT POPUP */
    function showAlert(content, buttons) 
    {
        $(".search-box").removeClass("top");
        var stuff = "<div class='form'><div class='alert-desc'>" + content + "</div>";
        buttons ? stuff += buttons : stuff += "<button class='form-button' id='okay-button'>OKAY</button>";
        stuff += "</div>";
        $("#alert-stuff").html(stuff);
        $("#alert").css("display", "block");
    }
    $(document).on("click", ".alert-close, #okay-button", function() //when we click the alert x button OR alert okay button
    {
        $("#alert").css("display", "none");
        $("#alert-stuff").html("");
    });



    /* AJAX function with optional callback function parameter */
    function ajax(url_, data_, function_) 
    {
        var params =
        {
            url: url_,
            type: "POST",
            contentType: "application/json",
            data: data_,
        };
        $.ajax(params).done
        (
            function (data) 
            {
                if (function_) 
                {
                    function_(data);
                }
            }
        );
    }



    /* for delaying things to avoid conundrums */
    function debounce(fn, delay) {
        var timer = null;
        return function() {
            var context = this, args = arguments;
            clearTimeout(timer);
            timer = setTimeout(function() {
                fn.apply(context, args);
            }, delay);
        };
    }

});