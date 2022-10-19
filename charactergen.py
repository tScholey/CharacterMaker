import os
import pdfrw
from random import *
from pandas import *
from math import ceil
import numpy

rawGitURL = 'https://raw.githubusercontent.com/tScholey/CharacterMaker/master/{}.csv'


races = read_csv(rawGitURL.format('Races'))
classes = read_csv(rawGitURL.format('Classes'))
subs = read_csv(rawGitURL.format('Subs'))
items = read_csv(rawGitURL.format('MagicItems'))
backgrounds = read_csv(rawGitURL.format('Backgrounds'))
profs = read_csv(rawGitURL.format('Profs'))
raceprofs = read_csv(rawGitURL.format('RacialProfs'))
bgprofs = read_csv(rawGitURL.format('BGProficiencies'))
bgflaws = read_csv(rawGitURL.format('BGFlaws'))
bgbonds = read_csv(rawGitURL.format('BGBonds'))
bgideals = read_csv(rawGitURL.format('BGIdeals'))
bgpers = read_csv(rawGitURL.format('BGPersonality'))
feats = read_csv(rawGitURL.format('Feats'))
featreqs = read_csv(rawGitURL.format('FeatsReqs'))
featplus = read_csv(rawGitURL.format('FeatsPlusses'))



cwd = os.getcwd().replace('\\','/')

vowels = ['A','E','I','O','U']
gender = ['Male', 'Female', 'Non-Binary']
alignments = ['Lawful Good', 'Neutral Good', 'Chaotic Good',
              'Lawful Neutral', 'True Neutral', 'Chaotic Neutral',
              'Lawful Evil', 'Neutral Evil', 'Chaotic Evil']
strSkills = ['Athletics']
dexSkills = ['Acrobatics', 'Sleight of Hand','Stealth']
intSkills = ['Arcana', 'History', 'Investigation', 'Nature', 'Religion']
wisSkills = ['Animal Handling', 'Insight', 'Medicine', 'Perception','Survival']
chaSkills = ['Deception', 'Intimidation', 'Performance', 'Persuasion']



def dN(N): #roll an n sided dice
    dN = randint(1,N)
    return dN

def AdN(A,N): #sum a roll of a n-sided dice 
    out = 0
    for a in range(A):
        out += dN(N)
    return out

def getItem(n,r): # gets a random item from the list
    item = []
    for i in range(n):
        gen = randint(0,items.shape[0]-1)
        while type(items.iloc[gen,r]) == float:
            gen = randint(0,items.shape[0]-1)
        item.append(items.iloc[gen,r])
    return item

def getInv(curvl): # generates an inventory given a list in order [amount of common items, amount of uncommon items..., amount of legendary items]
    inv = []
    while len(curvl) >5:
        curvl.pop()
    for i in range(len(curvl)):
        inv.extend(getItem(curvl[i],i))
    return str(inv)

def statGen(): # generates stats using 4d6 drop lowest
    stats = []
    for i in range(6):
        stat = [randint(1,6),randint(1,6),randint(1,6),randint(1,6)]
        stats.append(sum(stat)-min(stat))
    return stats      

def statCheck(stats):
    for i in range(len(stats)):
        if stats[i] > 20:
            stats[i] = 20
    return stats

def getRace():
    race = races.iloc[randint(0,races.shape[0]-1),0]
    return race

def getHeight(race):
    raceInfo = races.loc[races['racename'] == race]
    baseH = raceInfo.iloc[0,1]
    addH = AdN(raceInfo.iloc[0,2],raceInfo.iloc[0,3])
    footH = (baseH + addH) // 12
    inchH =  (baseH + addH) - footH*12
    return [footH,inchH]

