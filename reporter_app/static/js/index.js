$(document).ready(function() {
    $('#phab_general_tabel').dataTable({
        "order" : [[4, "desc"]]
    });
    $('#phab_users_table').dataTable({
        "order" : [[2, "desc"]]
    });
    $('#git_projs_table').dataTable({
        "order" : [[1, "desc"]]
    });
    $('#git_users_table').dataTable({
        "order" : [[3, "desc"]]
    });
    $('#wiki_plat_table').dataTable({
        "order" : [[1, "desc"]]
    });
    $('#wiki_users_table').dataTable({
        "order" : [[5, "desc"]]
    });
});
