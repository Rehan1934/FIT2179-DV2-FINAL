from pathlib import Path
import json
import re
import pandas as pd
import numpy as np

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / 'data' / 'raw'
PROCESSED = BASE / 'data' / 'processed'
SPECS = BASE / 'specs'
CSS = BASE / 'css'
JS = BASE / 'js'
for d in [PROCESSED, SPECS, CSS, JS]:
    d.mkdir(parents=True, exist_ok=True)
for d in [PROCESSED, SPECS]:
    for f in d.glob('*'):
        if f.is_file():
            f.unlink()

def clean_col(x):
    x = str(x).strip().lower()
    x = re.sub(r'[^a-z0-9]+', '_', x)
    return re.sub(r'_+', '_', x).strip('_')

def find_file(*names):
    for n in names:
        p = RAW / n
        if p.exists():
            return p
    raise FileNotFoundError('Missing raw file. Tried: ' + ', '.join(names))

def yes_no(s):
    return s.astype(str).str.strip().str.lower().map({'yes':1,'no':0,'true':1,'false':0,'1':1,'0':0}).fillna(0).astype(int)

def pct(n, d):
    return round(float(n) / float(d) * 100, 1) if d else 0.0

def save_csv(df, name):
    df.to_csv(PROCESSED / name, index=False)
    print(f'Saved data/processed/{name} ({len(df)} rows)')

def save_spec(name, spec):
    spec['config'] = CONFIG
    (SPECS / name).write_text(json.dumps(spec, indent=2), encoding='utf-8')
    print(f'Saved specs/{name}')

CONFIG = {
    'background': 'transparent',
    'font': 'Inter',
    'view': {'stroke': None},
    'axis': {'labelFont': 'Inter', 'titleFont': 'Inter', 'labelColor': '#52616b', 'titleColor': '#132238', 'gridColor': '#e8eef5', 'domainColor': '#d6e0ea', 'tickColor': '#d6e0ea'},
    'legend': {'labelFont': 'Inter', 'titleFont': 'Inter', 'labelColor': '#52616b', 'titleColor': '#132238', 'orient': 'bottom'},
    'title': {'font': 'Inter', 'fontWeight': 800, 'color': '#132238', 'anchor': 'start'}
}
ASEAN = ['Brunei','Cambodia','Indonesia','Laos','Malaysia','Myanmar','Philippines','Singapore','Thailand','Vietnam']
COORDS = {'Brunei':(114.7277,4.5353),'Cambodia':(104.991,12.5657),'Indonesia':(113.9213,-0.7893),'Laos':(102.4955,19.8563),'Malaysia':(101.9758,4.2105),'Myanmar':(95.956,21.9162),'Philippines':(121.774,12.8797),'Singapore':(103.8198,1.3521),'Thailand':(100.9925,15.87),'Vietnam':(108.2772,14.0583)}
FIX_COUNTRY = {'Brunei Darussalam':'Brunei', "Lao People's Democratic Republic":'Laos', 'Lao PDR':'Laos', 'Viet Nam':'Vietnam'}

# ===================== DATA CLEANING =====================
# Student survey
student = pd.read_csv(find_file('student_mental_health.csv', 'Student Mental health.csv'))
student.columns = [clean_col(c) for c in student.columns]
student = student.rename(columns={
    'choose_your_gender':'gender', 'your_current_year_of_study':'year_of_study', 'what_is_your_cgpa':'cgpa',
    'do_you_have_depression':'depression', 'do_you_have_anxiety':'anxiety', 'do_you_have_panic_attack':'panic_attack',
    'did_you_seek_any_specialist_for_a_treatment':'specialist_treatment'
})
need = ['gender','year_of_study','cgpa','depression','anxiety','panic_attack','specialist_treatment']
missing = [c for c in need if c not in student.columns]
if missing:
    raise ValueError(f'Student file missing {missing}. Columns found: {list(student.columns)}')
for c in student.select_dtypes(include='object').columns:
    student[c] = student[c].astype(str).str.strip()
student['gender'] = student['gender'].str.title()
student['cgpa'] = student['cgpa'].str.replace('–','-', regex=False)
def clean_year(v):
    m = re.search(r'(\d+)', str(v))
    return f'Year {m.group(1)}' if m else str(v).title()
student['year_of_study'] = student['year_of_study'].apply(clean_year)
for c in ['depression','anxiety','panic_attack','specialist_treatment']:
    student[c + '_flag'] = yes_no(student[c])
student['symptom_count'] = student[['depression_flag','anxiety_flag','panic_attack_flag']].sum(axis=1)
student['any_symptom'] = (student['symptom_count'] > 0).astype(int)
student['multiple_symptoms'] = (student['symptom_count'] >= 2).astype(int)
student['symptomatic_no_treatment'] = ((student['any_symptom'] == 1) & (student['specialist_treatment_flag'] == 0)).astype(int)
N = len(student)
save_csv(student, 'student_clean.csv')

student_summary = pd.DataFrame([
    ['Any reported symptom', pct(student.any_symptom.sum(), N), int(student.any_symptom.sum()), N, 'Symptoms'],
    ['Anxiety', pct(student.anxiety_flag.sum(), N), int(student.anxiety_flag.sum()), N, 'Symptoms'],
    ['Depression', pct(student.depression_flag.sum(), N), int(student.depression_flag.sum()), N, 'Symptoms'],
    ['Panic attacks', pct(student.panic_attack_flag.sum(), N), int(student.panic_attack_flag.sum()), N, 'Symptoms'],
    ['Multiple symptoms', pct(student.multiple_symptoms.sum(), N), int(student.multiple_symptoms.sum()), N, 'Overlap'],
    ['Specialist treatment', pct(student.specialist_treatment_flag.sum(), N), int(student.specialist_treatment_flag.sum()), N, 'Support']
], columns=['metric','percentage','count','total','type'])
save_csv(student_summary, 'student_summary.csv')

