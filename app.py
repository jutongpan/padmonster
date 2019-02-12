## To do:
## Evolution
## Fully collapsible Awoken Skill panel, same as Active Skill
## wu in Awoken Skill in monDataViewer
## Active Skill and Awoken Skill panel remade as Modal 

from flask import Flask, render_template, render_template_string, request, jsonify
import sqlite3
import pandas as pd
import re
import urllib.request

app = Flask(__name__)

img_source = "https://raw.githubusercontent.com/jutongpan/paddata/master/"

local_filename, headers = urllib.request.urlretrieve('https://raw.githubusercontent.com/jutongpan/paddata/master/padmonster.sqlite3')
conn = sqlite3.connect(local_filename)

Attributes_All = pd.read_sql_query("select AttributeName from Attribute;", conn).AttributeName.tolist()

df_monster = pd.read_sql_query("select * from Monster;", conn)
df_monster['Weighted'] = df_monster['Hp']/10 + df_monster['Atk']/5 + df_monster['Rcv']/3
df_monster['Weighted110'] = df_monster['Hp110']/10 + df_monster['Atk110']/5 + df_monster['Rcv110']/3

df_awoken = pd.read_sql_query("select * from AwokenSkillRelation;", conn)
AwokenSkillIds_All = df_awoken.AwokenSkillId.unique()
AwokenSkillIds_All.sort()
df_countAS_byMonAS = df_awoken.groupby(['MonsterId','AwokenSkillId']).size().reset_index(name='counts')
df_countAS_byMonASSuper = df_awoken.groupby(['MonsterId','AwokenSkillId', 'SuperAwoken']).size().reset_index(name='counts')

df_type = pd.read_sql_query("select * from TypeRelation;", conn)
TypeIds_All = pd.read_sql_query("select TypeId from Type;", conn).TypeId.tolist()

df_activeskill = pd.read_sql_query("select * from ActiveSkill;", conn)
df_activeskill['ActiveSkillDescription'] = df_activeskill['ActiveSkillDescription'].str.replace('<img src="img', ''.join(['<img src="', img_source, 'img']))

df_activeskilltype = pd.read_sql_query("select * from ActiveSkillType;", conn)
df_activeskilltype.loc[df_activeskilltype.ActiveSkillType=="傷害吸收無效化", 'ActiveSkillType'] = "大傷吸收無效"
df_activeskilltype.loc[df_activeskilltype.ActiveSkillType=="全場攻擊", 'ActiveSkillType'] = "全體攻擊"
df_activeskilltype.loc[df_activeskilltype.ActiveSkillType=="增加移動時間", 'ActiveSkillType'] = "轉珠時間增加"
df_activeskilltype.loc[df_activeskilltype.ActiveSkillType=="減少移動時間", 'ActiveSkillType'] = "轉珠時間減少"
df_activeskilltype.loc[df_activeskilltype.ActiveSkillType.str.contains("大炮（全體", na=False), 'ActiveSkillType'] = "大炮（全體）"
df_activeskilltype.loc[df_activeskilltype.ActiveSkillType.str.contains("大炮（單體", na=False), 'ActiveSkillType'] = "大炮（單體）"
df_activeskilltype.loc[df_activeskilltype.ActiveSkillType=="天降的寶珠不會產生COMBO", 'ActiveSkillType'] = "無天降"
df_activeskilltype.loc[df_activeskilltype.ActiveSkillType=="屬性傷害吸收無效化", 'ActiveSkillType'] = "屬性傷害吸收無效"
df_activeskilltype.loc[df_activeskilltype.ActiveSkillType=="解除鎖定", 'ActiveSkillType'] = "寶珠解鎖"
df_activeskilltype.loc[df_activeskilltype.ActiveSkillType=="防禦力下降", 'ActiveSkillType'] = "敵人防禦下降"
df_activeskilltype.loc[df_activeskilltype.ActiveSkillType=="傷害增幅（類型）", 'ActiveSkillType'] = "增傷（Type）"
df_activeskilltype.loc[df_activeskilltype.ActiveSkillType=="傷害增幅（屬性）", 'ActiveSkillType'] = "增傷（屬性）"
df_activeskilltype.loc[df_activeskilltype.ActiveSkillType=="傷害增幅（全隊）", 'ActiveSkillType'] = "增傷（按覺醒數量）"
df_activeskilltype.loc[df_activeskilltype.ActiveSkillType=="轉換敵方屬性", 'ActiveSkillType'] = "敵人屬性轉換"
df_activeskilltype.loc[df_activeskilltype.ActiveSkillType=="自身屬性變換", 'ActiveSkillType'] = "自身屬性轉換"
df_activeskilltype.loc[df_activeskilltype.ActiveSkillType=="提升寶珠掉率", 'ActiveSkillType'] = "寶珠掉率提升"
df_activeskilltype.drop(df_activeskilltype[df_activeskilltype.ActiveSkillType=="隨機效果"].index, inplace=True)
df_activeskilltype.drop(df_activeskilltype[df_activeskilltype.ActiveSkillType=="路徑顯示"].index, inplace=True)
ActiveSkillTypes_All = sorted(df_activeskilltype.ActiveSkillType.dropna().unique())

