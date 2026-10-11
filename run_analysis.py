"""Runnable demonstration for Case Study 4. All generated results are illustrative."""
def display(value):
    print(value.to_string() if hasattr(value, "to_string") else value)

from pathlib import Path
import numpy as np
import pandas as pd

DATA_PATH = Path('Case_Study_4_Environmental_Sustainability.csv')
RNG = np.random.default_rng(27)

if DATA_PATH.exists():
    raw = pd.read_csv(DATA_PATH)
    SOURCE = 'supplied CSV'
else:
    n = 2000
    raw = pd.DataFrame({
        'record_id': np.arange(1,n+1),
        'site': RNG.choice(['Paris HQ','Paris HQ  ','Bengaluru Plant','Austin Office'], n),
        'year': 2026,
        'grid_kwh': RNG.uniform(500,9000,n).round(1),
        'renewable_kwh_claimed': RNG.uniform(0,400,n).round(1),
        'renewable_evidence_verified': RNG.choice([True,False],n,p=[.65,.35]),
        'water_m3': RNG.uniform(4,120,n).round(2),
        'waste_kg': RNG.uniform(30,800,n).round(1),
        'recycling_pct': RNG.uniform(10,85,n).round(1),
        'scope1_reported_tco2e': RNG.uniform(0,8,n).round(3),
        'audit_status': RNG.choice(['PENDING','Pending Audit','Complete'],n)
    })
    raw.loc[[10,55],'recycling_pct'] = 105
    raw.loc[[17,71],'scope1_reported_tco2e'] = -3
    raw.loc[90,'renewable_kwh_claimed'] = 10000
    SOURCE = 'synthetic demonstration only'
print(SOURCE, raw.shape)
raw.head()


ALIASES = {
 'record_id':['record_id','id'], 'site':['site','site_location','facility'],
 'year':['year','reporting_year'], 'grid_kwh':['grid_kwh','electricity_kwh','energy_kwh'],
 'renewable_kwh_claimed':['renewable_kwh_claimed','renewable_offset_kwh','renewable_kwh'],
 'renewable_evidence_verified':['renewable_evidence_verified','renewable_verified'],
 'water_m3':['water_m3','water_consumption_m3'], 'waste_kg':['waste_kg','waste_generated_kg'],
 'recycling_pct':['recycling_pct','waste_recycling_pct'],
 'scope1_reported_tco2e':['scope1_reported_tco2e','scope_1_emissions_mtco2e','scope1_mtco2e'],
 'audit_status':['audit_status','iso_audit_status']}
rename = {}
for canonical, options in ALIASES.items():
    found = next((x for x in options if x in raw.columns), None)
    if found: rename[found] = canonical
df = raw.rename(columns=rename).copy()
required = ['record_id','site','year','grid_kwh','water_m3','waste_kg','recycling_pct','scope1_reported_tco2e','audit_status']
missing = [x for x in required if x not in df]
if missing: raise ValueError(f'Missing required fields: {missing}. Update ALIASES using CSV headers.')
for optional, default in [('renewable_kwh_claimed',0),('renewable_evidence_verified',False)]:
    if optional not in df: df[optional] = default
df['site_clean'] = df.site.astype('string').str.strip().str.replace(r'\s+',' ',regex=True).str.title()
df['audit_status_clean'] = df.audit_status.astype('string').str.strip().str.lower().map(
    {'pending':'Pending audit','pending audit':'Pending audit','complete':'Complete','completed':'Complete'}).fillna('Review')
num = ['grid_kwh','renewable_kwh_claimed','water_m3','waste_kg','recycling_pct','scope1_reported_tco2e']
for col in num: df[col] = pd.to_numeric(df[col],errors='coerce')
df['duplicate_id'] = df.duplicated('record_id',keep=False)
df['invalid_activity'] = df[['grid_kwh','water_m3','waste_kg']].isna().any(axis=1) | (df[['grid_kwh','water_m3','waste_kg']]<0).any(axis=1)
df['invalid_recycling'] = ~df.recycling_pct.between(0,100)
df['invalid_scope1'] = df.scope1_reported_tco2e.isna() | (df.scope1_reported_tco2e<0)
df['claim_gt_grid'] = df.renewable_kwh_claimed.gt(df.grid_kwh)
df['quarantine'] = df[['duplicate_id','invalid_activity','invalid_recycling','invalid_scope1','claim_gt_grid']].any(axis=1)
qa = df[['duplicate_id','invalid_activity','invalid_recycling','invalid_scope1','claim_gt_grid','quarantine']].sum().rename('records')
display(qa.to_frame())
clean = df.loc[~df.quarantine].copy()


