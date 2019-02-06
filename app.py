from flask import Flask, render_template, render_template_string, request, jsonify
import sqlite3
import pandas as pd
import re
import urllib.request

app = Flask(__name__)

img_source = "https://raw.githubusercontent.com/jutongpan/paddata/master/"

local_filename, headers = urllib.request.urlretrieve('https://raw.githubusercontent.com/jutongpan/paddata/master/padmonster.sqlite3')
conn = sqlite3.connect(local_filename)

df_monster = pd.read_sql_query("select * from Monster;", conn)
df_monster['Weighted'] = df_monster['Hp']/10 + df_monster['Atk']/5 + df_monster['Rcv']/3
df_monster['Weighted110'] = df_monster['Hp110']/10 + df_monster['Atk110']/5 + df_monster['Rcv110']/3

df_awoken = pd.read_sql_query("select * from AwokenSkillRelation;", conn)
df_countAS_byMonAS = df_awoken.groupby(['MonsterId','AwokenSkillId']).size().reset_index(name='counts')
df_countAS_byMonASSuper = df_awoken.groupby(['MonsterId','AwokenSkillId', 'SuperAwoken']).size().reset_index(name='counts')

df_type = pd.read_sql_query("select * from TypeRelation;", conn)

df_activeskill = pd.read_sql_query("select * from ActiveSkill;", conn)
df_activeskill['ActiveSkillDescription'] = df_activeskill['ActiveSkillDescription'].str.replace('<img src="img', ''.join(['<img src="', img_source, 'img']))

df_leaderskill = pd.read_sql_query("select * from LeaderSkill;", conn)
df_leaderskill['LeaderSkillDescription'] = df_leaderskill['LeaderSkillDescription'].str.replace('<img src="images/.+?>', '')

conn.close()


@app.route('/')
def index():
    AwokenSkillIds = df_awoken.AwokenSkillId.unique()
    AwokenSkillIds.sort()

    return render_template(
        'index.html',
        img_source = img_source,
        AwokenSkillIds = AwokenSkillIds
        )


@app.route('/monSearch1', methods=['POST'])
def monSearch1():

    MainAtt   = request.json['MainAtt']
    SubAtt    = request.json['SubAtt']
    Awoken    = request.json['Awoken']
    IncSuper  = request.json['IncSuper']
    TopN      = request.json['TopN']

    if MainAtt=="Any":
        dff = df_monster
    else:
        dff = df_monster[df_monster.MainAtt==MainAtt]

    if SubAtt=="None":
        dff = dff[dff.SubAtt.isna()]
    elif SubAtt!="Any":
        dff = dff[dff.SubAtt==SubAtt]

    if Awoken:
        Awoken = [int(i) for i in Awoken]
        MonsterIdByNonSuperAwoken_listoflists = [df_countAS_byMonASSuper[(df_countAS_byMonASSuper.SuperAwoken==0) & (df_countAS_byMonASSuper.AwokenSkillId==i) & (df_countAS_byMonASSuper.counts>=Awoken.count(i))].MonsterId.tolist() for i in list(set(Awoken))]
        if IncSuper==False:
            MonsterIdByNonSuperAwoken = list(set.intersection(*map(set, MonsterIdByNonSuperAwoken_listoflists)))
            dff = dff[dff.MonsterId.isin(MonsterIdByNonSuperAwoken)]
        else:
            MonsterIdByAllAwoken_listoflists = [df_countAS_byMonAS[(df_countAS_byMonAS.AwokenSkillId==i) & (df_countAS_byMonAS.counts>=Awoken.count(i))].MonsterId.tolist() for i in list(set(Awoken))]
            MonsterIdDiff_listofsets = [set.difference(set(MonsterIdByAllAwoken_listoflists[i]), set(MonsterIdByNonSuperAwoken_listoflists[i])) for i in range(len(set(Awoken)))]
            if len(set(Awoken))>1:
                MonsterIdDiffIntersec = set.intersection(*MonsterIdDiff_listofsets)
            else:
                MonsterIdDiffIntersec = set()
            MonsterIdByAllAwoken = set.intersection(*map(set, MonsterIdByAllAwoken_listoflists))
            MonsterIdByAwokenIncOneSup = list(set.difference(MonsterIdByAllAwoken, MonsterIdDiffIntersec))
            dff = dff[dff.MonsterId.isin(MonsterIdByAwokenIncOneSup)]

    if TopN!="All":
        dff = dff.nlargest(n = int(re.search('[0-9]+', TopN)[0]), columns = 'MonsterId')

    MonsterId = dff.MonsterId.tolist()

    MonsterIcon_source = [None] * len(MonsterId)
    for x in range(len(MonsterId)):
        MonsterIcon_source[x] = "".join(["<button class='btn btn-default btn-monster'><input type='hidden' value=", str(MonsterId[x]), "><img src=", img_source, "img/MonsterIcon/", str(MonsterId[x]), ".png width='47'></button>"])

    if MonsterId:
        return jsonify(Monster=MonsterIcon_source)

    return jsonify(error='No match!')


@app.route('/monData', methods=['POST'])
def monData():

    MonsterId = int(request.json['ID'])

    Monster = df_monster[df_monster.MonsterId==MonsterId].to_dict('records')[0]

    TypeIds = df_type[df_type.MonsterId==MonsterId].TypeId.tolist()

    AwokenSkillIds = df_awoken[(df_awoken.MonsterId==MonsterId) & (df_awoken.SuperAwoken==0)].AwokenSkillId.tolist()
    SuperAwokenSkillIds = df_awoken[(df_awoken.MonsterId==MonsterId) & (df_awoken.SuperAwoken==1)].AwokenSkillId.tolist()

    ActiveSkillId = df_monster[df_monster.MonsterId==MonsterId].ActiveSkillId.tolist()[0]
    ActiveSkill = df_activeskill[df_activeskill.ActiveSkillId==ActiveSkillId].to_dict('records')[0]

    LeaderSkillId = df_monster[df_monster.MonsterId==MonsterId].LeaderSkillId.tolist()[0]
    LeaderSkill = df_leaderskill[df_leaderskill.LeaderSkillId==LeaderSkillId].to_dict('records')[0]

    if MonsterId:
        return render_template(
            'monDataViewer.html',
            img_source = img_source,
            Monster = Monster,
            TypeIds = TypeIds,
            AwokenSkillIds = AwokenSkillIds,
            SuperAwokenSkillIds = SuperAwokenSkillIds,
            ActiveSkill = ActiveSkill,
            LeaderSkill = LeaderSkill
            )

    return jsonify(error='No match!')


if __name__ == '__main__':
    app.run(debug=True)