symptom_rates = pd.DataFrame([
    ['Depression', pct(student.depression_flag.sum(), N), int(student.depression_flag.sum()), N],
    ['Anxiety', pct(student.anxiety_flag.sum(), N), int(student.anxiety_flag.sum()), N],
    ['Panic attacks', pct(student.panic_attack_flag.sum(), N), int(student.panic_attack_flag.sum()), N]
], columns=['symptom','percentage','count','total'])
save_csv(symptom_rates, 'symptom_rates.csv')

overlap = student.groupby('symptom_count').size().reindex([0,1,2,3], fill_value=0).reset_index(name='count')
overlap['percentage'] = (overlap['count']/N*100).round(1)
overlap['label'] = overlap['symptom_count'].map({0:'No reported symptoms',1:'One symptom',2:'Two symptoms',3:'All three symptoms'})
save_csv(overlap, 'symptom_overlap.csv')

gap = pd.DataFrame([
    ['Reported at least one symptom', pct(student.any_symptom.sum(), N), int(student.any_symptom.sum()), N, 'Symptom'],
    ['Symptomatic but no specialist treatment', pct(student.symptomatic_no_treatment.sum(), N), int(student.symptomatic_no_treatment.sum()), N, 'Gap'],
    ['Sought specialist treatment', pct(student.specialist_treatment_flag.sum(), N), int(student.specialist_treatment_flag.sum()), N, 'Support']
], columns=['category','percentage','count','total','type'])
save_csv(gap, 'treatment_gap.csv')

gender_rows=[]
for g, sub in student.groupby('gender'):
    for symptom, col in [('Anxiety','anxiety_flag'),('Depression','depression_flag'),('Panic attacks','panic_attack_flag')]:
        gender_rows.append([g, symptom, pct(sub[col].sum(), len(sub)), int(sub[col].sum()), len(sub)])
save_csv(pd.DataFrame(gender_rows, columns=['gender','symptom','percentage','count','total']), 'gender_symptoms.csv')

year_rows=[]
for y, sub in student.groupby('year_of_study'):
    order = int(re.search(r'\d+', y).group()) if re.search(r'\d+', y) else 99
    for symptom, col in [('Anxiety','anxiety_flag'),('Depression','depression_flag'),('Panic attacks','panic_attack_flag')]:
        year_rows.append([y, order, symptom, pct(sub[col].sum(), len(sub)), int(sub[col].sum()), len(sub)])
save_csv(pd.DataFrame(year_rows, columns=['year_of_study','year_order','symptom','percentage','count','total']), 'year_symptoms.csv')

cgpa_order = ['0 - 1.99','2.00 - 2.49','2.50 - 2.99','3.00 - 3.49','3.50 - 4.00']
cgpa_rows=[]
for i, c in enumerate(cgpa_order):
    sub = student[student.cgpa == c]
    if len(sub):
        cgpa_rows.append([c, i, pct(sub.any_symptom.sum(), len(sub)), int(sub.any_symptom.sum()), len(sub)])
save_csv(pd.DataFrame(cgpa_rows, columns=['cgpa','order','percentage','count','total']), 'cgpa_symptoms.csv')

# Global data
xl = find_file('global_mental_health.xlsx', 'Mental health Depression disorder Data.xlsx')
prev = pd.read_excel(xl, sheet_name='prevalence-by-mental-and-substa')
prev = prev.rename(columns={'Entity':'country','Code':'code','Year':'year','Depression (%)':'depression','Anxiety disorders (%)':'anxiety','Schizophrenia (%)':'schizophrenia','Bipolar disorder (%)':'bipolar','Eating disorders (%)':'eating','Drug use disorders (%)':'drug_use','Alcohol use disorders (%)':'alcohol_use'})
prev['country'] = prev['country'].replace(FIX_COUNTRY)
asean_prev = prev[prev.country.isin(ASEAN)].copy()
trend = asean_prev.melt(id_vars=['country','code','year'], value_vars=['depression','anxiety'], var_name='condition', value_name='prevalence')
trend['condition'] = trend['condition'].map({'depression':'Depression','anxiety':'Anxiety'})
trend['prevalence'] = pd.to_numeric(trend['prevalence'], errors='coerce').round(2)
save_csv(trend, 'asean_trend.csv')
save_csv(trend[trend.country == 'Malaysia'], 'malaysia_trend.csv')
latest = asean_prev[asean_prev.year == 2017].copy()
latest['longitude'] = latest.country.map(lambda c: COORDS[c][0])
latest['latitude'] = latest.country.map(lambda c: COORDS[c][1])
latest['group'] = np.where(latest.country == 'Malaysia', 'Malaysia', 'Other ASEAN countries')
latest = latest[['country','year','depression','anxiety','longitude','latitude','group']].copy()
latest['depression'] = latest['depression'].round(2)
latest['anxiety'] = latest['anxiety'].round(2)
latest = latest.sort_values('depression', ascending=False)
save_csv(latest, 'asean_latest.csv')
mal_latest = asean_prev[(asean_prev.country == 'Malaysia') & (asean_prev.year == 2017)].iloc[0]
profile = pd.DataFrame([
    ['Anxiety', float(mal_latest.anxiety)], ['Depression', float(mal_latest.depression)], ['Drug use disorders', float(mal_latest.drug_use)],
    ['Alcohol use disorders', float(mal_latest.alcohol_use)], ['Bipolar disorder', float(mal_latest.bipolar)], ['Eating disorders', float(mal_latest.eating)], ['Schizophrenia', float(mal_latest.schizophrenia)]
], columns=['condition','prevalence'])
profile['prevalence'] = profile['prevalence'].round(2)
save_csv(profile, 'malaysia_disorder_profile.csv')

