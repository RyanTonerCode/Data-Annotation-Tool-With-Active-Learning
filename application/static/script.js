$(document).ready(function(){


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
        $(".color-selector-options").toggle();
        var color_html = e.target;
        if (color_html.className != "color-selector-option")
        {
            color_html = color_html.parentElement;
        }
        color_html = color_html.firstElementChild.className.replace('tag-color ','');
        // color_html = color_html.firstElementChild.dataset.color;
        // console.log(color_html);
        $(".color-selector-button").css("background-color", color_html);
        $(".color-selector-button").attr("color", color_html);
    });

    ajax("/", JSON.stringify({new_tag: ["", ""]}), update_tags);

    $(document).on("click", ".submit-new-tag", function() //when we click DONE (for new tag) button
    {
        $(".create-tag").hide();
        var tag_name = $(".new-tag-input").val();
        // console.log(tag_name);
        var tag_color = $(".color-selector-button").first().attr("color");
        // console.log(tag_color);
        var new_tag = [tag_name, tag_color]
        $(".new-tag-input").val("");
        $(".color-selector-button").first().css("background-color", "").attr("color", null);

        ajax("/", JSON.stringify({new_tag}), update_tags);
    });

    function update_tags(data)
    {
        if (data != "")
        {
            $(".tags-area .tags").html(data);
        }
    }

    $(document).on("click", ".tags .delete", function(e) //when we click delete tag (X) button
    {
        var index = e.target.dataset.index;
        // console.log(index);
        ajax("/", JSON.stringify({delete_tag: index}), update_tags);
    });


    ajax("/", JSON.stringify({run_manual: ""}), update_sentences);

    $(document).on("click", ".run", function() //when we click RUN... button
    {
        $(".run-options").toggle();
    });
    $(document).on("click", ".run-options button", function() //when we click a RUN... menu button
    {
        $(".run-options").hide();
    });
    $(document).on("click", ".run-manual", function() //when we click RUN-MANUAL button
    {
        var text = $("#text-box-field").val();
        // console.log(text);
        ajax("/", JSON.stringify({run_manual: text}), update_sentences);
    });
    $(document).on("click", ".run-corrections", function() //when we click RUN-CORRECTIONS button
    {
        var text = $("#text-box-field").val();
        // console.log(text);
        ajax("/", JSON.stringify({run_corrections: text}), update_sentences);
    });
    $(document).on("click", ".run-automatic", function() //when we click RUN-AUTOMATIC button
    {
        var text = $("#text-box-field").val();
        // console.log(text);
        ajax("/", JSON.stringify({run_automatic: text}), update_sentences);
    });

    function update_sentences(data)
    {
        $(".sentences-area").html(data);
    }




    $(document).on("click", ".select-tag-button", function(e) //when we click TAG button below a word
    {
        var sentence_index = this.parentElement.parentElement.dataset.index;
        var word_index = this.parentElement.dataset.index;
        var tag_index = $("input[name=radio]:checked").val();

        // console.log(sentence_index);

        var tag_word = [sentence_index, word_index, tag_index];
        ajax("/", JSON.stringify({tag_word}), update_sentences);
    });

    $(document).on("click", ".sentences-area .delete", function(e) //when we click delete tag word
    {
        var sentence_index = this.parentElement.parentElement.parentElement.dataset.index;
        var word_index = this.parentElement.parentElement.dataset.index;

        var tag_word = [sentence_index, word_index, -1];
        ajax("/", JSON.stringify({tag_word}), update_sentences);
    });


    var selected_sentence = 0;
    var selected_word = 0;

    $(document).keydown(function(e)
    {
        var number_of_sentences = document.getElementsByClassName("sentence-area").length;
        var words_in_sentence = document.getElementsByClassName("sentence-area")[selected_sentence].children.length;
        // console.log(e.key);

        if (e.key == "ArrowRight")
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
        else if (e.key == "ArrowLeft")
        {
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
        else if (e.key == "ArrowUp")
        {
            if (selected_sentence > 0) //if there is at least one more sentence to above
            {
                document.getElementsByClassName("sentence-area")[selected_sentence].children[selected_word].classList.remove("selected")
                selected_sentence--;
                words_in_sentence = document.getElementsByClassName("sentence-area")[selected_sentence].children.length; //get wordcount of sentence above
                words_in_sentence >= selected_word ? selected_word = selected_word : selected_word = words_in_sentence - 1; //move straight up if possible, otherwise go to end
                document.getElementsByClassName("sentence-area")[selected_sentence].children[selected_word].classList.add("selected")
            }
        }
        else if (e.key == "ArrowDown")
        {
            if (selected_sentence < number_of_sentences - 1) //if there is at least one more sentence to below
            {
                document.getElementsByClassName("sentence-area")[selected_sentence].children[selected_word].classList.remove("selected")
                selected_sentence++;
                words_in_sentence = document.getElementsByClassName("sentence-area")[selected_sentence].children.length; //get wordcount of sentence below
                words_in_sentence >= selected_word ? selected_word = selected_word : selected_word = words_in_sentence - 1; //move straight down if possible, otherwise go to end
                document.getElementsByClassName("sentence-area")[selected_sentence].children[selected_word].classList.add("selected")
            }
        }
        else if (e.key in ["1","2","3","4","5","6","7","8","9"]) //tag a word when we click a number, that number in line on the tag bar will be what it is
        {
            var sentence_index = selected_sentence;
            var word_index = selected_word;
            var tag_index = parseInt(e.key) - 1; //in what place on the tag bar is the tag we want? nothing to do with its unique ID number
            var number_of_tags = document.getElementsByClassName("tag-container").length;

            if (tag_index <= number_of_tags - 1) //if we are within the number of tags
            {
                var tag_id = document.getElementsByClassName("tag-container")[tag_index].children[1].children[1].dataset.index;
                console.log(tag_id);

                var tag_word = [sentence_index, word_index, tag_id];
                ajax("/", JSON.stringify({tag_word}), update_sentences);    
            }
        }
        else if (e.key == "x") //when we click x, delete tag from selected word
        {
            var sentence_index = selected_sentence;
            var word_index = selected_word;
    
            var tag_word = [sentence_index, word_index, -1];
            ajax("/", JSON.stringify({tag_word}), update_sentences);    
        }

    });











    $(document).on("click", ".clear-tags", function() //when we click CLEAR TAGS
    {        
        ajax("/", JSON.stringify({clear_tags: ""}), update_tags);
    });
    $(document).on("click", ".clear-sentences", function() //when we click CLEAR SENTENCES
    {        
        ajax("/", JSON.stringify({clear_sentences: ""}), update_sentences);
    });
    document.getElementById("file-upload").onchange = function() //when a file is chosen to upload
    {
        document.getElementById("file-upload-form").submit();
    };
    $(document).on("click", ".download-tags", function() //when we click DOWNLOAD TAGS
    {        
        ajax("/", JSON.stringify({download_tags: ""}));
    });
    $(document).on("click", ".download-sentences", function() //when we click DOWNLOAD SENTENCES
    {        
        ajax("/", JSON.stringify({download_sentences: ""}));
    });









    /* MENU BUTTON (MOBILE) */
     $(document).on("click", "#menu-dropdown-button", function() //when we click menu
    {
        if (document.getElementsByClassName("menu-items")[0].style.height > "0px")
        {
            $("#menu-items").animate({'height': "0"});
            $("body").animate({'margin-top': "100"});
        }
        else
        {
            $("#menu-items").animate({'height': "50"});
            $("body").animate({'margin-top': "150"});
        }
    });
    $(document).click(function(e) //click out of menu
    {
        if (!e.target.className.includes("menu-dropdown-button") && document.getElementsByClassName("menu-items")[0].style.height == "50px")
        {
            $("#menu-items").animate({'height': "-=50"});
            $("body").animate({'margin-top': "-=50"});
        }
    });




   // ALERT POPUP 
    function showAlert(text)
    {
        $(".search-box").removeClass("top");
        $("#listDropdown").slideUp(750, function(){setTimeout(function(){$(".listDropdown").empty();},250);});
        var stuff = "<div class='form'><div class='alert-desc'>" + text + "</div>"
        stuff += "<button class='form-button' id='okay-button'>OKAY</button></div>" 
        $("#alert-stuff").html(stuff);
        $("#alert").css("display", "block");
    }
    $(document).on("click", "#okay-button", function() //when we click the alert okay button
    {
        $("#alert").css("display", "none");
    });
    $(document).on("click", ".alert-close", function() //when we click the alert x button
    {
        $("#alert").css("display", "none");
    });









    function ajax(url_, data_, function_)
    {
        var params = 
        {
            url: url_,
            type: "POST",
            contentType: "application/json",
            data: data_,
        };
        //console.log(params);
        $.ajax(params).done
        (
            function(data)
            {
                if (function_)
                {
                    function_(data);
                }
            }
        );
    }  

    function debounce(fn, delay) 
    {
        var timer = null;
        return function() 
        {
          var context = this, args = arguments;
          clearTimeout(timer);
          timer = setTimeout(function() 
          {
            fn.apply(context, args);
          }, delay);
        };
    }

});