def statAdj(race,clas):
    raceInfo = races.loc[races['racename'] == race]
    adjustment = []
    for i in range(4,10):
         adjustment.append(raceInfo.iloc[0,i])
    if raceInfo.iloc[0,10] != 0:
        i = 0
        nonspecamount = raceInfo.iloc[0,10]
        classInfo = classes.loc[classes['Class:']==clas]
        classPrio = classInfo.iloc[0,1]
        prio = [int(classPrio[2*n+1]) for n in range(0,6)]
        while nonspecamount > 0:  
            if adjustment[prio[i]] == 0:
                    adjustment[prio[i]] = 1
                    nonspecamount -= 1
            else:
                i+=1
                    
    return adjustment
     
def statOptimise(stats,clas):
    classInfo = classes.loc[classes['Class:']==clas]
    classPrio = classInfo.iloc[0,1]
    prio = [int(classPrio[2*n+1]) for n in range(0,6)]
    statEnd = [0,0,0,0,0,0]
    stats.sort()
    for i in prio:
        statEnd[i] = max(stats)
        stats.pop()
    return statEnd
    

def getClass():
    clas = classes.iloc[randint(0,classes.shape[0]-1,),0]
    return clas

def getSub(n):
    sub = subs.loc[randint(0,subs.shape[0]-1),n]
    while type(sub) == float:
        sub = subs.loc[randint(0,subs.shape[0]-1),n]
    return sub

def getBG():
    bg = backgrounds.iloc[randint(0,backgrounds.shape[0]-1),0]
    return bg

def getBGProfs(bg,race):
    profs = getRaceProfs(race)
    if type(bgprofs.loc[2,bg]) == float:
        profs.append(bgprofs.loc[0,bg])
        profs.append(bgprofs.loc[1,bg])
    else:
        addedProfs = 0
        while addedProfs < 2:
            priors = []
            r = randint(0,17)
            if r not in priors and bgprofs.loc[r,bg] not in profs:
                profs.append(bgprofs.loc[r,bg])
                priors.append(r)
            else:
                priors.append(r)
    return profs

def getFlaws(bg):
    flaw = bgflaws.loc[randint(0,5),bg]
    return flaw
    
def getPers(bg):
    pers = bgpers.loc[randint(0,7),bg]
    if type(pers) == float:
        pers = bgpers.loc[randint(0,5),bg]
    return pers

def getIdeals(bg):
    ideal = bgideals.loc[randint(0,5),bg]
    return ideal

def getBonds(bg):
    bond = bgbonds.loc[randint(0,5),bg]
    return bond
    


def getPBonus(level):
    profBonus = ceil(level/4) +1
    return profBonus

def statBonus(stat):
    bonus = (stat-10)//2
    return bonus

def getHealth(CON, clas, level,feats):
    classInfo = classes.loc[classes['Class:']==clas]
    con = statBonus(CON)
    hd = classInfo.iloc[0,3]
    baseHP = hd
    rolledHP = AdN(level-1,hd)
    tough = 0
    if 'Tough' in feats:
        tough = 2
    conHP = con * (level-1)
    if con < 0:
        return baseHP + rolledHP + tough*level
    return baseHP + rolledHP + conHP + tough*level

def getRaceProfs(race):
    raceInfo = races.loc[races['racename'] == race]
    profAm = raceInfo.iloc[0,11]
    profs = []
    if profAm > 0:
        while len(profs) < profAm:
            r = randint(0,15)
            priors = []
            if r not in priors and type(raceprofs.loc[r,race]) != float and raceprofs.loc[r,race] not in profs:
                profs.append(raceprofs.loc[r,race])
            else:
                priors.append(r)
    return profs