# Adolescent data
ghsh = pd.read_csv(find_file('ghsh_adolescent.csv', 'GHSH_Pooled_Data1.csv'))
ghsh.columns = [clean_col(c) for c in ghsh.columns]
ghsh = ghsh.rename(columns={'overwieght':'overweight','missed_classes_without_permssion':'missed_classes_without_permission'})
ghsh['country'] = ghsh['country'].replace(FIX_COUNTRY)
malg = ghsh[ghsh.country == 'Malaysia'].copy()
for c in malg.columns:
    if c not in ['country','age_group','sex']:
        malg[c] = pd.to_numeric(malg[c], errors='coerce')
warn = {'Seriously injured':'got_seriously_injured','Had fights':'had_fights','Bullied':'bullied','Currently drink alcohol':'currently_drink_alcohol','Smoking currently':'smoke_cig_currently','Attempted suicide':'attempted_suicide','No close friends':'no_close_friends','Understanding parents':'have_understanding_parents'}
wr=[]
for label, col in warn.items():
    if col in malg.columns:
        wr.append([label, round(float(malg[col].mean(skipna=True)),1), 'Protective support' if label == 'Understanding parents' else 'Warning sign'])
adolescent_profile = pd.DataFrame(wr, columns=['indicator','percentage','type'])
save_csv(adolescent_profile, 'adolescent_profile.csv')
long=[]
for _, r in malg.iterrows():
    for label, col in warn.items():
        if col in malg.columns and pd.notna(r[col]):
            long.append([r.country, int(r.year), r.age_group, r.sex, label, round(float(r[col]),1)])
adlong = pd.DataFrame(long, columns=['country','year','age_group','sex','indicator','percentage'])
save_csv(adlong, 'adolescent_long.csv')
save_csv(adlong[adlong.indicator == 'Attempted suicide'], 'attempted_suicide_age_sex.csv')

pressure = pd.DataFrame([
    ['General population estimate','Malaysia anxiety estimate', float(mal_latest.anxiety), '2017 modelled estimate'],
    ['General population estimate','Malaysia depression estimate', float(mal_latest.depression), '2017 modelled estimate'],
    ['Adolescent warning signs','Seriously injured', float(adolescent_profile.loc[adolescent_profile.indicator=='Seriously injured','percentage'].iloc[0]), 'Adolescent indicator'],
    ['Adolescent warning signs','Had fights', float(adolescent_profile.loc[adolescent_profile.indicator=='Had fights','percentage'].iloc[0]), 'Adolescent indicator'],
    ['Adolescent warning signs','Attempted suicide', float(adolescent_profile.loc[adolescent_profile.indicator=='Attempted suicide','percentage'].iloc[0]), 'Sensitive warning sign'],
    ['University survey case study','Any reported symptom', pct(student.any_symptom.sum(), N), 'Student survey case study'],
    ['University survey case study','Multiple symptoms', pct(student.multiple_symptoms.sum(), N), 'Student survey case study'],
    ['Support gap','Sought specialist treatment', pct(student.specialist_treatment_flag.sum(), N), 'Student survey case study']
], columns=['layer','indicator','percentage','interpretation'])
pressure['percentage'] = pressure['percentage'].round(1)
save_csv(pressure, 'pressure_profile.csv')

# ===================== VEGA-LITE SPECS =====================
vl = 'https://vega.github.io/schema/vega-lite/v5.json'

def simple_layered_bar(data, yfield, xfield, title_x, width, height, color_field=None, domain=None, rng=None, sort='-x'):
    enc_color = {'value':'#7c6bb0'} if not color_field else {'field':color_field,'type':'nominal','legend':None,'scale':{'domain':domain,'range':rng}}
    return {'$schema':vl,'data':{'url':data},'width':width,'height':height,'layer':[
        {'mark':{'type':'bar','cornerRadiusEnd':7},'encoding':{'y':{'field':yfield,'type':'nominal','sort':sort,'title':None},'x':{'field':xfield,'type':'quantitative','title':title_x},'color':enc_color,'tooltip':[{'field':yfield,'type':'nominal'},{'field':xfield,'type':'quantitative','format':'.1f'}]}},
        {'mark':{'type':'text','align':'left','dx':7,'fontWeight':800,'color':'#132238'},'encoding':{'y':{'field':yfield,'type':'nominal','sort':sort},'x':{'field':xfield,'type':'quantitative'},'text':{'field':xfield,'type':'quantitative','format':'.1f'}}}
    ]}