factors = pd.DataFrame([
 ['Paris Hq',2026,.05,.08,0,.30,.25,'ILLUSTRATIVE - replace'],
 ['Bengaluru Plant',2026,.70,.75,0,.30,.25,'ILLUSTRATIVE - replace'],
 ['Austin Office',2026,.40,.45,0,.30,.25,'ILLUSTRATIVE - replace'],
],columns=['site_clean','year','grid_kg_per_kwh','residual_kg_per_kwh','contract_kg_per_kwh','water_kg_per_m3','waste_kg_per_kg','factor_source'])
clean = clean.merge(factors,on=['site_clean','year'],how='left',validate='many_to_one')
factor_cols = ['grid_kg_per_kwh','residual_kg_per_kwh','contract_kg_per_kwh','water_kg_per_m3','waste_kg_per_kg']
if clean[factor_cols].isna().any().any():
    raise ValueError('Missing site/year factor. Add verified factors before calculation.')
verified = clean.renewable_evidence_verified.astype('string').str.lower().isin(['true','1','yes'])
eligible_kwh = clean.renewable_kwh_claimed.where(verified,0)
clean['scope1_t'] = clean.scope1_reported_tco2e
clean['scope2_location_t'] = clean.grid_kwh * clean.grid_kg_per_kwh / 1000
clean['scope2_market_t'] = (eligible_kwh*clean.contract_kg_per_kwh + (clean.grid_kwh-eligible_kwh)*clean.residual_kg_per_kwh)/1000
clean['scope3_water_cat1_t'] = clean.water_m3 * clean.water_kg_per_m3 / 1000
clean['scope3_waste_cat5_t'] = clean.waste_kg * clean.waste_kg_per_kg / 1000
clean['scope3_partial_t'] = clean.scope3_water_cat1_t + clean.scope3_waste_cat5_t
clean['total_location_partial_t'] = clean.scope1_t + clean.scope2_location_t + clean.scope3_partial_t
clean['total_market_partial_t'] = clean.scope1_t + clean.scope2_market_t + clean.scope3_partial_t
assert clean.scope2_location_t.ge(0).all() and clean.scope2_market_t.ge(0).all()
assert not clean.record_id.duplicated().any()
summary = clean.groupby('site_clean',dropna=False).agg(records=('record_id','size'),grid_kwh=('grid_kwh','sum'),water_m3=('water_m3','sum'),waste_kg=('waste_kg','sum'),scope1_t=('scope1_t','sum'),scope2_location_t=('scope2_location_t','sum'),scope2_market_t=('scope2_market_t','sum'),scope3_partial_t=('scope3_partial_t','sum'),total_location_partial_t=('total_location_partial_t','sum')).round(2)
display(summary)


gri = pd.DataFrame([
 ['Climate','GRI 305-1 / future GRI 102','Scope 1 gross emissions, gases, boundary, factors','Partial','Fuel-level evidence missing'],
 ['Climate','GRI 305-2 / future GRI 102','Scope 2 location and market totals, certificate quality','Partial','Verify instruments and residual factors'],
 ['Climate','GRI 305-3 / future GRI 102','Material Scope 3 categories and exclusions','Gap','Only water service and waste modeled'],
 ['Energy','GRI 302 / future GRI 103','Energy by source and renewable/nonrenewable split','Partial','Fuel and purchased heat missing'],
 ['Water','GRI 303-3 to 303-5','Withdrawal, discharge, consumption; water stress','Gap','Consumption alone cannot establish all'],
 ['Waste','GRI 306-3 to 306-5','Generated, diverted, disposal by method','Gap','Recycling percentage lacks method evidence'],
],columns=['topic','reference','expected_evidence','readiness','next_evidence'])
display(gri)
out = Path('case_study_outputs'); out.mkdir(exist_ok=True)
df.to_csv(out/'quality_review.csv',index=False)
clean.to_csv(out/'carbon_ledger_demo.csv',index=False)
summary.to_csv(out/'site_summary_demo.csv')
gri.to_csv(out/'gri_readiness.csv',index=False)
print('Saved demonstration outputs to',out.resolve())