df_leaderskill = pd.read_sql_query("select * from LeaderSkill;", conn)
df_leaderskill['LeaderSkillDescription'] = df_leaderskill['LeaderSkillDescription'].str.replace('<img src="images/.+?>', '')

df_evo = pd.read_sql_query("select * from Evolution;", conn)

conn.close()


@app.route('/')
def index():
    return render_template(
        'index.html',
        img_source = img_source,
        Attributes = Attributes_All,
        TypeIds = TypeIds_All,
        AwokenSkillIds = AwokenSkillIds_All,
        ActiveSkillTypes = ActiveSkillTypes_All
        )


@app.route('/monSearch1', methods=['POST'])
def monSearch1():

    MainAtt   = request.json['MainAtt']
    SubAtt    = request.json['SubAtt']
    Type      = request.json['Type']
    Awoken    = request.json['Awoken']
    IncSuper  = request.json['IncSuper']
    Active    = request.json['Active']
    SortBy    = request.json['SortBy']
    TopN      = request.json['TopN']

    if MainAtt=="Any":
        dff = df_monster
    else:
        dff = df_monster[df_monster.MainAtt==MainAtt]

    if SubAtt=="None":
        dff = dff[dff.SubAtt.isna()]
    elif SubAtt!="Any":
        dff = dff[dff.SubAtt==SubAtt]

    if Type:
        Type = [int(i) for i in Type]
        MonsterIdByType = df_type[df_type.TypeId.isin(Type)].MonsterId.tolist()
        dff = dff[dff.MonsterId.isin(MonsterIdByType)]

    if Awoken:
        Awoken = [int(i) for i in Awoken]
        MonsterIdByNonSuperAwoken_listoflists = [df_countAS_byMonASSuper[(df_countAS_byMonASSuper.SuperAwoken==0) & (df_countAS_byMonASSuper.AwokenSkillId==i) & (df_countAS_byMonASSuper.counts>=Awoken.count(i))].MonsterId.tolist() for i in list(set(Awoken))]
        if IncSuper=="Exclude Super Awoken":
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

    if Active:
        ActiveSkillId_listoflists = [df_activeskilltype[df_activeskilltype.ActiveSkillType == i].ActiveSkillId.tolist() for i in Active]
        ActiveSkillIdByTypes = list(set.intersection(*map(set, ActiveSkillId_listoflists)))
        dff = dff[dff.ActiveSkillId.isin(ActiveSkillIdByTypes)]

    if TopN!="All":
        dff = dff.nlargest(n = int(re.search('[0-9]+', TopN)[0]), columns = SortBy)

    MonsterId = dff.MonsterId.tolist()

    MonsterIcon_source = [None] * len(MonsterId)
    for x in range(len(MonsterId)):
        MonsterIcon_source[x] = "".join(["<button class='btn btn-default btn-monster' value=", str(MonsterId[x]), "><img src=", img_source, "img/MonsterIcon/", str(MonsterId[x]), ".png width='47'></button>"])

    if MonsterId:
        return jsonify(Monster=MonsterIcon_source)

    return jsonify(error='No match!')


@app.route('/monSearch2', methods=['POST'])
def monSearch2():

    FromId  = request.json['FromId']
    ToId    = request.json['ToId']

    if FromId:
        if ToId:
            MonsterId = list(range(int(FromId), int(ToId)+1))
        else:
            MonsterId = [int(FromId)]
    elif ToId:
        MonsterId = [int(ToId)]
    else:
        MonsterId = []

    dff = df_monster[df_monster.MonsterId.isin(MonsterId)]

    MonsterId = dff.MonsterId.tolist()

    MonsterIcon_source = [None] * len(MonsterId)
    for x in range(len(MonsterId)):
        MonsterIcon_source[x] = "".join(["<button class='btn btn-default btn-monster' value='", str(MonsterId[x]), "'><img src=", img_source, "img/MonsterIcon/", str(MonsterId[x]), ".png width='47'></button>"])

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
    MonsterIdSameAS = df_monster.query('ActiveSkillId!=21 & ActiveSkillId==@ActiveSkillId & MonsterId!=@MonsterId').MonsterId.tolist()

    LeaderSkillId = df_monster[df_monster.MonsterId==MonsterId].LeaderSkillId.tolist()[0]
    LeaderSkill = df_leaderskill[df_leaderskill.LeaderSkillId==LeaderSkillId].to_dict('records')[0]
    EvoGroup = df_evo.query('MonsterId == @MonsterId').EvoGroup.tolist()
    MonsterIdSameEvo = df_evo.query('EvoGroup == @EvoGroup & MonsterId != @MonsterId').MonsterId.tolist()

    if MonsterId:
        return render_template(
            'monDataViewer.html',
            img_source = img_source,
            Monster = Monster,
            TypeIds = TypeIds,
            AwokenSkillIds = AwokenSkillIds,
            SuperAwokenSkillIds = SuperAwokenSkillIds,
            ActiveSkill = ActiveSkill,
            MonsterIdSameAS = MonsterIdSameAS,
            LeaderSkill = LeaderSkill,
            MonsterIdSameEvo = MonsterIdSameEvo
            )

    return jsonify(error='No match!')


if __name__ == '__main__':
    app.run(debug=True)