save_spec('01_student_summary.json', simple_layered_bar('data/processed/student_summary.csv','metric','percentage','Student respondents (%)',900,300,'type',['Symptoms','Overlap','Support'],['#7c6bb0','#4f8fc0','#65a891']))
save_spec('02_symptom_rates.json', simple_layered_bar('data/processed/symptom_rates.csv','symptom','percentage','Student respondents (%)',520,250,'symptom',['Depression','Anxiety','Panic attacks'],['#7c6bb0','#4f8fc0','#e08e79']))
save_spec('03_overlap_strip.json', {'$schema':vl,'data':{'url':'data/processed/symptom_overlap.csv'},'width':520,'height':170,'mark':{'type':'bar','cornerRadius':9},'encoding':{'y':{'value':75},'x':{'aggregate':'sum','field':'percentage','type':'quantitative','title':'Share of student respondents (%)','scale':{'domain':[0,100]}},'color':{'field':'label','type':'nominal','title':'Reported symptoms','sort':['No reported symptoms','One symptom','Two symptoms','All three symptoms'],'scale':{'domain':['No reported symptoms','One symptom','Two symptoms','All three symptoms'],'range':['#d9e4ef','#7fb3c8','#7c6bb0','#e08e79']}},'order':{'field':'symptom_count','type':'quantitative'},'tooltip':[{'field':'label','type':'nominal'},{'field':'percentage','type':'quantitative','format':'.1f'},{'field':'count','type':'quantitative'}]}})
save_spec('04_treatment_gap.json', {'$schema':vl,'data':{'url':'data/processed/treatment_gap.csv'},'width':900,'height':260,'layer':[{'mark':{'type':'rule','strokeWidth':5,'opacity':0.28},'encoding':{'y':{'field':'category','type':'nominal','sort':['Reported at least one symptom','Symptomatic but no specialist treatment','Sought specialist treatment'],'title':None},'x':{'value':0},'x2':{'field':'percentage'},'color':{'field':'type','type':'nominal','legend':None,'scale':{'domain':['Symptom','Gap','Support'],'range':['#4f8fc0','#e08e79','#65a891']}}}},{'mark':{'type':'circle','size':240},'encoding':{'y':{'field':'category','type':'nominal','sort':['Reported at least one symptom','Symptomatic but no specialist treatment','Sought specialist treatment']},'x':{'field':'percentage','type':'quantitative','title':'Student respondents (%)','scale':{'domain':[0,70]}},'color':{'field':'type','type':'nominal','legend':None,'scale':{'domain':['Symptom','Gap','Support'],'range':['#4f8fc0','#e08e79','#65a891']}},'tooltip':[{'field':'category','type':'nominal'},{'field':'percentage','type':'quantitative','format':'.1f'},{'field':'count','type':'quantitative'}]}},{'mark':{'type':'text','align':'left','dx':10,'fontWeight':800},'encoding':{'y':{'field':'category','type':'nominal','sort':['Reported at least one symptom','Symptomatic but no specialist treatment','Sought specialist treatment']},'x':{'field':'percentage','type':'quantitative'},'text':{'field':'percentage','type':'quantitative','format':'.1f'}}}]})
for name, file, scheme, dom in [('05_gender_heatmap.json','gender_symptoms.csv','blues',[0,65]),('06_year_heatmap.json','year_symptoms.csv','purples',[0,80])]:
    yfield = 'gender' if 'gender' in file else 'year_of_study'
    yenc = {'field':yfield,'type':'nominal','title':None}
    if yfield == 'year_of_study': yenc['sort'] = ['Year 1','Year 2','Year 3','Year 4']
    save_spec(name, {'$schema':vl,'data':{'url':'data/processed/'+file},'width':520,'height':250,'layer':[{'mark':{'type':'rect','cornerRadius':6},'encoding':{'x':{'field':'symptom','type':'nominal','title':None},'y':yenc,'color':{'field':'percentage','type':'quantitative','title':'%','scale':{'scheme':scheme,'domain':dom}},'tooltip':[{'field':yfield,'type':'nominal'},{'field':'symptom','type':'nominal'},{'field':'percentage','type':'quantitative','format':'.1f'}]}},{'mark':{'type':'text','fontWeight':800},'encoding':{'x':{'field':'symptom','type':'nominal'},'y':yenc,'text':{'field':'percentage','type':'quantitative','format':'.1f'},'color':{'condition':{'test':'datum.percentage > 45','value':'white'},'value':'#132238'}}}]})