def getProfs(level, stats, clas, race, bg):
    strProfs = [statBonus(stats[0])]
    dexProfs = [statBonus(stats[1]),statBonus(stats[1]),statBonus(stats[1])]
    intProfs = [statBonus(stats[3]),statBonus(stats[3]),statBonus(stats[3]),statBonus(stats[3]),statBonus(stats[3])]
    wisProfs = [statBonus(stats[4]),statBonus(stats[4]),statBonus(stats[4]),statBonus(stats[4]),statBonus(stats[4])]
    chaProfs = [statBonus(stats[5]),statBonus(stats[5]),statBonus(stats[5]),statBonus(stats[5])]
    pb = getPBonus(level)
    classInfo = classes.loc[classes['Class:']==clas]
    profRolls = classInfo.iloc[0,6]
    proficiencies = getBGProfs(bg,race)
    profRolled = 0
    while profRolled < profRolls:
        priorRolls = []
        r = randint(0,16)
        if r not in priorRolls and type(profs.loc[r,clas]) != float and profs.loc[r,clas] not in proficiencies:
            proficiencies.append(profs.loc[r,clas])
            profRolled +=1
            priorRolls.append(r)
        else:
            priorRolls.append(r)
    for i in proficiencies:
        if i in strSkills:
            strProfs[strSkills.index(i)] += pb
        elif i in dexSkills:
            dexProfs[dexSkills.index(i)] += pb
        elif i in intSkills:
            intProfs[intSkills.index(i)] += pb
        elif i in wisSkills:
            wisProfs[wisSkills.index(i)] += pb
        elif i in chaSkills:
            chaProfs[chaSkills.index(i)] += pb
    if clas == 'Bard' and level >=2:
        for i in strSkills:
            if i not in proficiencies:
                strProfs[strSkills.index(i)] += pb//2
        for i in dexSkills:
            if i not in proficiencies:
                dexProfs[dexSkills.index(i)] += pb//2
        for i in intSkills:
            if i not in proficiencies:
                intProfs[intSkills.index(i)] += pb//2
        for i in wisSkills:
            if i not in proficiencies:
                wisProfs[wisSkills.index(i)] += pb//2
        for i in chaSkills:
            if i not in proficiencies:
                chaProfs[chaSkills.index(i)] += pb//2
        
    outProfs = [strProfs,dexProfs,intProfs,wisProfs,chaProfs]        
    return outProfs, proficiencies

def getSaves(level,stats,clas):
     classInfo = classes.loc[classes['Class:']==clas]
     out = [statBonus(stats[0]),statBonus(stats[1]),statBonus(stats[2]),statBonus(stats[3]),statBonus(stats[4]),statBonus(stats[5])]
     profs = [classInfo.iloc[0,4],classInfo.iloc[0,5]]
     pb = getPBonus(level)
     for i in profs:
         out[i] += pb
     return out
         
 
    
def getFeats(featsIn, stats):
    added = 0
    while added <1:
        r = randint(0,feats.shape[0]-1)
        feat = feats.iloc[r,0]
        priors = []
        
        if feats.iloc[r,3] != 0:
            if feats.iloc[r,3] == 1:    
                if stats[int(featreqs.loc[0,feat])] < 13:
                    priors.append(r)
            elif feats.iloc[r,3] == 2:  
               prereq = [int(featreqs.loc[i,feat]) for i in range(2)]
               if stats[prereq[0]] <13 and stats[prereq[1]] < 13:
                   priors.append(r)
        if feat not in featsIn and r not in priors:
            return feat
            added +=1
        if r in priors:
            r = randint(0,feats.shape[0]-1)      

def getFeatDesc(featlist,stats,clas):
    classInfo = classes.loc[classes['Class:']==clas]
    classPrio = classInfo.iloc[0,1]
    prio = [int(classPrio[2*n+1]) for n in range(0,6)]
    effects = []
    saves = []
    for feat in featlist:
        featInfo = feats.loc[feats['Feat Name'] == feat]       
        if featInfo.iloc[0,1] != 0:
            if stats[prio[0]] % 2 == 1:
                for i in range(featInfo.iloc[0,1]):
                    if featplus.loc[i,feat] == stats.index(max(stats)):
                        stats[stats.index(max(stats))] += 1
            else:
                plus = int(featplus.loc[randint(0,int(featInfo.iloc[0,1])-1),feat])
                stats[plus] += 1
                if feat == 'Resilient':
                    saves.append(plus)
        effects.append(featInfo.iloc[0,2])
    return statCheck(stats), saves, effects

