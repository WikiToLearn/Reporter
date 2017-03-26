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

        computed: {
            filteredcommits: function(){
                return this.commits.filter( function(cm){
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
    /* Plots */
    var gitResponse, mediawikiResponse, phabricatorResponse;
    // Set the json for the requests
    var gitData = {
        'stats': 'total',
        'collection': 'git'
    };
    var mediawikiData = {
        'stats': 'total',
        'collection': 'mediawiki'
    };
    var phabricatorData = {
        'stats': 'total',
        'collection': 'phabricator'
    };

    $.when(
        // Get the total commits via ajax request
        $.ajax({
            type: "POST",
            url: "/history",
            data: JSON.stringify(gitData),
            contentType: "application/json",
            dataType: "json",
            success: function(data) {
                gitResponse = data;
            },
            error: function(data) {
                console.log("Failed to load git data for plotly.");
            }
        }),
        $.ajax({
            type: "POST",
            url: "/history",
            data: JSON.stringify(mediawikiData),
            contentType: "application/json",
            dataType: "json",
            success: function(data) {
                mediawikiResponse = data;
            },
            error: function(data) {
                console.log("Failed to load git data for plotly.");
            }
        }),
        $.ajax({
            type: "POST",
            url: "/history",
            data: JSON.stringify(phabricatorData),
            contentType: "application/json",
            dataType: "json",
            success: function(data) {
                phabricatorResponse = data;
            },
            error: function(data) {
                console.log("Failed to load git data for plotly.");
            }
        })
    ).then(function () {
        // Get the column data for git 
        var gitTimes = gitResponse.map(function(item) {
            return item.end_date;
        });
        var n_commits = gitResponse.map(function(item) {
            return item.n_commits;
        });
        // Get the column data for mediawiki 
        var mediawikiTimes = mediawikiResponse.map(function(item) {
            return item.end_date;
        });
        var edits = mediawikiResponse.map(function(item) {
            return item.edits;
        });
        // Get the column data for phabricator 
        var phabricatorTimes = phabricatorResponse.map(function(item) {
            return item.end_date;
        });
        var tasks = phabricatorResponse.map(function(item) {
            return item.resolved;
        });
        // Set the default trace data for the plots
        trace = {
            x: '',
            y: '',
            mode: 'line',
            name: '',
            visible: false,
            line: {
                shape: 'spline',
                color: ''
            }
        }; 
        // Set the custom option for the different plots
        gitTrace = $.extend(true, {}, trace);
        // This is the first plot a user will see, so it
        // should be set as visible
        gitTrace.visible = true;
        gitTrace.x = gitTimes;
        gitTrace.y = n_commits;
        gitTrace.name = 'Github';
        gitTrace.line.color = '#69b140';

        mediawikiTrace = $.extend(true, {}, trace);
        mediawikiTrace.x = mediawikiTimes;
        mediawikiTrace.y = edits;
        mediawikiTrace.name = 'WikiToLearn';
        mediawikiTrace.line.color = '#ffbc31';

        phabricatorTrace = $.extend(true, {}, trace);
        phabricatorTrace.x = phabricatorTimes;
        phabricatorTrace.y = tasks;
        phabricatorTrace.name = 'Phabricator';
        phabricatorTrace.line.color = '#db3e14'; 

        // Pack the data and send it to the plotting function
        data = [gitTrace, mediawikiTrace, phabricatorTrace];
        plotStats(data);
    });

    function plotStats(data) {
        var d3 = Plotly.d3;
        var WIDTH_IN_PERCENT_OF_PARENT = 100,
            HEIGHT_IN_PERCENT_OF_PARENT = 40;

        // bind to new element and use it to plot data
        var gd3 = d3.select('#global-stats-plot')
                    .style({
                        width: WIDTH_IN_PERCENT_OF_PARENT + '%',
                        height: HEIGHT_IN_PERCENT_OF_PARENT + 'rem',
                        'margin-top': '3 rem'
                    });
        var gd = gd3.node()

        // Call the plotting function and define the dropdown
        // buttons
        Plotly.plot(gd, data, {
            updatemenus: [{
                y: 1,
                x: -0.1,
                yanchor: 'top',
                buttons: [{
                    method: 'restyle',
                    args: ['visible', [true, false, false]],
                    label: 'Github'
                }, {
                    method: 'restyle',
                    args: ['visible', [false, true, false]],
                    label: 'MediaWiki'
                }, {
                    method: 'restyle',
                    args: ['visible', [false, false, true]],
                    label: 'Phabricator'
                }, {
                    method: 'restyle',
                    args: [{
                        'visible': [true, true, true],
                        'line.color': ['#ffbc31', '#6ab141', '#db3e14']
                    }],
                    label: 'All'
                }]
            }],
        });

        // Make the plot resposnsive
        window.onresize = function() {
            Plotly.Plots.resize(gd);
        };
    }
});