save_spec('07_cgpa_lollipop.json', {'$schema':vl,'data':{'url':'data/processed/cgpa_symptoms.csv'},'width':900,'height':260,'layer':[{'mark':{'type':'rule','strokeWidth':5,'opacity':0.25,'color':'#7c6bb0'},'encoding':{'y':{'field':'cgpa','type':'ordinal','sort':cgpa_order,'title':'CGPA range'},'x':{'value':0},'x2':{'field':'percentage'}}},{'mark':{'type':'circle','size':230,'color':'#7c6bb0'},'encoding':{'y':{'field':'cgpa','type':'ordinal','sort':cgpa_order},'x':{'field':'percentage','type':'quantitative','title':'Students with at least one symptom (%)','scale':{'domain':[0,100]}},'tooltip':[{'field':'cgpa','type':'nominal'},{'field':'percentage','type':'quantitative','format':'.1f'},{'field':'count','type':'quantitative'}]}},{'mark':{'type':'text','align':'left','dx':10,'fontWeight':800},'encoding':{'y':{'field':'cgpa','type':'ordinal','sort':cgpa_order},'x':{'field':'percentage','type':'quantitative'},'text':{'field':'percentage','type':'quantitative','format':'.1f'}}}]})
save_spec('08_malaysia_trend.json', {'$schema':vl,'data':{'url':'data/processed/malaysia_trend.csv'},'width':900,'height':340,'mark':{'type':'line','point':True,'strokeWidth':3},'encoding':{'x':{'field':'year','type':'ordinal','title':'Year','axis':{'labelAngle':0,'values':[1990,1995,2000,2005,2010,2015,2017]}},'y':{'field':'prevalence','type':'quantitative','title':'Estimated prevalence (%)','scale':{'zero':False}},'color':{'field':'condition','type':'nominal','title':'Condition','scale':{'domain':['Depression','Anxiety'],'range':['#7c6bb0','#4f8fc0']}},'tooltip':[{'field':'year','type':'ordinal'},{'field':'condition','type':'nominal'},{'field':'prevalence','type':'quantitative','format':'.2f'}]}})
save_spec('09_asean_ranking.json', simple_layered_bar('data/processed/asean_latest.csv','country','depression','Estimated depression prevalence (%)',520,330,'group',['Malaysia','Other ASEAN countries'],['#e08e79','#7c6bb0']))
save_spec('10_asean_map.json', {'$schema':vl,'data':{'url':'data/processed/asean_latest.csv'},'width':900,'height':430,'projection':{'type':'equirectangular','center':[108,8],'scale':700},'layer':[{'data':{'sphere':True},'mark':{'type':'geoshape','fill':'#f3f8fc','stroke':'#d9e4ef','strokeWidth':1}},{'data':{'graticule':True},'mark':{'type':'geoshape','stroke':'#d9e4ef','strokeWidth':0.6,'opacity':0.7}},{'mark':{'type':'circle','opacity':0.88,'stroke':'white','strokeWidth':2},'encoding':{'longitude':{'field':'longitude','type':'quantitative'},'latitude':{'field':'latitude','type':'quantitative'},'size':{'field':'depression','type':'quantitative','title':'Depression (%)','scale':{'range':[300,1800]}},'color':{'field':'group','type':'nominal','title':None,'scale':{'domain':['Malaysia','Other ASEAN countries'],'range':['#e08e79','#7c6bb0']}},'tooltip':[{'field':'country','type':'nominal'},{'field':'depression','type':'quantitative','format':'.2f'},{'field':'anxiety','type':'quantitative','format':'.2f'}]}},{'mark':{'type':'text','dy':18,'fontSize':11,'fontWeight':700,'color':'#52616b'},'encoding':{'longitude':{'field':'longitude','type':'quantitative'},'latitude':{'field':'latitude','type':'quantitative'},'text':{'field':'country','type':'nominal'}}},{'transform':[{'filter':'datum.country == "Malaysia"'}],'mark':{'type':'circle','fillOpacity':0,'stroke':'#e08e79','strokeWidth':4,'size':2400},'encoding':{'longitude':{'field':'longitude','type':'quantitative'},'latitude':{'field':'latitude','type':'quantitative'}}}]})
save_spec('11_disorder_profile.json', simple_layered_bar('data/processed/malaysia_disorder_profile.csv','condition','prevalence','Estimated prevalence (%)',900,330,'condition',None,['#4f8fc0','#7c6bb0','#e08e79','#65a891','#b7c4d0','#e5b567','#a98fc3']))
save_spec('12_adolescent_profile.json', simple_layered_bar('data/processed/adolescent_profile.csv','indicator','percentage','Average reported share (%)',520,330,'type',['Warning sign','Protective support'],['#e08e79','#65a891']))
save_spec('13_attempted_suicide.json', {'$schema':vl,'data':{'url':'data/processed/attempted_suicide_age_sex.csv'},'width':520,'height':310,'mark':{'type':'bar','cornerRadiusTopLeft':6,'cornerRadiusTopRight':6},'encoding':{'x':{'field':'age_group','type':'nominal','title':'Age group'},'xOffset':{'field':'sex'},'y':{'field':'percentage','type':'quantitative','title':'Reported attempted-suicide indicator (%)','scale':{'domain':[0,10]}},'color':{'field':'sex','type':'nominal','scale':{'range':['#4f8fc0','#e08e79']}},'tooltip':[{'field':'age_group','type':'nominal'},{'field':'sex','type':'nominal'},{'field':'percentage','type':'quantitative','format':'.1f'}]}})
save_spec('14_pressure_profile.json', {'$schema':vl,'data':{'url':'data/processed/pressure_profile.csv'},'width':900,'height':380,'layer':[{'mark':{'type':'rule','strokeWidth':5,'opacity':0.25},'encoding':{'y':{'field':'indicator','type':'nominal','sort':'-x','title':None,'axis':{'labelLimit':260}},'x':{'value':0},'x2':{'field':'percentage'}}},{'mark':{'type':'circle','size':220},'encoding':{'y':{'field':'indicator','type':'nominal','sort':'-x'},'x':{'field':'percentage','type':'quantitative','title':'Indicator value (%)','scale':{'domain':[0,100]}},'color':{'field':'layer','type':'nominal','title':'Evidence layer','scale':{'range':['#4f8fc0','#e08e79','#7c6bb0','#65a891']}},'tooltip':[{'field':'layer','type':'nominal'},{'field':'indicator','type':'nominal'},{'field':'percentage','type':'quantitative','format':'.1f'},{'field':'interpretation','type':'nominal'}]}},{'mark':{'type':'text','align':'left','dx':9,'fontWeight':800},'encoding':{'y':{'field':'indicator','type':'nominal','sort':'-x'},'x':{'field':'percentage','type':'quantitative'},'text':{'field':'percentage','type':'quantitative','format':'.1f'}}}]})