def getASI(level,clas,stats, nstats):
    classInfo = classes.loc[classes['Class:']==clas]
    classPrio = classInfo.iloc[0,1]
    prio = [int(classPrio[2*n+1]) for n in range(0,6)]
    asi = [4*i-1 for i in range (1,5)] + [18]
    if clas == 'Fighter':
        asi += [5,13]
    asi = asi + [level]
    asi.sort()
    feats = []
    for i in range(asi.index(level)):
        if nstats[prio[0]] < 20:
            stat_alloc = 2
            while stat_alloc > 0:
                if nstats[prio[0]] % 2 == 1:
                    poss = []
                    for i in range(featplus.shape[0]):
                        for j in range(featplus.shape[1]):
                            try:
                                int(featplus.iloc[i,j])
                            except:
                                a = 1
                            else: 
                                if int(featplus.iloc[i,j]) == prio[0]:
                                    if featplus.columns[j] not in feats:
                                        poss.append(featplus.columns[j])
                    if len(poss) != 0:
                        feats.append(poss[randint(0,len(poss))-1])
                        stat_alloc -= 2
                        nstats[prio[0]] += 1
                    else:
                        nstats[prio[0]] += 1
                        stats[prio[0]] += 1
                        stat_alloc-=1
                        checkOdd = [0,0,0,0,0,0]
                        for i in range(len(stats)):
                            if nstats[i] % 2 == 1:
                                checkOdd[i] = nstats[i]
                                if checkOdd != [0,0,0,0,0,0]:
                                    stats[checkOdd.index(max(checkOdd))] +=1
                                    nstats[checkOdd.index(max(checkOdd))] +=1
                                    stat_alloc-=1
                                else:
                                    if nstats[prio[0]] != 20:
                                        nstats[prio[0]] += 1
                                        stats[prio[0]] += 1
                                    else:
                                        secStat = nstats
                                        secStat[prio[0]] = 0
                                        nstats[nstats.index(max(secStat))]+=1
                                        stats[nstats.index(max(secStat))]+=1
                                        stat_alloc-=1
                elif max(nstats) % 2 == 0:
                    nstats[prio[0]]+=2
                    stats[prio[0]]+=2
                    stat_alloc-=2
        else:
            feats.append(getFeats(feats,nstats))      
    return feats, stats

def getInit(clas,sub,level,feats,stats):
    init = statBonus(stats[1])
    if sub == 'Swashbuckler':
        init += statBonus(stats[5])
    elif sub == 'Gloom Stalker':
        init += statBonus(stats[4])
    elif sub == 'War Magic':
        init += statBonus(stats[3])
    if clas == 'Bard' and level >= 2:
        init += getPBonus(level)//2	
    if 'Alert' in feats:
        init += 5	
    return init



