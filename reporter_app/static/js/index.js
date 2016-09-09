$(document).ready(function () {
    //tags currently written in the p
    var current_tags = []
    //function that finds tags in post-text and
    //asks for related_tags to the server metadata entrypoing
    var mark_related_tags = function(){
        var re = /#(.*?)(?=([\s#:]|$))/g;
        var str = $('#post-text').val();
        var m;
        var tags = [];
        while ( (m = re.exec(str)) !== null) {
            if (m[1]!=''){
                tags.push(m[1]);
            }
        }
        for (t of tags){
            if (tags.length != current_tags.lenght ||
            $.inArray(t,current_tags)==-1){
                $.ajax({
                    type: 'POST',
                    url: CURRENT_COLLECTION+'/metadata',
                     data: JSON.stringify(
                         {"method": "related_tags",
                         "tags": tags}),
                    contentType: "application/json",
                    dataType: 'json',
                    success: function(data){
                        $('.add-tag').removeClass('btn-primary');
                        $('.add-tag').addClass('btn-default');
                        for (tag of data.related_tags){
                            $('.add-tag[tag="'+tag+'"]').addClass('btn-primary');
                        }
                    }}
                );
                break;
            }
        }
        current_tags = tags;
    }
    //function that add a tag to the post-text
    var tag_add_click = function(){
        var tag = $(this).attr("tag");
        var post_text = $('#post-text');
        post_text.val(post_text.val() + ' #'+ tag);
        post_text.focus();
        mark_related_tags();
    }
    //function to select the category in the searchbar dropdown menu
    var cat_query_click = function(){
        var cat = $(this).attr("cat");
        var cat_sel = $('#cat-selected');
        var previous_cat = cat_sel.attr("cat");
        cat_sel.text(cat);
        cat_sel.attr("cat", cat);
        if (previous_cat!="ALL" && cat=="ALL"){
            cat_sel.removeClass("btn-info");
            cat_sel.addClass("btn-success");
        }else if(previous_cat=="ALL" && cat!="ALL"){
            cat_sel.removeClass("btn-success");
            cat_sel.addClass("btn-info");
        }
        //a new query is triggered
        query_data(current_query);
    }
    //event handler for tag click in the posts. It adds
    //the tag in the search bar
    var tag_post_click = function (){
        var tg = $(this).attr("tag");
        var query_text = $('#query-text');
        query_text.val(query_text.val() + ' ' + tg);
        current_query = query_text.val().trim();
        query_data(current_query);
    }

    //adding event handler to add tags to post-test
    $('.add-tag').click(tag_add_click);
    //category management in the search bar
    $('.cat-query').click(cat_query_click);
    //click of tags in the post adds the tag to the search bar
    $('.post-tag').click(tag_post_click);
    //event handler for input on post input textarea
    $('#post-text').on("input", mark_related_tags);

    //function that creates element for post
    var create_post_element = function(post){
        element = '<div class="list-group-item row">'+
            '<div class="col-md-9">'+
                '<div class="row">'+post.text + '</div>'+
                '<div class="row">'+
                    '<div class="btn-group" role="group">';
        for (j in post.tags){
            element+= '<a href="#" class="btn btn-default post-tag"'+
                       'tag="'+post.tags[j]+'">'+
                        post.tags[j] + '</a>';
        }
        element += '</div></div>'+
        '<div class ="row">'+
            '<div class="btn-group" role="group" aria-label="...">';
        for (k in post.props){
            element +='<button type="button" class="btn btn-info">'+
                k+'='+ post.props[k]+'</button>';
        }
        element+='</div></div></div>'+
        '<div class="col-md-3 list-group">'+
            '<a href="#" class="list-group-item active cat-query"'+
            'cat="'+ post.category+ '">'+ post.category+
            '</a><a href="#" class="list-group-item">' + post.user +
            '</a></div></div>';
        return element;
    }

    //send data for new post
    $('#send-button').click(function () {
        var post_list = $('#post-list');
        var post_text = $('#post-text').val().trim();
        var category = $('#category-input').val().trim();
        if (post_text.length==0) {
            post_list.text("Insert post!");
        }else{
            if (category.length==0){
                category="main";
            }
            $.ajax({
                type: 'POST',
                url: CURRENT_COLLECTION,
                 data: JSON.stringify(
                     {"text": post_text,
                     "category": category,
                     "user": "valsdav"}),
                contentType: "application/json",
                dataType: 'json',
                success: function(data){
                    //adding the tags
                    var tag_list = $('#tags-list');
                    for (i in data.tags){
                        tg = data.tags[i];
                        if (!(tg in collection_tags)){
                            collection_tags[tg] = 1
                            tag_list.append('<li><a class="btn btn-default add-tag"'+
                            'href="#" role="button" tag="'+tg + '">'+ tg +
                            ' <span class="badge badge-add" tag="'+tg +'">'+1+ '</span></a></li>');
                            $('.add-tag[tag="'+tg+'"]').click(tag_add_click);
                        }else{
                            var badge = $(".badge-add[tag='"+ tg+ "']");
                            badge.text(parseInt(badge.text())+1);
                        }
                    }
                    //adding the category
                    if (!(category in categories_tags)){
                        categories_tags[category] = 1;
                        $('#cats-dropdown').prepend('<li><a href="#" cat="'+
                        category + '" class="cat-query">'+ category + ' ('+
                            categories_tags[category]+')' +'</a></li>');
                        $('.cat-query[cat="'+category+'"]').click(cat_query_click);
                    }else{
                        //catching the right li
                        categories_tags[category] += 1;
                        $('.cat-query[cat="'+category+'"]').text(category +
                                ' ('+ categories_tags[category] + ')');
                    }
                    categories_tags['ALL'] += 1;
                    $('.cat-query[cat="ALL"]').text("ALL" +
                            ' ('+ categories_tags['ALL'] + ')');
                    //empty the post_text form and category
                    $('#post-text').val('');
                    $('.add-tag').removeClass('btn-primary');
                    $('.add-tag').addClass('btn-default');
                    //$('#category-input').val('');
                    //triggering the query
                    query_data(current_query);
                }
            });
        }
    });


    //function to query posts
    var query_data = function(query){
        $.ajax({
            type: 'POST',
            url: CURRENT_COLLECTION+'/query',
             data: JSON.stringify(
                 {"query": query,
                 "category": $('#cat-selected').attr("cat"),
                 "user": "valsdav",
                 "limit":20}),
            contentType: "application/json",
            dataType: 'json',
            success: function(data){
                var post_list = $('#post-list');
                post_list.empty();
                var docs = data.docs;
                var related_tags = data.related_tags;
                for(var i = 0; i< docs.length; i++){
                    var post =docs[i];
                    var element = create_post_element(post);
                    post_list.append(element);
                }
                //adding related tags
                var tag_list = $('#relatedtags-list');
                tag_list.empty();
                var i = 0;
                for (tg in related_tags){
                    if(i==10) break;
                    tag_list.append('<li><a class="btn btn-primary post-tag"'+
                    'href="#" role="button" tag="'+tg + '">'+ tg +
                    ' <span class="badge badge-query" tag="'+tg +'">'+
                    related_tags[tg]+ '</span></a></li>');
                    i++;
                }
                //adding event handler for tag in the post-list
                $('.post-tag').click(tag_post_click);
                $('.cat-query').click(cat_query_click);
            }
        });
    }

    //searchbar input
    var current_query = '';
    $('#query-text').on('input',function(e){
        var q = $(this).val().trim();
        if(q!=current_query){
            current_query = q;
            query_data(current_query);
        }
    });

});