# ===================== WEB FILES =====================
(JS / 'main.js').write_text("""const charts = [
  ['#vis-trend', 'specs/08_malaysia_trend.json'],
  ['#vis-ranking', 'specs/09_asean_ranking.json'],
  ['#vis-map', 'specs/10_asean_map.json'],
  ['#vis-profile', 'specs/11_disorder_profile.json'],
  ['#vis-adolescent', 'specs/12_adolescent_profile.json'],
  ['#vis-suicide', 'specs/13_attempted_suicide.json'],
  ['#vis-summary', 'specs/01_student_summary.json'],
  ['#vis-symptoms', 'specs/02_symptom_rates.json'],
  ['#vis-overlap', 'specs/03_overlap_strip.json'],
  ['#vis-gap', 'specs/04_treatment_gap.json'],
  ['#vis-gender', 'specs/05_gender_heatmap.json'],
  ['#vis-year', 'specs/06_year_heatmap.json'],
  ['#vis-cgpa', 'specs/07_cgpa_lollipop.json'],
  ['#vis-pressure', 'specs/14_pressure_profile.json']
];
async function embedChart(selector, specUrl) {
  const el = document.querySelector(selector);
  if (!el) return;
  el.innerHTML = '';
  try {
    await vegaEmbed(selector, `${specUrl}?v=${Date.now()}`, {actions:false, renderer:'svg'});
  } catch (err) {
    console.error(err);
    el.innerHTML = `<p class="chart-error">Chart failed to load: ${specUrl}</p>`;
  }
}
charts.forEach(([selector, specUrl]) => embedChart(selector, specUrl));
""", encoding='utf-8')

(CSS / 'style.css').write_text("""*{box-sizing:border-box}:root{--bg:#f4f8fb;--card:#fff;--ink:#112036;--muted:#586879;--line:#dce7f1;--blue:#4f8fc0;--purple:#7c6bb0;--coral:#e08e79;--teal:#65a891;--shadow:0 16px 38px rgba(17,32,54,.08)}html{scroll-behavior:smooth}body{margin:0;font-family:Inter,Arial,sans-serif;color:var(--ink);background:radial-gradient(circle at top left,rgba(79,143,192,.15),transparent 34rem),linear-gradient(180deg,#f7fbff 0%,var(--bg) 100%);line-height:1.65}.page{max-width:1180px;margin:0 auto;padding:34px 22px 72px}.hero{padding:52px;border-radius:32px;background:linear-gradient(135deg,#fff 0%,#eef7fc 100%);border:1px solid #e3edf5;box-shadow:var(--shadow)}.kicker,.section-number{margin:0 0 10px;text-transform:uppercase;letter-spacing:.14em;color:var(--blue);font-weight:800;font-size:.78rem}h1{margin:0 0 18px;font-size:clamp(2.8rem,6.5vw,5.4rem);line-height:.98;letter-spacing:-.07em;max-width:970px}.subtitle{max-width:860px;font-size:clamp(1.08rem,2vw,1.38rem);color:var(--muted);margin:0 0 30px}.hero-grid,.takeaway-grid,.method-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.hero-grid div,.takeaway-grid div,.method-grid div{background:rgba(255,255,255,.78);border:1px solid var(--line);border-radius:18px;padding:18px}.hero-grid strong,.takeaway-grid strong{display:block;color:var(--ink);font-size:.92rem;margin-bottom:4px}.hero-grid span,.takeaway-grid span{color:var(--muted);font-size:.95rem}.intro-card,.chart-card,.takeaways,.methodology{background:var(--card);border:1px solid #e7edf4;border-radius:26px;box-shadow:var(--shadow)}.intro-card,.takeaways,.methodology{padding:30px;margin:28px 0}.section{margin:62px 0}.section-heading{border-top:2px solid var(--line);padding-top:30px;margin-bottom:22px}.section-number{color:var(--purple)}h2{font-size:clamp(1.9rem,3.2vw,2.8rem);line-height:1.05;letter-spacing:-.055em;margin:0 0 10px}h3{margin:0 0 18px;font-size:1.25rem;line-height:1.2;letter-spacing:-.02em}p{color:var(--muted);margin:0 0 14px}.note{border-left:4px solid var(--coral);background:#fff6f2;border-radius:0 14px 14px 0;padding:12px 16px}.chart-grid.two{display:grid;grid-template-columns:1fr 1fr;gap:24px}.chart-card{padding:26px;margin-bottom:24px;overflow:hidden}.chart{width:100%;min-height:170px}.vega-embed,.vega-embed svg,.vega-embed canvas{max-width:100%;height:auto}.insight{margin-top:18px;border-left:4px solid var(--blue);background:#f2f7fd;color:#334155;padding:14px 16px;border-radius:0 16px 16px 0;font-size:.96rem}.caption{font-size:.84rem;color:#728196;margin:12px 0 0}.takeaway-grid{grid-template-columns:repeat(4,1fr);margin-top:18px}.method-grid{grid-template-columns:repeat(2,1fr);margin-top:18px}.methodology a{display:inline-block;color:#3b76a8;font-weight:700;text-decoration:none;border-bottom:2px solid rgba(79,143,192,.25);margin-top:6px}.methodology a:hover{border-bottom-color:var(--blue)}.footer{border-top:1px solid var(--line);padding-top:24px;margin-top:58px;font-size:.9rem}.chart-error{color:#b42318;background:#fff1f0;border:1px solid #ffd3d0;padding:12px;border-radius:12px}@media(max-width:980px){.hero-grid,.chart-grid.two,.takeaway-grid,.method-grid{grid-template-columns:1fr}.hero{padding:34px}}@media(max-width:620px){.page{padding:18px 12px 52px}.hero,.intro-card,.chart-card,.takeaways,.methodology{border-radius:20px;padding:20px}h1{font-size:2.55rem}}""", encoding='utf-8')