def makeCharacter(level, *args): # Input a list: [Amount of common items, Amount of uncommon items...]
    race = getRace()
    clas = getClass()
    classInfo = classes.loc[classes['Class:']==clas]
    sub = ''
    if level >= classInfo.iloc[0,2]:
        sub = getSub(clas)
    height = getHeight(race)
    ft = height[0]
    inch = height[1]
    preStats = statOptimise(statGen(),clas)
    adjStats = statAdj(race,clas)
    asistats = statCheck([m + n for m,n in zip(preStats,adjStats)])
    asi = getASI(level,clas,asistats,asistats)
    if race == 'Human (Variant)':
        asi[1].append(getFeats(asi[1],stats))
    deets = getFeatDesc(asi[0],asi[1],clas)
    stats = deets[0]
    feats = asi[0]
    for i in range(len(feats)):
        feats.insert(2*i+1,deets[2][i]) 
    init = getInit(clas,sub,level,feats,stats)
    gend = choices(gender,[0.45,0.45,0.1])[0]
    alignment = choices(alignments,[5/36,5/36,5/36,5/36,5/36,5/36,2/36,2/36,2/36])[0]
    bg = getBG()
    pb = getPBonus(level)
    hp = getHealth(stats[2], clas, level, feats)
    hd = classInfo.iloc[0,3]
    getProf = getProfs(level,stats,clas,race,bg)
    profs = getProf[0]
    proficiencies = getProf[1]
    strProfs = ['No']
    dexProfs = ['No','No','No']
    intProfs = ['No','No','No','No','No']
    wisProfs = ['No','No','No','No','No']
    chaProfs = ['No','No','No','No']
    for i in proficiencies:
        if i in strSkills:
            strProfs[strSkills.index(i)] = 'Yes'
        elif i in dexSkills:
            dexProfs[dexSkills.index(i)] = 'Yes'
        elif i in intSkills:
            intProfs[intSkills.index(i)] = 'Yes'
        elif i in wisSkills:
            wisProfs[wisSkills.index(i)] = 'Yes'
        elif i in chaSkills:
            chaProfs[chaSkills.index(i)] = 'Yes'
    boolProfs = [strProfs,dexProfs,intProfs,wisProfs,chaProfs]
    saves = getSaves(level, stats, clas)
    saveProf = ['No','No','No','No','No','No']
    savingThrows = [classInfo.iloc[0,4],classInfo.iloc[0,5]] + deets[1]
    for i in savingThrows:
        saveProf[i] = 'Yes'
    inv = []
    pers = getPers(bg)
    bond = getBonds(bg)
    flaw = getFlaws(bg)
    ideal = getIdeals(bg)
    
    if len(args) != 0:
        inv = getInv(*args)
    
    data_dict = {
   'Gender': gend,
   'Race' : race,
   'ClassLevel' : sub + ' ' + clas + ' ' + str(level),
   'Background' : bg,
   'Height' : str(ft) + '\'' + str(inch) + '"',
   'ProfB' : '+ ' + str(pb),
   'HPMax' : str(hp),
   'HPCurrent' : str(hp),
   'STR' : str(stats[0]),
   'STRmod' : int(statBonus(stats[0])),
   'DEX' : str(stats[1]),
   'DEXmod' : int(statBonus(stats[1])),
   'CON' : str(stats[2]),
   'CONmod' : int(statBonus(stats[2])),
   'INT' : str(stats[3]),
   'INTmod' : int(statBonus(stats[3])),
   'WIS' : str(stats[4]),
   'WISmod' : int(statBonus(stats[4])),
   'CHA' : str(stats[5]),
   'CHAmod' : int(statBonus(stats[5])),
   'Alignment' : alignment,
   'SavingThrows' : int(saves[0]),
   'SavingThrows2' : int(saves[1]),
   'SavingThrows3' : int(saves[2]),
   'SavingThrows4' : int(saves[3]),
   'SavingThrows5' : int(saves[4]),
   'SavingThrows6' : int(saves[5]),
   'Athletics' : int(profs[0][0]),
   'Acrobatics' : int(profs[1][0]),
   'SleightofHand' : int(profs[1][1]),
   'Stealth' : int(profs[1][2]),
   'Arcana' : int(profs[2][0]),
   'History' : int(profs[2][1]),
   'Investigation' : int(profs[2][2]),
   'Nature' : int(profs[2][3]),
   'Religion' : int(profs[2][4]),
   'Animal Handling' : int(profs[3][0]),
   'Insight' : int(profs[3][1]),
   'Medicine' : int(profs[3][2]),
   'Perception' : int(profs[3][3]),
   'Survival' : int(profs[3][4]),
   'Deception' : int(profs[4][0]),
   'Intimidation' : int(profs[4][1]),
   'Performance' : int(profs[4][2]),
   'Persuasion' : int(profs[4][3]),
   'Passive' : str(10 + profs[3][3]),
   'Equipment' : str(inv)[1:-1],
   'HD' : 'd' + str(hd),
   'HDTotal' : str(level) + 'd' + str(hd),
   'ChBx Acrobatics' : pdfrw.PdfName(boolProfs[1][0]),
   'ChBx Athletics' : pdfrw.PdfName(boolProfs[0][0]),
   'ChBx Sleight' : pdfrw.PdfName(boolProfs[1][1]),
   'ChBx Stealth' : pdfrw.PdfName(boolProfs[1][2]),
   'ChBx Arcana' : pdfrw.PdfName(boolProfs[2][0]),
   'ChBx History' : pdfrw.PdfName(boolProfs[2][1]),
   'ChBx Investigation' : pdfrw.PdfName(boolProfs[2][2]),
   'ChBx Nature' : pdfrw.PdfName(boolProfs[2][3]),
   'ChBx Religion' : pdfrw.PdfName(boolProfs[2][4]),
   'ChBx Animal' : pdfrw.PdfName(boolProfs[3][0]),
   'ChBx Insight' : pdfrw.PdfName(boolProfs[3][1]),
   'ChBx Medicine' : pdfrw.PdfName(boolProfs[3][2]),
   'ChBx Perception' : pdfrw.PdfName(boolProfs[3][3]),
   'ChBx Survival' : pdfrw.PdfName(boolProfs[3][4]),
   'ChBx Deception' : pdfrw.PdfName(boolProfs[4][0]),
   'ChBx Intimidation' : pdfrw.PdfName(boolProfs[4][1]),
   'ChBx Performance' : pdfrw.PdfName(boolProfs[4][2]),
   'ChBx Persuasion' : pdfrw.PdfName(boolProfs[4][3]),
   'ST Strength' :  pdfrw.PdfName(saveProf[0]),
   'ST Dexterity' :  pdfrw.PdfName(saveProf[1]),
   'ST Constitution' :  pdfrw.PdfName(saveProf[2]),
   'ST Intelligence' :  pdfrw.PdfName(saveProf[3]),
   'ST Wisdom' :  pdfrw.PdfName(saveProf[4]),
   'ST Charisma' :  pdfrw.PdfName(saveProf[5]),
   'PersonalityTraits ' : pers,
   'Ideals' : ideal,
   'Bonds' : bond,
   'Flaws' : flaw,
   'Initiative' : int(init),
   'Features and Traits' : str(feats)[1:-1],
   'Help' : deets,

}
    
    
    return data_dict



