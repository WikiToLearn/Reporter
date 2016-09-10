from reporter_app.providers import git_provider as gp
from reporter_app.providers import phabricator_provider as pp
from reporter_app.providers import mediawiki_provider as mp

data = {}


def fetch_data(start_date, end_date, repos, phab_groups, mediawiki_langs ):
    data.clear()
    data["git"] = []
    data["phabricator"] = {}
    #getting data from git
    print("Fetching git data...")
    for repo in repos:
        data["git"].append(
            {
                "repo_name": repo,
                "stats_per_user" : gp.get_contributes_per_user(repo, start_date, end_date),
                "stats_total": gp.get_total_contributions(repo, start_date, end_date)
             })
    #getting data from phab
    print("Fetching phabricator data...")
    for ph_gr in phab_groups:
        ph_data = pp.calculate_generic_stats(phab_groups[ph_gr], start_date, end_date)
        data["phabricator"][ph_gr] = ph_data
    return data




if __name__ == '__main__':
    import datetime
    start = datetime.date(2016,9,1)
    end = datetime.date.today()
    fetch_data(start, end, ["WikiToLearn/WikiToLearn", "WikiToLearn/CourseEditor",
                            "WikiToLearn/WikiToLearnSkin", "WikiToLearn/Neverland"],
               {"WikiToLearn (1.0)":["PHID-PROJ-rzv3cv7obh4chahwejq3"]}, [])
    print(data)
