$(document).ready(function() {
    $('#phab_general_tabel').dataTable({
        "order" : [[1, "desc"]]
    });
    $('#phab_users_table').dataTable({
        "order" : [[2, "desc"]]
    });
    $('#git_projs_table').dataTable({
        "order" : [[1, "desc"]]
    });
    $('#git_users_table').dataTable({
        "order" : [[2, "desc"]]
    });
    $('#wiki_plat_table').dataTable({
        "order" : [[1, "desc"]]
    });
    $('#wiki_users_table').dataTable({
        "order" : [[5, "desc"]]
    });

    var git_data = {
        selectedRepo :"WikiToLearn/WikiToLearn",
        selectedAuthor : "All",
        commitQuery: null
    }

    //Components for git commit viewer
    Vue.component('git-commits', {
    	template: '#git-commits',
    	props: [ 'commits'],

        methods: {
            filtercommits: function(commits){
                return commits.filter( function(cm){
                    if (git_data.commitQuery != null && git_data.commitQuery != ""){
                        var patt = new RegExp(git_data.commitQuery);
                        return patt.test(cm.commit.message);
                    }else {
                        return true;
                    }
                })
            }
        }
    });

    Vue.component('git-searchbar', {
    	template: '#git-searchbar',
    	props: [ 'repos', 'devs'],

        data : function(){
            return  git_data
        },

        methods: {
            chosenRepo: function( event ) {
                var rep = event.target.text;
                this.selectedRepo = rep;
                this.$emit("changeddata");
            },
            chosenAuthor: function( event ) {
                var au = event.target.text;
                this.selectedAuthor = au;
                this.$emit("changeddata")
            }
        }
    });

    Vue.filter('slice', function (value) {
        return value.slice(0,7)
    });

    Vue.filter('fix_date', function (date) {
        var d =  new Date(date);
        return d.toDateString()
    });

    var app = new Vue(

        {
            el: "#commits-stats",

            data: {
                commits : []
            },

            created :  function () {
                this.fetchData();
            },

            methods: {
                fetchData : function() {
                    var self = this;
                    var start_date = $('#commits-stats').attr("start-date");
                    var end_date = $('#commits-stats').attr("end-date");
                    var query = "https://api.github.com/repos/"+ git_data.selectedRepo +
                                "/commits" + "?since=" + start_date + "&until="+ end_date;
                    if (git_data.selectedAuthor != "All"){
                        query += "&author=" + git_data.selectedAuthor
                    }
                    $.getJSON(query, null,
                        function success(data){
                            self.commits = data;
                    });
                },
            }
        }

    );
});
