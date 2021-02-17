$(document).ready(function () {

    function initialize() {
        ajax("/", JSON.stringify({ new_tag: ["", ""] }), update_tags); //////////////////////////////////////// INITIATE TAGS!
        // ajax("/", JSON.stringify({run_manual: ""}), update_sentences); //////////////////////////////////////// INITIATE SENTENCES!
        // debounce(function(){ajax("/", JSON.stringify({run_manual: ""}), update_sentences);}, 100);
        setTimeout(function () { ajax("/", JSON.stringify({ run_manual: "" }), update_sentences); }, 100);
    }
    initialize();



    /* TAGS BAR */
    $(document).on("click", ".new-tag", function () //when we click new tag (+) button
    {
        $(".create-tag").toggle();
    });
    $(document).on("click", ".color-selector-button", function () //when we click SELECT COLOR... button
    {
        $(".color-selector-options").toggle();
    });
    $(document).on("click", ".color-selector-option", function (e) //when we click a color option button
    {
        $(".color-selector-options").toggle();
        var color_html = e.target;
        if (color_html.className != "color-selector-option") {
            color_html = color_html.parentElement;
        }
        color_html = color_html.firstElementChild.className.replace('tag-color ', '');
        // color_html = color_html.firstElementChild.dataset.color;
        $(".color-selector-button").css("background-color", color_html);
        $(".color-selector-button").attr("color", color_html);
    });
    $(document).on("click", ".submit-new-tag", function () //when we click DONE (for new tag) button
    {
        $(".create-tag").hide();
        var tag_name = $(".new-tag-input").val();
        var tag_color = $(".color-selector-button").first().attr("color");
        var new_tag = [tag_name, tag_color]
        $(".new-tag-input").val("");
        $(".color-selector-button").first().css("background-color", "").attr("color", null);

        ajax("/", JSON.stringify({ new_tag }), update_tags);
    });
    $(document).on("click", ".tags .delete", function (e) //when we click delete tag (X) button
    {
        var index = e.target.dataset.index;
        // console.log(index);
        ajax("/", JSON.stringify({ delete_tag: index }), update_tags);
    });
    function update_tags(data) {
        if (data != "") {
            $(".tags-area .tags").html(data);
        }
    }



    /* RUN BUTTONS */
    $(document).on("click", ".run", function () //when we click RUN... button
    {
        $(".run-options").toggle();
    });
    $(document).on("click", ".run-options button", function () //when we click a RUN... menu button
    {
        $(".run-options").hide();
    });
    $(document).on("click", ".run-manual", function () //when we click RUN-MANUAL button
    {
        var text = $("#text-box-field").val();
        $("#text-box-field").val("");
        ajax("/", JSON.stringify({ run_manual: text }), update_sentences);
    });
    $(document).on("click", ".run-corrections", function () //when we click RUN-CORRECTIONS button
    {
        var text = $("#text-box-field").val();
        $("#text-box-field").val();
        ajax("/", JSON.stringify({ run_corrections: text }), update_sentences);
    });
    $(document).on("click", ".run-automatic", function () //when we click RUN-AUTOMATIC button
    {
        var text = $("#text-box-field").val();
        $("#text-box-field").val();
        ajax("/", JSON.stringify({ run_automatic: text }), update_sentences);
    });
    function update_sentences(data) {
        $(".sentences-area").html(data);
    }



    /* ADD OR REMOVE TAG FROM WORD */
    $(document).on("click", ".select-tag-button", function (e) //when we click TAG button below a word
    {
        var sentence_index = this.parentElement.parentElement.dataset.index;
        var word_index = this.parentElement.dataset.index;
        var tag_index = $("input[name=radio]:checked").val();
        var tag_word = [sentence_index, word_index, tag_index];
        ajax("/", JSON.stringify({ tag_word }), update_sentences);
    });
    $(document).on("click", ".sentences-area .delete", function (e) //when we click delete tag word
    {
        var sentence_index = this.parentElement.parentElement.parentElement.dataset.index;
        var word_index = this.parentElement.parentElement.dataset.index;
        var tag_word = [sentence_index, word_index, 0];
        ajax("/", JSON.stringify({ tag_word }), update_sentences);
    });



    /* KEYDOWN - SENTENCE NAV, TAGGING */
    var selected_sentence = 0;
    var selected_word = 0;
    $(document).keydown(function (e) {
        var number_of_sentences = document.getElementsByClassName("sentence-area").length;
        if ($("input").is(":focus") || $("textarea").is(":focus") || number_of_sentences == 0) { return; }
        //dont do stuff from keys if typing somewhere (text field) or if there arent any sentences yet
        var words_in_sentence = document.getElementsByClassName("sentence-area")[selected_sentence].children.length;

        function advance_right() //in a function so it can be called in other places
        {
            if (selected_word < words_in_sentence - 1) //if there is at least one more word to right
            {
                document.getElementsByClassName("sentence-area")[selected_sentence].children[selected_word].classList.remove("selected")
                selected_word++;
                document.getElementsByClassName("sentence-area")[selected_sentence].children[selected_word].classList.add("selected")
            }
            else if (selected_sentence < number_of_sentences - 1) //if there is at least one more sentence to below, at end of line go to next sentence
            {
                document.getElementsByClassName("sentence-area")[selected_sentence].children[selected_word].classList.remove("selected")
                selected_sentence++;
                selected_word = 0; //go to first word in next sentence below
                document.getElementsByClassName("sentence-area")[selected_sentence].children[selected_word].classList.add("selected")
            }
        }

        if (e.key == "ArrowRight") {
            advance_right();
        }
        else if (e.key == "ArrowLeft") {
            if (selected_word > 0) //if there is at least one more word to left
            {
                document.getElementsByClassName("sentence-area")[selected_sentence].children[selected_word].classList.remove("selected")
                selected_word--;
                document.getElementsByClassName("sentence-area")[selected_sentence].children[selected_word].classList.add("selected")
            }
            else if (selected_sentence > 0) //if there is at least one more sentence to above, at beginning of line go to previous sentence's end
            {
                document.getElementsByClassName("sentence-area")[selected_sentence].children[selected_word].classList.remove("selected")
                selected_sentence--;
                words_in_sentence = document.getElementsByClassName("sentence-area")[selected_sentence].children.length; //get wordcount of sentence above
                selected_word = words_in_sentence - 1; //go to end of that sentence above
                document.getElementsByClassName("sentence-area")[selected_sentence].children[selected_word].classList.add("selected")
            }
        }
        else if (e.key == "ArrowUp") {
            if (selected_sentence > 0) //if there is at least one more sentence to above
            {
                document.getElementsByClassName("sentence-area")[selected_sentence].children[selected_word].classList.remove("selected")
                selected_sentence--;
                words_in_sentence = document.getElementsByClassName("sentence-area")[selected_sentence].children.length; //get wordcount of sentence above
                words_in_sentence >= selected_word + 1 ? selected_word = selected_word : selected_word = words_in_sentence - 1; //move straight up if possible, otherwise go to end
                document.getElementsByClassName("sentence-area")[selected_sentence].children[selected_word].classList.add("selected")
            }
        }
        else if (e.key == "ArrowDown") {
            if (selected_sentence < number_of_sentences - 1) //if there is at least one more sentence to below
            {
                document.getElementsByClassName("sentence-area")[selected_sentence].children[selected_word].classList.remove("selected")
                selected_sentence++;
                words_in_sentence = document.getElementsByClassName("sentence-area")[selected_sentence].children.length; //get wordcount of sentence below
                words_in_sentence >= selected_word + 1 ? selected_word = selected_word : selected_word = words_in_sentence - 1; //move straight down if possible, otherwise go to end
                document.getElementsByClassName("sentence-area")[selected_sentence].children[selected_word].classList.add("selected")
            }
        }
        else if (["1", "2", "3", "4", "5", "6", "7", "8", "9"].includes(e.key)) //tag a word when we click a number, that number in line on the tag bar will be what it is
        {
            var sentence_index = selected_sentence;
            var word_index = selected_word;
            var tag_index = parseInt(e.key) - 1; //in what place on the tag bar is the tag we want? nothing to do with its unique ID number
            var number_of_tags = document.getElementsByClassName("tag-container").length;

            if (tag_index <= number_of_tags - 1) //if we are within the number of tags
            {
                var tag_id = document.getElementsByClassName("tag-container")[tag_index].children[1].children[1].dataset.index;
                var tag_word = [sentence_index, word_index, tag_id];
                ajax("/", JSON.stringify({ tag_word }), update_sentences);
                setTimeout(function () { advance_right(); }, 100);
            }
        }
        else if (e.key == "x") //when we click x, delete tag from selected word
        {
            var sentence_index = selected_sentence;
            var word_index = selected_word;

            var tag_word = [sentence_index, word_index, 0];
            ajax("/", JSON.stringify({ tag_word }), update_sentences);
            setTimeout(function () { advance_right(); }, 100);
        }

    });



    /* CLEAR BUTTONS */
    $(document).on("click", ".clear-all", function () //when we click CLEAR ALL
    {
        ajax("/", JSON.stringify({ clear_all: "" }));
        initialize();
    });
    $(document).on("click", ".clear-tags", function () //when we click CLEAR TAGS
    {
        ajax("/", JSON.stringify({ clear_tags: "" }));
        initialize();
    });
    $(document).on("click", ".clear-sentences", function () //when we click CLEAR SENTENCES
    {
        ajax("/", JSON.stringify({ clear_sentences: "" }), update_sentences);
        initialize();
    });



    var upload_after_download = false; //set as flag, so that upload form is submitted after download is requested

    /* UPLOAD BUTTONS */
    document.getElementById("file-upload").onchange = function () //when a file is chosen to upload
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
        content = "If you would like to save data before overwriting, enter a name below. Either way, click continue to import your file. TXT files do not overwrite any data. <br><br>";
        content += "<input type='text' name='download-name' placeholder='Filename' id='download-name' class='new-tag-input' autofocus>";
        button = "<button class='form-button' id='upload-continue-button'>CONTINUE</button>";
        showAlert(content, button);

        $(document).on("click", "#upload-continue-button", async function () {
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
    $(document).on("click", ".download-all", function () //when we click DOWNLOAD JSON
    {
        choose_filename(1);
        $(document).on("click", "#download-button.id-1", function () {
            request_file({ download_all: $("#download-name").val() });
        });
    });
    $(document).on("click", ".download-csv", function () //when we click DOWNLOAD CSV
    {
        choose_filename(4);
        $(document).on("click", "#download-button.id-4", function () {
            request_file({ download_csv: $("#download-name").val() });
        });
    });
    $(document).on("click", ".download-tags", function () //when we click DOWNLOAD TAGS
    {
        choose_filename(2);
        $(document).on("click", "#download-button.id-2", function () {
            request_file({ download_tags: $("#download-name").val() });
        });
    });
    $(document).on("click", ".download-sentences", function () //when we click DOWNLOAD SENTENCES
    {
        choose_filename(3);
        $(document).on("click", "#download-button.id-3", function () {
            request_file({ download_sentences: $("#download-name").val() });
        });
    });
    function choose_filename(id_num) //show a popup giving the user a chance to choose a filename
    {
        $(':focus').blur()
        $(".search-box").removeClass("top");
        content = "<input type='text' name='download-name' placeholder='Filename' id='download-name' class='new-tag-input' autofocus>";
        button = "<button class='form-button id-" + id_num + "' id='download-button'>DOWNLOAD</button>";
        showAlert(content, button);
    }
    function request_file(query) //request the file from the server with type and name specified in the query... it will download on callback
    {
        ajax("/", JSON.stringify(query), download);
        $("#alert").css("display", "none");
        $("#alert-stuff").html("");
    }
    function download(dict) {
        fileName = dict["name"] + "." + dict["extension"]; //create filename
        data = dict["file"]; //retrieve file data
        var element = document.createElement("a"); //create invisible link to click to download
        element.style = "display: none";
        document.body.appendChild(element);

        if (dict["extension"] == "json") {
            var json = JSON.stringify(data),
                blob = new Blob([json], { type: "octet/stream" }),
                url = window.URL.createObjectURL(blob);
        }
        else if (dict["extension"] == "txt") {
            var url = "data:text/plain;charset=utf-8," + encodeURIComponent(data);
        }
        else if (dict["extension"] == "csv") {
            var url = "data:text/plain;charset=utf-8," + encodeURIComponent(data);
        }

        element.href = url;
        element.download = fileName;
        element.click(); //download the file
        window.URL.revokeObjectURL(url); //I think this means: don't actually open a new window?

        if (upload_after_download) //if there is something waiting to upload
        {
            setTimeout(function () //wait 100ms to give enough time to download (is this reliable?)
            {
                upload_after_download = false; //reset flag
                document.getElementById("file-upload-form").submit(); //submit file upload form
                initialize();
            }, 100);
        }
    }



    /* MENU BUTTON (MOBILE) */
    $(document).on("click", "#menu-dropdown-button", function () //when we click menu
    {
        if (document.getElementsByClassName("menu-items")[0].style.height > "0px") {
            $("#menu-items").animate({ 'height': "0" });
            $("body").animate({ 'margin-top': "100" });
        }
        else {
            $("#menu-items").animate({ 'height': "50" });
            $("body").animate({ 'margin-top': "150" });
        }
    });
    $(document).click(function (e) //click out of menu
    {
        if (!e.target.className.includes("menu-dropdown-button") && document.getElementsByClassName("menu-items")[0].style.height == "50px") {
            $("#menu-items").animate({ 'height': "-=50" });
            $("body").animate({ 'margin-top': "-=50" });
        }
    });



    /* ALERT POPUP */
    function showAlert(content, buttons) {
        $(".search-box").removeClass("top");
        var stuff = "<div class='form'><div class='alert-desc'>" + content + "</div>";
        buttons ? stuff += buttons : stuff += "<button class='form-button' id='okay-button'>OKAY</button>";
        stuff += "</div>";
        $("#alert-stuff").html(stuff);
        $("#alert").css("display", "block");
    }
    $(document).on("click", "#okay-button", function () //when we click the alert okay button
    {
        $("#alert").css("display", "none");
        $("#alert-stuff").html("");
    });
    $(document).on("click", ".alert-close", function () //when we click the alert x button
    {
        $("#alert").css("display", "none");
        $("#alert-stuff").html("");
    });



    /* AJAX function with optional callback function parameter */
    function ajax(url_, data_, function_) {
        var params =
        {
            url: url_,
            type: "POST",
            contentType: "application/json",
            data: data_,
        };
        $.ajax(params).done
            (
                function (data) {
                    if (function_) {
                        function_(data);
                    }
                }
            );
    }



    /* for delaying things to avoid conundrums */
    function debounce(fn, delay) {
        var timer = null;
        return function () {
            var context = this, args = arguments;
            clearTimeout(timer);
            timer = setTimeout(function () {
                fn.apply(context, args);
            }, delay);
        };
    }

});