index = """<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'/><meta name='viewport' content='width=device-width, initial-scale=1.0'/><title>Malaysia’s Mental Health Crisis | FIT2179 DV2</title><link rel='preconnect' href='https://fonts.googleapis.com'><link rel='preconnect' href='https://fonts.gstatic.com' crossorigin><link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap' rel='stylesheet'><link rel='stylesheet' href='css/style.css'/><script src='https://cdn.jsdelivr.net/npm/vega@5'></script><script src='https://cdn.jsdelivr.net/npm/vega-lite@5'></script><script src='https://cdn.jsdelivr.net/npm/vega-embed@6'></script></head><body><main class='page'>
<header class='hero'><p class='kicker'>FIT2179 Data Visualisation 2 · Malaysia</p><h1>Malaysia’s Mental Health Crisis</h1><p class='subtitle'>How general population estimates, adolescent warning signs, and a university survey case study show why mental-health awareness needs to start earlier.</p><div class='hero-grid'><div><strong>Domain</strong><span>Mental-health awareness and public-health warning signs in Malaysia.</span></div><div><strong>Audience</strong><span>Average Malaysians, especially students, families, young adults and educators.</span></div><div><strong>Evidence layers</strong><span>ASEAN estimates, adolescent indicators, and a focused student survey case study.</span></div></div></header>
<section class='intro-card'><h2>Why this matters</h2><p>Mental health is not visible through one number. It can appear through estimated population-level prevalence, warning signs during adolescence, and reported symptoms among students. This visualisation combines these evidence layers to explain why awareness and support should begin before distress becomes severe.</p><p class='note'><strong>Important:</strong> The student survey is used as a focused case study, not as a national estimate. The charts show patterns and warning signs, not clinical diagnosis or proof of causation.</p></section>
<section class='section'><div class='section-heading'><p class='section-number'>Section 1</p><h2>Malaysia in wider mental-health context</h2><p>Global prevalence estimates help position Malaysia beside neighbouring ASEAN countries. This gives the story a broader public-health context instead of treating mental health as only a student issue.</p></div><div class='chart-card'><h3>Malaysia’s estimated depression and anxiety trend</h3><div id='vis-trend' class='chart'></div><div class='insight'><strong>Insight:</strong> Anxiety remains consistently above depression in these estimates, while both remain visible across the period. This supports treating mental health as an ongoing public-health concern rather than a short-term issue.</div><p class='caption'>Source: Mental Health Depression Disorder dataset. Values are estimated prevalence percentages, not raw survey counts.</p></div><div class='chart-grid two'><div class='chart-card'><h3>Latest ASEAN depression ranking</h3><div id='vis-ranking' class='chart'></div><div class='insight'><strong>Insight:</strong> Ranking gives a direct comparison of Malaysia against neighbouring countries without forcing readers to trace many lines.</div></div><div class='chart-card'><h3>Malaysia’s mental-disorder profile</h3><div id='vis-profile' class='chart'></div><div class='insight'><strong>Insight:</strong> Different conditions appear at different levels, which is why a single mental-health number is not enough.</div></div></div><div class='chart-card'><h3>ASEAN geographic view</h3><div id='vis-map' class='chart'></div><div class='insight'><strong>Insight:</strong> The map places Malaysia geographically within ASEAN and helps readers see that the issue is regional rather than isolated.</div><p class='caption'>Geographic point map built in Vega-Lite. Circle size encodes estimated depression prevalence.</p></div></section>
<section class='section'><div class='section-heading'><p class='section-number'>Section 2</p><h2>Warning signs can appear before adulthood</h2><p>Adolescent indicators show why mental-health awareness and support should begin before students enter university.</p></div><div class='chart-grid two'><div class='chart-card'><h3>Malaysia adolescent warning-sign profile</h3><div id='vis-adolescent' class='chart'></div><div class='insight'><strong>Insight:</strong> Bullying, fighting, serious injury and social isolation sit beside self-harm indicators, showing that wellbeing is social as well as individual.</div><p class='caption'>Source: GHSH pooled adolescent dataset. Values are averages across available Malaysia sex and age groups.</p></div><div class='chart-card'><h3>Attempted-suicide indicator by age and sex</h3><div id='vis-suicide' class='chart'></div><div class='insight'><strong>Insight:</strong> Splitting by age and sex gives more detail while still requiring careful and sensitive interpretation.</div><p class='caption'>Sensitive indicator shown as a warning sign, not as an explanation of causes.</p></div></div></section>
<section class='section'><div class='section-heading'><p class='section-number'>Section 3</p><h2>A university survey case study</h2><p>The university survey provides a focused student-level snapshot. It is not nationally representative, but it shows how symptoms and help-seeking can appear in a student setting.</p></div><div class='chart-card'><h3>Student survey snapshot</h3><div id='vis-summary' class='chart'></div><div class='insight'><strong>Insight:</strong> Reported symptoms appear much more visible than specialist treatment-seeking in this survey.</div><p class='caption'>Source: Student Mental Health dataset, Kaggle/IIUM student survey. Percentages are based on 101 respondents.</p></div><div class='chart-grid two'><div class='chart-card'><h3>Which symptoms were reported most?</h3><div id='vis-symptoms' class='chart'></div><div class='insight'><strong>Insight:</strong> Depression, anxiety and panic attacks appear at similar levels, so the case study is not limited to one symptom type.</div></div><div class='chart-card'><h3>Symptoms overlap</h3><div id='vis-overlap' class='chart'></div><div class='insight'><strong>Insight:</strong> A stacked distribution shows that many respondents reported at least one symptom, and some reported multiple symptoms together.</div></div></div><div class='chart-card'><h3>The support gap</h3><div id='vis-gap' class='chart'></div><div class='insight'><strong>Insight:</strong> The gap between reported symptoms and specialist treatment is one of the clearest reasons for awareness-building.</div><p class='caption'>This does not judge students; it highlights a possible access, awareness, affordability or stigma gap.</p></div><div class='chart-grid two'><div class='chart-card'><h3>Symptoms by gender</h3><div id='vis-gender' class='chart'></div><div class='insight'><strong>Insight:</strong> The heatmap supports comparison, but the small sample means this should not be overgeneralised.</div></div><div class='chart-card'><h3>Symptoms by year of study</h3><div id='vis-year' class='chart'></div><div class='insight'><strong>Insight:</strong> Year-of-study comparison suggests that support planning should consider different stages of university life.</div></div></div><div class='chart-card'><h3>Reported symptoms across CGPA ranges</h3><div id='vis-cgpa' class='chart'></div><div class='insight'><strong>Insight:</strong> This chart shows association only. It should not be interpreted as evidence that CGPA causes mental-health symptoms.</div></div></section>
<section class='section'><div class='section-heading'><p class='section-number'>Section 4</p><h2>Connecting the evidence</h2><p>The final chart connects general, adolescent and student indicators without pretending they measure the same population.</p></div><div class='chart-card'><h3>Custom pressure profile: connecting the evidence</h3><div id='vis-pressure' class='chart'></div><div class='insight'><strong>Insight:</strong> This custom profile is a communication summary, not a medical index. It helps readers see how multiple evidence layers point toward the same awareness need.</div></div></section>
<section class='takeaways'><h2>What the data suggests</h2><div class='takeaway-grid'><div><strong>Context matters.</strong><span>Malaysia’s pattern is clearer when compared with nearby countries.</span></div><div><strong>Warning signs start early.</strong><span>Adolescent indicators suggest support should begin before university.</span></div><div><strong>Symptoms can overlap.</strong><span>The student case study shows that symptoms can appear together.</span></div><div><strong>Help-seeking is lower.</strong><span>The survey highlights a gap between symptoms and specialist treatment.</span></div></div></section>
<section class='methodology'><h2>Data sources, authorship & limitations</h2><div class='method-grid'><div><h3>Global mental-health estimates</h3><p>Used for Malaysia and ASEAN comparisons of depression, anxiety and related indicators.</p><a href='https://www.kaggle.com/datasets/muhammadfaizan65/mental-health-depression-disorder-data' target='_blank' rel='noopener'>Kaggle: Mental Health Depression Disorder Data</a></div><div><h3>Adolescent warning signs</h3><p>Used for youth indicators such as attempted suicide, bullying, social isolation and parental understanding.</p><a href='https://www.kaggle.com/datasets/kashishnaqvi/suicidal-behaviours-among-adolescents' target='_blank' rel='noopener'>Kaggle: Suicidal Behaviours Among Adolescents / GHSH</a></div><div><h3>University survey case study</h3><p>Used for reported depression, anxiety, panic attacks, CGPA, year of study and treatment-seeking.</p><a href='https://www.kaggle.com/datasets/shariful07/student-mental-health/data' target='_blank' rel='noopener'>Kaggle: Student Mental Health Dataset</a></div><div><h3>Limitations</h3><p>The student survey is small and not nationally representative. Global values may be modelled estimates. The charts show patterns and warning signs, not clinical diagnosis or causation.</p></div></div></section>
<footer class='footer'><p><strong>Author:</strong> Abdullah Rehan · <strong>Student ID:</strong> 34445390 · <strong>Unit:</strong> FIT2179 Data Visualisation 2 · <strong>Date:</strong> 31 May 2026</p><p><strong>AI acknowledgement:</strong> Generative AI tools were used to assist with planning, wording, code debugging and layout refinement. All data selection, interpretation, visualisation decisions and final submission were reviewed and edited by the author.</p></footer>
</main><script src='js/main.js'></script></body></html>"""
(BASE/'index.html').write_text(index, encoding='utf-8')

