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

df_type = pd.read_sql_query("select * from TypeRelation;", conn)

df_activeskill = pd.read_sql_query("select * from ActiveSkill;", conn)
df_activeskill['ActiveSkillDescription'] = df_activeskill['ActiveSkillDescription'].str.replace('<img src="img', ''.join(['<img src="', img_source, 'img']))

df_leaderskill = pd.read_sql_query("select * from LeaderSkill;", conn)
df_leaderskill['LeaderSkillDescription'] = df_leaderskill['LeaderSkillDescription'].str.replace('<img src="images/.+?>', '')

conn.close()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/monSearch1', methods=['POST'])
def monSearch1():

    MainAtt = request.form['MainAtt']
    SubAtt  = request.form['SubAtt']
    TopN    = request.form['TopN']

    if MainAtt=="Any":
        dff = df_monster
    else:
        dff = df_monster[df_monster.MainAtt==MainAtt]

    if SubAtt=="None":
        dff = dff[dff.SubAtt.isna()]
    elif SubAtt!="Any":
        dff = dff[dff.SubAtt==SubAtt]

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

    print(request.json)
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