char = makeCharacter(15)



Sheet_Path = cwd + '/Character Sheet.pdf'
OUTPUT_PATH = cwd + '/{} {} {}.pdf'.format(char['Gender'],char['Race'],char['ClassLevel'])


ANNOT_KEY = '/Annots'
ANNOT_FIELD_KEY = '/T'
ANNOT_VAL_KEY = '/V'
ANNOT_RECT_KEY = '/Rect'
SUBTYPE_KEY = '/Subtype'
WIDGET_SUBTYPE_KEY = '/Widget'


def write_fillable_pdf(input_pdf_path, output_pdf_path, data_dict):
    template_pdf = pdfrw.PdfReader(input_pdf_path)
    template_pdf.Root.AcroForm.update(pdfrw.PdfDict(NeedAppearances=pdfrw.PdfObject('true'))) 
    annotations = template_pdf.pages[0][ANNOT_KEY]
    for annotation in annotations:
        if annotation[SUBTYPE_KEY] == WIDGET_SUBTYPE_KEY:
            if annotation[ANNOT_FIELD_KEY]:
                key = annotation[ANNOT_FIELD_KEY][1:-1]
                if key in data_dict.keys():
                    annotation.update(
                       pdfrw.PdfDict(AP=data_dict[key], V=data_dict[key])
                    )
    pdfrw.PdfWriter().write(output_pdf_path, template_pdf)


def addPlus(data_dict):
    for i in data_dict:
        if type(data_dict[i]) == int:
            if data_dict[i] >= 0:
                data_dict[i] = '+' + str(data_dict[i])
            else:
                data_dict[i] = str(data_dict[i])
    return data_dict


write_fillable_pdf(Sheet_Path, OUTPUT_PATH, addPlus(char))

def makeParty(n,level,*args):
    for i in range(n):
        chars = makeCharacter(level,*args)
        write_fillable_pdf(Sheet_Path, cwd + '/{} {} {}.pdf'.format(chars['Gender'],chars['Race'],chars['ClassLevel']), addPlus(chars))