(BASE/'moodle_description.txt').write_text("""Domain: This visualisation focuses on Malaysia’s mental health crisis as a public-health awareness issue. It combines global mental-health estimates, adolescent warning-sign indicators, and a Malaysian university student survey case study to show why awareness and support should begin earlier.

Why and who: The visualisation is designed for average Malaysian readers, especially students, young adults, families and educators. Mental health can be difficult to notice because it appears through many warning signs, including anxiety, depression, panic attacks, bullying, isolation and low treatment-seeking.

What: The project uses three main evidence layers. The global mental-health dataset supports Malaysia and ASEAN comparisons for depression and anxiety estimates. The GHSH/adolescent dataset provides youth warning-sign indicators where Malaysia data is available. The student mental-health dataset provides a focused university case study on reported symptoms, symptom overlap, CGPA groups, year of study and specialist treatment-seeking.

How: The design follows Munzer’s What/Why/How framework by matching each visualisation idiom to a communication task. Line charts show trends over time, ranking bars compare countries, a geographic map places Malaysia in regional context, heatmaps compare student groups, a lollipop chart highlights the treatment gap, and a custom pressure profile connects the evidence layers. Tooltips provide simple interactivity without turning the story into a complex dashboard.

Limitations: The university survey is small and should not be treated as a national estimate of all Malaysian students. Global prevalence values may be modelled estimates rather than direct survey counts. The visualisation shows patterns and warning signs, not clinical diagnosis or proof of causation. Generative AI tools were used to assist with planning, wording, code debugging and layout refinement. All data selection, interpretation, visualisation decisions and final submission were reviewed and edited by the author.
""", encoding='utf-8')

(BASE/'README.md').write_text("""# Malaysia’s Mental Health Crisis

FIT2179 Data Visualisation 2 final project by Abdullah Rehan (34445390).

Run locally:

```bash
py -m http.server 8000
```

Then open `http://localhost:8000`.
""", encoding='utf-8')

print('\nFINAL BUILD COMPLETE')
print('Run: py -m http.server 8000')
print('Open: http://localhost:8000/?v=final')
