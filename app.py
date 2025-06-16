from flask import Flask,render_template,request,jsonify
from bp import *
from diesese import *
import pandas as pd
import time
import os

# Dieases
prescriptions = {
    'Influenza': {
        'medicine': ['Oseltamivir (Tamiflu)', 'Zanamivir (Relenza)', 'Acetaminophen (for fever)'],
        'recommendation': ['Rest and hydrate', 'Use a humidifier', 'Avoid close contact with others'],
        'note': 'Antivirals work best when started within 48 hours of symptom onset',
        'advise': 'Get annual flu vaccination to prevent infection'
    },
    'Common Cold': {
        'medicine': ['Acetaminophen or Ibuprofen (for pain/fever)', 'Decongestants (e.g., Pseudoephedrine)', 'Antihistamines (e.g., Diphenhydramine)'],
        'recommendation': ['Drink warm fluids', 'Get plenty of rest', 'Use saline nasal drops'],
        'note': 'Antibiotics are ineffective as it is viral',
        'advise': 'Wash hands frequently to prevent spread'
    },
    'Eczema': {
        'medicine': ['Topical corticosteroids (e.g., Hydrocortisone)', 'Antihistamines (for itching)', 'Moisturizers (e.g., Ceramide-based creams)'],
        'recommendation': ['Avoid irritants (e.g., harsh soaps)', 'Use fragrance-free products', 'Keep skin moisturized'],
        'note': 'Can flare due to stress or environmental triggers',
        'advise': 'Identify and avoid personal triggers'
    },
    'Asthma': {
        'medicine': ['Inhaled corticosteroids (e.g., Fluticasone)', 'Bronchodilators (e.g., Albuterol)', 'Leukotriene modifiers (e.g., Montelukast)'],
        'recommendation': ['Avoid triggers (e.g., smoke, pollen)', 'Use a peak flow meter', 'Follow an asthma action plan'],
        'note': 'Symptoms may worsen at night or with exercise',
        'advise': 'Carry rescue inhaler at all times'
    },
    'Hyperthyroidism': {
        'medicine': ['Methimazole', 'Propylthiouracil (PTU)', 'Beta-blockers (e.g., Propranolol for symptoms)'],
        'recommendation': ['Regular thyroid function tests', 'Avoid excess iodine', 'Monitor heart rate and blood pressure'],
        'note': 'Graves disease is most common cause',
        'advise': 'Report any fever/sore throat immediately (risk of agranulocytosis)'
    },
    'Allergic Rhinitis': {
        'medicine': ['Antihistamines (e.g., Loratadine)', 'Nasal corticosteroids (e.g., Fluticasone)', 'Decongestants (e.g., Pseudoephedrine)'],
        'recommendation': ['Avoid allergens (e.g., pollen, dust mites)', 'Use air purifiers', 'Wash bedding frequently'],
        'note': 'May be seasonal or perennial',
        'advise': 'Start medications before allergy season'
    },
    'Anxiety Disorders': {
        'medicine': ['SSRIs (e.g., Sertraline)', 'Benzodiazepines (e.g., Alprazolam for short-term use)', 'Buspirone'],
        'recommendation': ['Cognitive Behavioral Therapy (CBT)', 'Regular exercise', 'Practice mindfulness/meditation'],
        'note': 'Benzodiazepines risk dependence with long-term use',
        'advise': 'Avoid caffeine and alcohol which can worsen symptoms'
    },
    'Diabetes': {
        'medicine': ['Insulin (for Type 1)', 'Metformin (for Type 2)', 'SGLT2 inhibitors (e.g., Empagliflozin)'],
        'recommendation': ['Monitor blood sugar regularly', 'Follow a balanced diet', 'Exercise regularly'],
        'note': 'HbA1c should be checked every 3-6 months',
        'advise': 'Inspect feet daily for wounds'
    },
    'Gastroenteritis': {
        'medicine': ['Oral rehydration solutions (e.g., Pedialyte)', 'Antiemetics (e.g., Ondansetron for vomiting)', 'Probiotics'],
        'recommendation': ['Stay hydrated', 'Avoid dairy and fatty foods', 'Rest'],
        'note': 'Most cases viral (norovirus/rotavirus)',
        'advise': 'Practice good hand hygiene to prevent spread'
    },
    'Pancreatitis': {
        'medicine': ['Pain relievers (e.g., Acetaminophen)', 'IV fluids', 'Pancreatic enzyme supplements'],
        'recommendation': ['Avoid alcohol', 'Follow a low-fat diet', 'Small, frequent meals'],
        'note': 'Gallstones and alcohol are common causes',
        'advise': 'Absolute alcohol abstinence required'
    },
    'Rheumatoid Arthritis': {
        'medicine': ['DMARDs (e.g., Methotrexate)', 'NSAIDs (e.g., Ibuprofen)', 'Biologics (e.g., Adalimumab)'],
        'recommendation': ['Regular exercise (low-impact)', 'Joint protection techniques', 'Physical therapy'],
        'note': 'Morning stiffness >1 hour is characteristic',
        'advise': 'Monitor for extra-articular manifestations'
    },
    'Depression': {
        'medicine': ['SSRIs (e.g., Fluoxetine)', 'SNRIs (e.g., Venlafaxine)', 'Atypical antidepressants (e.g., Bupropion)'],
        'recommendation': ['Therapy (e.g., CBT)', 'Regular exercise', 'Maintain a support network'],
        'note': 'Medications take 4-6 weeks for full effect',
        'advise': 'Report any suicidal thoughts immediately'
    },
    'Liver Cancer': {
        'medicine': ['Chemotherapy (e.g., Sorafenib)', 'Immunotherapy', 'Pain management (e.g., Morphine)'],
        'recommendation': ['Regular follow-ups with oncologist', 'Nutritional support', 'Avoid alcohol'],
        'note': 'Often associated with cirrhosis or hepatitis',
        'advise': 'Surveillance ultrasound every 6 months if cirrhotic'
    },
    'Stroke': {
        'medicine': ['tPA (clot-busting drug)', 'Antiplatelets (e.g., Aspirin)', 'Anticoagulants (e.g., Warfarin)'],
        'recommendation': ['Rehabilitation therapy (physical/speech)', 'Control blood pressure', 'Healthy diet (low sodium)'],
        'note': 'Time is brain - tPA must be given within 4.5 hours',
        'advise': 'Learn FAST (Face, Arm, Speech, Time) warning signs'
    },
    'Urinary Tract Infection': {
        'medicine': ['Antibiotics (e.g., Nitrofurantoin)', 'Phenazopyridine (for pain relief)', 'Increased fluid intake'],
        'recommendation': ['Drink plenty of water', 'Urinate frequently', 'Avoid irritants (e.g., caffeine)'],
        'note': 'More common in women due to shorter urethra',
        'advise': 'Wipe front to back after bowel movements'
    },
    'Dengue Fever': {
        'medicine': ['Acetaminophen (for fever/pain)', 'Avoid NSAIDs (risk of bleeding)', 'IV fluids (for severe cases)'],
        'recommendation': ['Stay hydrated', 'Rest', 'Monitor for warning signs (e.g., bleeding)'],
        'note': 'Critical phase occurs during defervescence',
        'advise': 'Use mosquito nets and repellents'
    },
    'Hepatitis': {
        'medicine': ['Antivirals (e.g., Entecavir for Hepatitis B)', 'Interferon (for Hepatitis C)', 'Supportive care'],
        'recommendation': ['Avoid alcohol', 'Vaccination (for Hepatitis A/B)', 'Regular liver function tests'],
        'note': 'Hepatitis B and C can become chronic',
        'advise': 'Practice safe sex and avoid needle sharing'
    },
    'Kidney Cancer': {
        'medicine': ['Targeted therapy (e.g., Sunitinib)', 'Immunotherapy', 'Pain management'],
        'recommendation': ['Regular follow-ups', 'Healthy diet (low sodium)', 'Avoid smoking'],
        'note': 'Often asymptomatic until advanced stages',
        'advise': 'Monitor for paraneoplastic syndromes'
    },
    'Migraine': {
        'medicine': ['Triptans (e.g., Sumatriptan)', 'NSAIDs (e.g., Ibuprofen)', 'Preventive meds (e.g., Propranolol)'],
        'recommendation': ['Identify and avoid triggers', 'Stay hydrated', 'Rest in a dark, quiet room'],
        'note': 'Aura may precede headache in some cases',
        'advise': 'Keep a headache diary to identify patterns'
    },
    'Muscular Dystrophy': {
        'medicine': ['Corticosteroids (e.g., Prednisone)', 'Physical therapy', 'Assistive devices'],
        'recommendation': ['Regular exercise (as tolerated)', 'Respiratory support if needed', 'Genetic counseling'],
        'note': 'Duchenne type is X-linked recessive',
        'advise': 'Monitor for cardiomyopathy and respiratory failure'
    },
    'Sinusitis': {
        'medicine': ['Nasal corticosteroids (e.g., Fluticasone)', 'Decongestants', 'Antibiotics (if bacterial)'],
        'recommendation': ['Use saline nasal spray', 'Stay hydrated', 'Warm compresses'],
        'note': 'Most cases are viral and self-limiting',
        'advise': 'Consider allergy testing if recurrent'
    },
    'Ulcerative Colitis': {
        'medicine': ['Aminosalicylates (e.g., Mesalamine)', 'Immunosuppressants (e.g., Azathioprine)', 'Biologics (e.g., Infliximab)'],
        'recommendation': ['Low-residue diet during flares', 'Stress management', 'Regular colonoscopies'],
        'note': 'Continuous inflammation starting from rectum',
        'advise': 'Monitor for toxic megacolon during severe flares'
    },
    'Bipolar Disorder': {
        'medicine': ['Mood stabilizers (e.g., Lithium)', 'Antipsychotics (e.g., Quetiapine)', 'Therapy'],
        'recommendation': ['Regular sleep schedule', 'Avoid alcohol/drugs', 'Psychoeducation'],
        'note': 'Lithium requires regular blood level monitoring',
        'advise': 'Watch for early signs of mood episodes'
    },
    'Bronchitis': {
        'medicine': ['Cough suppressants (e.g., Dextromethorphan)', 'Bronchodilators (if wheezing)', 'Antibiotics (if bacterial)'],
        'recommendation': ['Stay hydrated', 'Use a humidifier', 'Avoid smoke'],
        'note': 'Most cases are viral and self-limiting',
        'advise': 'Consider smoking cessation if applicable'
    },
    'Cerebral Palsy': {
        'medicine': ['Muscle relaxants (e.g., Baclofen)', 'Anticonvulsants (if seizures)', 'Pain management'],
        'recommendation': ['Physical therapy', 'Occupational therapy', 'Assistive devices'],
        'note': 'Non-progressive brain injury causing motor impairment',
        'advise': 'Early intervention improves outcomes'
    },
    'Colorectal Cancer': {
        'medicine': ['Chemotherapy (e.g., 5-FU)', 'Targeted therapy', 'Pain management'],
        'recommendation': ['Regular screenings (colonoscopy)', 'Healthy diet (high fiber)', 'Exercise'],
        'note': 'Screening should begin at age 45 for average risk',
        'advise': 'Report any rectal bleeding immediately'
    },
    'Hypertensive Heart Disease': {
        'medicine': ['ACE inhibitors (e.g., Lisinopril)', 'Beta-blockers (e.g., Metoprolol)', 'Diuretics'],
        'recommendation': ['Low-sodium diet', 'Regular exercise', 'Monitor blood pressure'],
        'note': 'Long-term hypertension leads to LV hypertrophy',
        'advise': 'Home blood pressure monitoring recommended'
    },
    'Multiple Sclerosis': {
        'medicine': ['Disease-modifying therapies (e.g., Interferon beta)', 'Steroids (for flares)', 'Muscle relaxants'],
        'recommendation': ['Physical therapy', 'Avoid overheating', 'Stress management'],
        'note': 'Relapsing-remitting is most common form',
        'advise': 'Vitamin D supplementation may be beneficial'
    },
    'Myocardial Infarction (Heart Attack)': {
        'medicine': ['Aspirin', 'Beta-blockers', 'Statins'],
        'recommendation': ['Cardiac rehabilitation', 'Healthy diet (low fat)', 'Quit smoking'],
        'note': 'STEMI requires immediate reperfusion',
        'advise': 'Call emergency services for chest pain >15 minutes'
    },
    'Osteoporosis': {
        'medicine': ['Bisphosphonates (e.g., Alendronate)', 'Calcium/Vitamin D supplements', 'Hormone therapy'],
        'recommendation': ['Weight-bearing exercise', 'Fall prevention', 'Balanced diet'],
        'note': 'DEXA scan used for diagnosis',
        'advise': 'Take bisphosphonates with full glass of water upright'
    },
    'Pneumonia': {
        'medicine': ['Antibiotics (e.g., Azithromycin)', 'Antivirals (if viral)', 'Cough medicine'],
        'recommendation': ['Rest', 'Stay hydrated', 'Vaccination (pneumococcal/flu)'],
        'note': 'CURB-65 score helps determine severity',
        'advise': 'Complete full course of antibiotics'
    },
    'Atherosclerosis': {
        'medicine': ['Statins (e.g., Atorvastatin)', 'Antiplatelets (e.g., Aspirin)', 'Blood pressure meds'],
        'recommendation': ['Healthy diet (Mediterranean)', 'Exercise', 'Quit smoking'],
        'note': 'Leading cause of CAD and stroke',
        'advise': 'Regular lipid profile monitoring'
    },
    'Chronic Obstructive Pulmonary Disease (COPD)': {
        'medicine': ['Bronchodilators (e.g., Tiotropium)', 'Steroids (e.g., Prednisone)', 'Oxygen therapy'],
        'recommendation': ['Pulmonary rehabilitation', 'Avoid smoke/pollutants', 'Vaccinations (flu/pneumonia)'],
        'note': 'Smoking is primary risk factor',
        'advise': 'Pursed-lip breathing helps with dyspnea'
    },
    'Epilepsy': {
        'medicine': ['Anticonvulsants (e.g., Levetiracetam)', 'Vagus nerve stimulation', 'Ketogenic diet (for some)'],
        'recommendation': ['Regular medication', 'Avoid triggers (e.g., flashing lights)', 'Wear medical ID'],
        'note': 'Medication non-compliance is common cause of breakthrough',
        'advise': "Protect during seizures (don't restrain)"
    },
    'Hypertension': {
        'medicine': ['ACE inhibitors', 'Diuretics', 'Calcium channel blockers'],
        'recommendation': ['Low-sodium diet', 'Regular exercise', 'Limit alcohol'],
        'note': 'Often asymptomatic until complications develop',
        'advise': 'Home blood pressure monitoring recommended'
    },
    'Obsessive-Compulsive Disorder (OCD)': {
        'medicine': ['SSRIs (e.g., Fluoxetine)', 'Cognitive Behavioral Therapy (CBT)', 'Exposure therapy'],
        'recommendation': ['Stress management', 'Support groups', 'Regular therapy'],
        'note': 'Higher doses of SSRIs often needed than for depression',
        'advise': "Don't participate in patient's rituals"
    },
    'Psoriasis': {
        'medicine': ['Topical steroids', 'Biologics (e.g., Adalimumab)', 'Phototherapy'],
        'recommendation': ['Moisturize skin', 'Avoid triggers (e.g., stress)', 'Sun exposure in moderation'],
        'note': 'Koebner phenomenon - lesions at trauma sites',
        'advise': 'Monitor for psoriatic arthritis'
    },
    'Rubella': {
        'medicine': ['Supportive care (fever reducers)', 'Rest', 'Isolation to prevent spread'],
        'recommendation': ['Vaccination (MMR)', 'Avoid contact with pregnant women', 'Hydration'],
        'note': 'Congenital rubella syndrome causes severe birth defects',
        'advise': 'Ensure immunity before pregnancy'
    },
    'Cirrhosis': {
        'medicine': ['Diuretics (for edema)', 'Lactulose (for encephalopathy)', 'Beta-blockers (for varices)'],
        'recommendation': ['Avoid alcohol', 'Low-protein diet (if encephalopathy)', 'Regular monitoring'],
        'note': 'Irreversible liver fibrosis',
        'advise': 'Monitor for hepatic encephalopathy signs'
    },
    'Conjunctivitis (Pink Eye)': {
        'medicine': ['Antibiotic drops (if bacterial)', 'Antihistamines (if allergic)', 'Artificial tears'],
        'recommendation': ['Avoid rubbing eyes', 'Wash hands frequently', 'Avoid contact lenses'],
        'note': 'Viral conjunctivitis is highly contagious',
        'advise': "Don't share towels or eye makeup"
    },
    'Liver Disease': {
        'medicine': ['Ursodeoxycholic acid (for some types)', 'Diuretics (for ascites)', 'Lactulose (for encephalopathy)'],
        'recommendation': ['Avoid alcohol', 'Healthy diet (low fat)', 'Regular liver tests'],
        'note': 'Many types (viral, alcoholic, fatty liver)',
        'advise': 'Vaccinate against hepatitis A and B if susceptible'
    },
    'Malaria': {
        'medicine': ['Antimalarials (e.g., Chloroquine)', 'Artemisinin-based therapy', 'Quinine'],
        'recommendation': ['Mosquito prevention (nets/repellent)', 'Prophylaxis if traveling', 'Hydration'],
        'note': 'Falciparum malaria can be fatal',
        'advise': 'Use DEET repellent and bed nets in endemic areas'
    },
    'Spina Bifida': {
        'medicine': ['Surgery (for severe cases)', 'Physical therapy', 'Catheterization (if needed)'],
        'recommendation': ['Regular medical follow-ups', 'Assistive devices', 'Folic acid (prevention)'],
        'note': 'Folate deficiency in pregnancy increases risk',
        'advise': 'Women of childbearing age should take folate'
    },
    'Kidney Disease': {
        'medicine': ['ACE inhibitors', 'Erythropoietin (for anemia)', 'Diuretics'],
        'recommendation': ['Low-sodium diet', 'Monitor fluid intake', 'Dialysis if needed'],
        'note': 'Diabetes and HTN are leading causes',
        'advise': 'Monitor potassium levels carefully'
    },
    'Osteoarthritis': {
        'medicine': ['NSAIDs (e.g., Ibuprofen)', 'Acetaminophen', 'Corticosteroid injections'],
        'recommendation': ['Weight management', 'Low-impact exercise', 'Physical therapy'],
        'note': 'Wear-and-tear degenerative joint disease',
        'advise': 'Use assistive devices to reduce joint stress'
    },
    'Klinefelter Syndrome': {
        'medicine': ['Testosterone therapy', 'Speech/physical therapy (if delayed)', 'Fertility treatment (if desired)'],
        'recommendation': ['Educational support', 'Counseling', 'Regular endocrine follow-ups'],
        'note': '47,XXY karyotype',
        'advise': 'Monitor for osteoporosis and breast cancer'
    },
    'Acne': {
        'medicine': ['Topical retinoids (e.g., Tretinoin)', 'Antibiotics (e.g., Clindamycin)', 'Oral contraceptives (for females)'],
        'recommendation': ['Gentle skincare', 'Avoid picking', 'Non-comedogenic products'],
        'note': 'Hormonal acne often along jawline',
        'advise': 'Be patient - treatments take 6-8 weeks to work'
    },
    'Brain Tumor': {
        'medicine': ['Chemotherapy', 'Steroids (for swelling)', 'Anticonvulsants (if seizures)'],
        'recommendation': ['Regular imaging', 'Neurological monitoring', 'Supportive care'],
        'note': 'Symptoms depend on location and size',
        'advise': 'Report any new neurological symptoms immediately'
    },
    'Cystic Fibrosis': {
        'medicine': ['Bronchodilators', 'Pancreatic enzymes', 'CFTR modulators (e.g., Ivacaftor)'],
        'recommendation': ['Airway clearance techniques', 'High-calorie diet', 'Regular exercise'],
        'note': 'Autosomal recessive disorder',
        'advise': 'Genetic counseling for family planning'
    },
    'Glaucoma': {
        'medicine': ['Prostaglandin analogs (e.g., Latanoprost)', 'Beta-blocker drops', 'Oral carbonic anhydrase inhibitors'],
        'recommendation': ['Regular eye pressure checks', 'Avoid straining', 'Medication adherence'],
        'note': 'Silent thief of sight - often asymptomatic early',
        'advise': "Don't stop drops without doctor approval"
    },
    'Rabies': {
        'medicine': ['Post-exposure prophylaxis (vaccine + immunoglobulin)', 'Supportive care (if symptomatic)'],
        'recommendation': ['Immediate medical attention after exposure', 'Vaccinate pets', 'Avoid wild animals'],
        'note': 'Nearly 100% fatal once symptoms appear',
        'advise': 'Seek care immediately after any bat exposure'
    },
    'Chickenpox': {
        'medicine': ['Acetaminophen (for fever)', 'Antivirals (e.g., Acyclovir for severe cases)', 'Calamine lotion (for itching)'],
        'recommendation': ['Stay hydrated', 'Avoid scratching', 'Isolate to prevent spread'],
        'note': 'More severe in adults than children',
        'advise': 'Vaccination available (Varivax)'
    },
    'Coronary Artery Disease': {
        'medicine': ['Statins', 'Beta-blockers', 'Nitroglycerin (for angina)'],
        'recommendation': ['Cardiac rehab', 'Healthy diet (low cholesterol)', 'Regular exercise'],
        'note': 'Leading cause of death worldwide',
        'advise': 'Know angina symptoms and when to seek help'
    },
    'Eating Disorders (Anorexia/Bulimia)': {
        'medicine': ['SSRIs (e.g., Fluoxetine)', 'Nutritional supplements', 'Electrolyte management'],
        'recommendation': ['Therapy (CBT)', 'Nutritional counseling', 'Support groups'],
        'note': 'High relapse rate without comprehensive treatment',
        'advise': 'Family involvement crucial for recovery'
    },
    'Fibromyalgia': {
        'medicine': ['Pregabalin', 'Duloxetine', 'NSAIDs (for pain)'],
        'recommendation': ['Gentle exercise (e.g., yoga)', 'Sleep hygiene', 'Stress reduction'],
        'note': 'Diagnosis of exclusion with widespread pain',
        'advise': 'Pacing activities helps prevent flares'
    },
    'Hemophilia': {
        'medicine': ['Factor VIII/IX replacement', 'Antifibrinolytics (e.g., Tranexamic acid)', 'Pain management'],
        'recommendation': ['Avoid high-impact sports', 'Regular factor checks', 'Genetic counseling'],
        'note': 'X-linked recessive (mainly affects males)',
        'advise': 'Wear medical alert bracelet'
    },
    'Hypoglycemia': {
        'medicine': ['Glucose tablets/gel', 'Glucagon injection (for severe cases)'],
        'recommendation': ['Frequent small meals', 'Monitor blood sugar', 'Carry fast-acting carbs'],
        'note': 'Common complication in diabetes treatment',
        'advise': '15-15 rule: 15g carbs, wait 15 minutes, recheck'
    },
    'Lymphoma': {
        'medicine': ['Chemotherapy', 'Immunotherapy', 'Radiation'],
        'recommendation': ['Regular oncologist visits', 'Nutritional support', 'Infection prevention'],
        'note': 'Hodgkin vs non-Hodgkin have different treatments',
        'advise': 'Monitor for B symptoms (fever, night sweats)'
    },
    'Tuberculosis': {
        'medicine': ['Rifampin', 'Isoniazid', 'Pyrazinamide'],
        'recommendation': ['Complete full course of antibiotics', 'Isolation (if active)', 'Ventilate living spaces'],
        'note': 'Requires 6+ months of treatment',
        'advise': 'Directly observed therapy (DOT) improves adherence'
    },
    'Lung Cancer': {
        'medicine': ['Targeted therapy (e.g., Erlotinib)', 'Immunotherapy', 'Chemotherapy'],
        'recommendation': ['Quit smoking', 'Pulmonary rehab', 'Palliative care if needed'],
        'note': 'Smoking causes 80-90% of cases',
        'advise': 'Low-dose CT screening for high-risk patients'
    },
    'Hypothyroidism': {
        'medicine': ['Levothyroxine', 'Regular TSH checks'],
        'recommendation': ['Take medication on empty stomach', 'Monitor for symptoms', 'Balanced diet'],
        'note': "Hashimoto's is most common cause",
        'advise': "Don't take thyroid meds with calcium/iron"
    },
    'Autism Spectrum Disorder (ASD)': {
        'medicine': ['Antipsychotics (for irritability)', 'SSRIs (for anxiety)', 'Behavioral therapy'],
        'recommendation': ['Structured routines', 'Speech/occupational therapy', 'Parent training'],
        'note': 'Spectrum with wide variation in symptoms',
        'advise': 'Early intervention improves outcomes'
    },
    "Crohn's Disease": {
        'medicine': ['Corticosteroids (e.g., Prednisone)', 'Immunosuppressants (e.g., Azathioprine)', 'Biologics (e.g., Infliximab)'],
        'recommendation': ['Low-residue diet during flares', 'Stress management', 'Regular colonoscopies'],
        'note': 'Can affect any part of GI tract',
        'advise': 'Monitor for strictures and fistulas'
    },
    'Hyperglycemia': {
        'medicine': ['Insulin', 'Oral hypoglycemics (e.g., Metformin)', 'Hydration'],
        'recommendation': ['Monitor blood sugar', 'Healthy diet', 'Exercise'],
        'note': 'Can lead to DKA or HHS if severe',
        'advise': 'Check ketones if blood sugar >250 mg/dL'
    },
    'Melanoma': {
        'medicine': ['Immunotherapy (e.g., Pembrolizumab)', 'Targeted therapy (e.g., Vemurafenib)', 'Surgery'],
        'recommendation': ['Sun protection (SPF 50+)', 'Regular skin checks', 'Avoid tanning beds'],
        'note': 'ABCDE rule for identifying suspicious moles',
        'advise': 'Monthly self-skin exams'
    },
    'Ovarian Cancer': {
        'medicine': ['Chemotherapy (e.g., Carboplatin)', 'PARP inhibitors (e.g., Olaparib)', 'Hormone therapy'],
        'recommendation': ['Genetic testing (BRCA)', 'Regular follow-ups', 'Healthy diet'],
        'note': 'Often diagnosed at late stage',
        'advise': 'Report persistent bloating/pelvic pain'
    },
    'Turner Syndrome': {
        'medicine': ['Growth hormone (for short stature)', 'Estrogen therapy (for puberty)', 'Heart monitoring'],
        'recommendation': ['Regular endocrine checks', 'Educational support', 'Counseling'],
        'note': '45,X karyotype',
        'advise': 'Monitor for aortic dissection risk'
    },
    'Zika Virus': {
        'medicine': ['Supportive care (fever/pain relief)', 'Rest', 'Hydration'],
        'recommendation': ['Mosquito protection', 'Avoid pregnancy for months after infection', 'No specific antiviral'],
        'note': 'Causes microcephaly in fetal infection',
        'advise': 'Postpone pregnancy if in endemic area'
    },
    'Cataracts': {
        'medicine': ['Surgery (phacoemulsification)', 'Artificial lens implantation'],
        'recommendation': ['UV-protective sunglasses', 'Regular eye exams', 'Manage diabetes if present'],
        'note': 'Leading cause of blindness worldwide',
        'advise': 'Surgery indicated when vision impaired'
    },
    'Pneumocystis Pneumonia (PCP)': {
        'medicine': ['Antibiotics (e.g., Trimethoprim-sulfamethoxazole)', 'Steroids (for severe cases)', 'Oxygen therapy'],
        'recommendation': ['Prophylaxis if immunocompromised', 'Avoid smoking', 'Monitor oxygen levels'],
        'note': 'AIDS-defining illness',
        'advise': 'HIV testing if PCP occurs'
    },
    'Scoliosis': {
        'medicine': ['Bracing (for moderate cases)', 'Pain relievers', 'Surgery (for severe curvature)'],
        'recommendation': ['Physical therapy', 'Regular monitoring', 'Core-strengthening exercises'],
        'note': 'Most common in adolescent girls',
        'advise': 'Early detection improves outcomes'
    },
    'Sickle Cell Anemia': {
        'medicine': ['Hydroxyurea', 'Pain management', 'Folic acid supplements'],
        'recommendation': ['Stay hydrated', 'Avoid extreme temperatures', 'Vaccinations (pneumococcal)'],
        'note': 'Autosomal recessive inheritance',
        'advise': 'Seek care for pain crises or fever'
    },
    'Tetanus': {
        'medicine': ['Tetanus immune globulin', 'Muscle relaxants (e.g., Diazepam)', 'Antibiotics (e.g., Metronidazole)'],
        'recommendation': ['Vaccination (DTaP/Tdap)', 'Wound care', 'Immediate medical attention for wounds'],
        'note': 'Caused by Clostridium tetani toxin',
        'advise': 'Booster needed every 10 years'
    },
    'Anemia': {
        'medicine': ['Iron supplements (for iron-deficiency)', 'Vitamin B12 injections', 'Erythropoietin (for some types)'],
        'recommendation': ['Iron-rich diet (e.g., leafy greens)', 'Vitamin C (to enhance iron absorption)', 'Treat underlying cause'],
        'note': 'Workup should determine type and cause',
        'advise': 'Iron supplements cause black stools'
    },
    'Cholera': {
        'medicine': ['Oral rehydration solution (ORS)', 'Antibiotics (e.g., Doxycycline)', 'Zinc supplements'],
        'recommendation': ['Boil water', 'Wash hands frequently', 'Vaccination (for travelers)'],
        'note': 'Rice-water stools characteristic',
        'advise': 'Rehydration is primary treatment'
    },
    'Endometriosis': {
        'medicine': ['NSAIDs (e.g., Ibuprofen)', 'Hormonal therapy (e.g., Birth control pill)', 'GnRH agonists (e.g., Leuprolide)'],
        'recommendation': ['Heat therapy for pain', 'Regular exercise', 'Surgery (if severe)'],
        'note': 'Endometrial tissue outside uterus',
        'advise': 'Can cause infertility if severe'
    },
    'Sepsis': {
        'medicine': ['IV antibiotics', 'IV fluids', 'Vasopressors (for low BP)'],
        'recommendation': ['Immediate hospitalization', 'Source control (e.g., drain infection)', 'Monitor organ function'],
        'note': 'Life-threatening organ dysfunction',
        'advise': 'Know sepsis signs (fever, confusion, SOB)'
    },
    'Sleep Apnea': {
        'medicine': ['CPAP machine', 'Oral appliances', 'Surgery (in some cases)'],
        'recommendation': ['Weight loss if overweight', 'Avoid alcohol/sedatives', 'Side sleeping'],
        'note': 'Obstructive type most common',
        'advise': 'CPAP compliance crucial for benefits'
    },
    'Down Syndrome': {
        'medicine': ['Thyroid hormone (if hypothyroid)', 'Hearing/vision aids', 'Early intervention programs'],
        'recommendation': ['Regular health screenings', 'Speech/physical therapy', 'Educational support'],
        'note': 'Trisomy 21',
        'advise': 'Monitor for atlantoaxial instability'
    },
    'Ebola Virus': {
        'medicine': ['Supportive care (IV fluids)', 'Experimental antivirals (e.g., Remdesivir)', 'Symptom management'],
        'recommendation': ['Strict isolation', 'PPE for caregivers', 'Avoid outbreak areas'],
        'note': 'High mortality rate (up to 90%)',
        'advise': 'Follow CDC travel advisories'
    },
    'Lyme Disease': {
        'medicine': ['Antibiotics (e.g., Doxycycline)', 'IV antibiotics (for late-stage)', 'Pain relievers'],
        'recommendation': ['Tick prevention (repellent/checks)', 'Remove ticks promptly', 'Monitor for rash/fever'],
        'note': 'Erythema migrans rash is hallmark',
        'advise': 'Check for ticks after outdoor activities'
    },
    'Pancreatic Cancer': {
        'medicine': ['Chemotherapy (e.g., Gemcitabine)', 'Pain management', 'Surgery (if resectable)'],
        'recommendation': ['Palliative care', 'Nutritional support', 'Genetic counseling'],
        'note': 'Often diagnosed at advanced stage',
        'advise': 'Monitor for new-onset diabetes'
    },
    'Pneumothorax': {
        'medicine': ['Oxygen therapy', 'Chest tube insertion', 'Needle aspiration'],
        'recommendation': ['Avoid smoking', 'No air travel until resolved', 'Monitor for recurrence'],
        'note': 'Tall thin males at higher risk',
        'advise': 'Seek care immediately for chest pain/SOB'
    },
    'Appendicitis': {
        'medicine': ['IV antibiotics (if uncomplicated)', 'Appendectomy (surgery)'],
        'recommendation': ['Seek immediate medical attention', 'No laxatives if suspected', 'Post-op wound care'],
        'note': "McBurney's point tenderness classic",
        'advise': "Don't delay treatment - risk of rupture"
    },
    'Esophageal Cancer': {
        'medicine': ['Chemotherapy', 'Radiation', 'Surgery'],
        'recommendation': ['Avoid tobacco/alcohol', 'Small, frequent meals', 'Nutritional support'],
        'note': 'Adenocarcinoma vs squamous cell types',
        'advise': 'Monitor for dysphagia/weight loss'
    },
    'HIV/AIDS': {
        'medicine': ['Antiretroviral therapy (ART)', 'Prophylactic antibiotics (e.g., Bactrim)', 'Pain management'],
        'recommendation': ['Adherence to ART', 'Safe sex practices', 'Regular CD4/viral load tests'],
        'note': 'Untreated leads to AIDS (<200 CD4)',
        'advise': 'U=U (Undetectable = Untransmittable)'
    },
    'Marfan Syndrome': {
        'medicine': ['Beta-blockers (to reduce aortic stress)', 'Surgery (for aortic aneurysm)', 'Regular cardiac imaging'],
        'recommendation': ['Avoid intense physical activity', 'Regular cardiology visits', 'Genetic counseling'],
        'note': 'FBN1 gene mutation',
        'advise': 'Monitor for aortic dissection'
    },
    "Parkinson's Disease": {
        'medicine': ['Levodopa/Carbidopa', 'Dopamine agonists (e.g., Pramipexole)', 'MAO-B inhibitors (e.g., Selegiline)'],
        'recommendation': ['Physical therapy', 'Fall prevention', 'Speech therapy'],
        'note': 'Dopamine deficiency in substantia nigra',
        'advise': 'Medication timing crucial for symptom control'
    },
    'Hemorrhoids': {
        'medicine': ['Topical corticosteroids', 'Stool softeners (e.g., Docusate)', 'Pain relievers'],
        'recommendation': ['High-fiber diet', 'Sitz baths', 'Avoid straining'],
        'note': 'Internal vs external types',
        'advise': "Don't ignore rectal bleeding - rule out cancer"
    },
     'Polycystic Ovary Syndrome (PCOS)': {
        'medicine': ['Birth control pills (for regulation)', 'Metformin (for insulin resistance)', 'Fertility drugs (if desired)'],
        'recommendation': ['Weight management', 'Regular exercise', 'Balanced diet'],
        'note': 'PCOS is a hormonal disorder causing enlarged ovaries with small cysts. Insulin resistance is common.',
        'advice': 'Monitor blood sugar levels; consult an endocrinologist for long-term management.'
    },
    'Systemic Lupus Erythematosus (SLE)': {
        'medicine': ['Hydroxychloroquine', 'Corticosteroids (e.g., Prednisone)', 'Immunosuppressants (e.g., Azathioprine)'],
        'recommendation': ['Sun protection', 'Rest during flares', 'Regular lab monitoring'],
        'note': 'SLE is an autoimmune disease affecting multiple organs. Flares can be triggered by stress/sun exposure.',
        'advice': 'Use SPF 50+ sunscreen daily; track symptoms for early flare detection.'
    },
    'Typhoid Fever': {
        'medicine': ['Antibiotics (e.g., Ciprofloxacin)', 'Hydration', 'Fever reducers'],
        'recommendation': ['Vaccination (for travelers)', 'Safe food/water practices', 'Hand hygiene'],
        'note': 'Caused by Salmonella typhi. Spread through contaminated food/water. Can be life-threatening without treatment.',
        'advice': 'Boil water in endemic areas; seek immediate care for persistent high fever + diarrhea.'
    },
    'Breast Cancer': {
        'medicine': ['Chemotherapy', 'Hormone therapy (e.g., Tamoxifen)', 'Targeted therapy (e.g., Trastuzumab)'],
        'recommendation': ['Regular mammograms', 'Genetic testing (BRCA)', 'Healthy lifestyle'],
        'note': 'Most common cancer in women. Early detection improves survival rates significantly.',
        'advice': 'Perform monthly self-exams; start annual mammograms at age 40 (or earlier if high-risk).'
    },
    'Measles': {
        'medicine': ['Vitamin A (for severe cases)', 'Fever reducers', 'Supportive care'],
        'recommendation': ['MMR vaccination', 'Isolation', 'Hydration'],
        'note': 'Highly contagious viral infection. Complications include pneumonia/encephalitis.',
        'advice': 'Unvaccinated individuals should avoid contact for 4 days after rash onset.'
    },
    'Osteomyelitis': {
        'medicine': ['IV antibiotics (e.g., Vancomycin)', 'Surgery (to remove dead bone)', 'Pain management'],
        'recommendation': ['Complete full antibiotic course', 'Wound care', 'Immobilization if needed'],
        'note': 'Bone infection often caused by Staph aureus. Diabetics/IV drug users at higher risk.',
        'advice': 'Never skip antibiotic doses; monitor for signs of sepsis (fever, confusion).'
    },
    'Polio': {
        'medicine': ['Supportive care', 'Physical therapy', 'Pain relievers'],
        'recommendation': ['Vaccination (IPV)', 'Respiratory support if needed', 'Rehabilitation'],
        'note': 'Viral disease causing paralysis. Eradicated in most countries but still exists in few regions.',
        'advice': 'Ensure children receive all 4 doses of polio vaccine; travelers to endemic areas need boosters.'
    },
    'Chronic Kidney Disease': {
        'medicine': ['ACE inhibitors', 'Erythropoietin (for anemia)', 'Phosphate binders'],
        'recommendation': ['Low-protein diet', 'Monitor fluid intake', 'Dialysis if needed'],
        'note': 'Progressive loss of kidney function. Staged from 1 (mild) to 5 (end-stage requiring dialysis).',
        'advice': 'Limit potassium/phosphate intake; regularly check creatinine/GFR levels.'
    },
    'Hepatitis B': {
        'medicine': ['Antivirals (e.g., Entecavir)', 'Interferon', 'Regular liver monitoring'],
        'recommendation': ['Vaccination (if not infected)', 'Avoid alcohol', 'Safe sex practices'],
        'note': 'Viral infection causing liver inflammation. Can lead to cirrhosis/liver cancer if chronic.',
        'advice': 'Get family members tested; never share razors/needles; monitor for jaundice.'
    },
    'Prader-Willi Syndrome': {
        'medicine': ['Growth hormone therapy', 'Behavioral therapy', 'Sex hormone replacement (if needed)'],
        'recommendation': ['Strict diet control', 'Regular exercise', 'Educational support'],
        'note': 'Genetic disorder causing insatiable hunger, low muscle tone, and developmental delays.',
        'advice': 'Lock food cabinets; establish rigid meal routines; seek early intervention services.'
    },
    'Thyroid Cancer': {
        'medicine': ['Thyroid hormone replacement (after surgery)', 'Radioactive iodine therapy', 'Targeted therapy (for advanced)'],
        'recommendation': ['Regular thyroid checks', 'Monitor for recurrence', 'Healthy diet'],
        'note': 'Most are papillary carcinomas with excellent prognosis when caught early.',
        'advice': 'Take thyroid meds on empty stomach; watch for hoarseness/lumps in neck during follow-ups.'
    },
    'Bladder Cancer': {
        'medicine': ['BCG immunotherapy', 'Chemotherapy', 'Surgery'],
        'recommendation': ['Quit smoking', 'Regular cystoscopies', 'Hydration'],
        'note': 'Smoking is the #1 risk factor. Often presents with painless hematuria (blood in urine).',
        'advice': 'Report any blood in urine immediately; avoid occupational chemical exposures.'
    },
    'Otitis Media (Ear Infection)': {
        'medicine': ['Antibiotics (e.g., Amoxicillin)', 'Pain relievers', 'Warm compresses'],
        'recommendation': ['Avoid secondhand smoke', 'Vaccinations (pneumococcal)', 'Breastfeeding (reduces risk in infants)'],
        'note': 'Common in children due to shorter Eustachian tubes. Most viral cases resolve without antibiotics.',
        'advice': 'Use antibiotics only for confirmed bacterial infections to prevent resistance.'
    },
    'Tourette Syndrome': {
        'medicine': ['Antipsychotics (e.g., Haloperidol)', 'Behavioral therapy', 'Alpha-2 agonists (e.g., Clonidine)'],
        'recommendation': ['Educational support', 'Stress management', 'Support groups'],
        'note': 'Neurological disorder with motor/vocal tics. Often coexists with ADHD/OCD.',
        'advice': 'Avoid pointing out tics; provide quiet spaces for stress relief; educate teachers/peers.'
    },
    "Alzheimer's Disease": {
        'medicine': ['Cholinesterase inhibitors (e.g., Donepezil)', 'Memantine', 'Antidepressants (if needed)'],
        'recommendation': ['Cognitive stimulation', 'Safe home environment', 'Caregiver support'],
        'note': 'Progressive neurodegenerative disease. Early signs include memory loss and disorientation.',
        'advice': 'Label household items; establish daily routines; consider legal/financial planning early.'
    },
    'Dementia': {
        'medicine': ['Cholinesterase inhibitors', 'Memantine', 'Antipsychotics (for agitation)'],
        'recommendation': ['Structured routine', 'Cognitive exercises', 'Safety modifications at home'],
        'note': 'Umbrella term for cognitive decline. Alzheimer’s is the most common type.',
        'advice': 'Use calendars/clocks prominently; avoid sudden environment changes; simplify tasks.'
    },
    'Diverticulitis': {
        'medicine': ['Antibiotics (e.g., Ciprofloxacin + Metronidazole)', 'Clear liquid diet (during flare)', 'Pain relievers'],
        'recommendation': ['High-fiber diet (when not inflamed)', 'Hydration', 'Avoid nuts/seeds (controversial)'],
        'note': 'Inflammation of colon pouches. Severe cases may cause perforation requiring surgery.',
        'advice': 'Transition slowly to high-fiber foods; seek ER care for severe pain/fever.'
    },
    'Mumps': {
        'medicine': ['Supportive care (fever/pain relief)', 'Rest', 'Hydration'],
        'recommendation': ['MMR vaccination', 'Isolation', 'Warm/cold compresses for swelling'],
        'note': 'Viral infection causing parotid gland swelling. Complications include orchitis in males.',
        'advice': 'Apply ice packs for jaw pain; monitor for testicular swelling in post-pubertal males.'
    },
    'Cholecystitis': {
        'medicine': ['Antibiotics (e.g., Piperacillin-tazobactam)', 'Pain management', 'Cholecystectomy (surgery)'],
        'recommendation': ['Low-fat diet', 'Weight management', 'Post-op care'],
        'note': 'Gallbladder inflammation, often due to stones. "5 F’s" risk factors: Female, Fat, Forty, Fertile, Fair.',
        'advice': 'Avoid fatty meals pre-surgery; report yellow skin/eyes (jaundice) immediately.'
    },
    'Prostate Cancer': {
        'medicine': ['Hormone therapy (e.g., Leuprolide)', 'Chemotherapy', 'Radiation'],
        'recommendation': ['Regular PSA checks', 'Healthy diet', 'Exercise'],
        'note': 'Most grow slowly, but aggressive forms exist. Screening debated for low-risk men.',
        'advice': 'Discuss PSA testing pros/cons with doctor; report urinary changes promptly.'
    },
    'Schizophrenia': {
        'medicine': ['Antipsychotics (e.g., Risperidone)', 'Therapy', 'Social skills training'],
        'recommendation': ['Medication adherence', 'Support groups', 'Avoid substance abuse'],
        'note': 'Chronic brain disorder with hallucinations/delusions. Usually appears in late teens-30s.',
        'advice': 'Create crisis plan; watch for medication side effects like weight gain/tremors.'
    },
    'Gout': {
        'medicine': ['NSAIDs (e.g., Indomethacin)', 'Colchicine', 'Allopurinol (for prevention)'],
        'recommendation': ['Low-purine diet', 'Hydration', 'Limit alcohol'],
        'note': 'Uric acid crystal deposition causing sudden severe joint pain (often big toe).',
        'advice': 'Avoid organ meats/shellfish; elevate affected joint; don’t stop allopurinol during attacks.'
    },
    'Testicular Cancer': {
        'medicine': ['Chemotherapy (e.g., Bleomycin)', 'Radiation', 'Surgery (orchiectomy)'],
        'recommendation': ['Regular self-exams', 'Sperm banking (if desired)', 'Follow-up care'],
        'note': 'Most common in men 15-35. Highly treatable even when metastatic.',
        'advice': 'Perform monthly self-exams after warm showers; report any testicular lumps immediately.'
    },
    'Tonsillitis': {
        'medicine': ['Antibiotics (if bacterial)', 'Pain relievers', 'Warm saltwater gargles'],
        'recommendation': ['Hydration', 'Rest', 'Tonsillectomy if recurrent'],
        'note': 'Strep throat requires antibiotics to prevent rheumatic fever complications.',
        'advice': 'Complete full antibiotic course; use humidifier for comfort; watch for difficulty breathing.'
    },
    'Williams Syndrome': {
        'medicine': ['Calcium/vitamin D (for hypercalcemia)', 'Blood pressure meds', 'Developmental therapies'],
        'recommendation': ['Cardiac monitoring', 'Educational support', 'Social skills training'],
        'note': 'Genetic disorder causing elfin facial features, cardiovascular issues, and extreme sociability.',
        'advice': 'Regular cardiac ultrasounds; teach stranger danger (due to overly friendly behavior).'
    }
}

app = Flask(__name__)

@app.route("/",methods=['POST','GET'])
def start():
    return render_template('index.html')

@app.route("/model_form",methods=['POST','GET'])
def start1():
    if request.method == 'POST':
        die = request.form.get('die')
        age = request.form.get('age')
        gender = request.form.get('gender')
        headache = request.form.get('Headache')
        cough = request.form.get('cough')
        fever = request.form.get('fever')
        dizz = request.form.get('dizz')
        blu_vis = request.form.get('blu_vis')
        ches_pai = request.form.get('ches_pai')
        fati = request.form.get('fati')
        shor_brea = request.form.get('shor_brea')
        diff_brea = request.form.get('diff_brea')
        ireg_hertb = request.form.get('ireg_hertb')
        sweat = request.form.get('sweat')
        slp_pr = request.form.get('slp_pr')
        swel_leg = request.form.get('swel_leg')
        tinnit = request.form.get('tinnit')
        time.sleep(10)
        result = bpmodel(age,gender,headache,dizz,blu_vis,ches_pai,fati,shor_brea,ireg_hertb,sweat,slp_pr,swel_leg,tinnit)
        if result == 0:
            text = "Low Blood Pressure"
            bp = 'Low'
        elif result == 1:
            text = "Normal Blood Pressure"
            bp = 'Normal'
        else:
            text = "High Blood Pressure"
            bp = 'High'
            
            
        result1 = dies(die,fever,cough,fati,diff_brea,age,gender,bp)
        if result1 == 'Negative':
            test = 'Negative'
            text1 = "Consult a healthcare provider if symptoms persist or new concerns arise."
        else:
            test = 'Positive'
            text1 = "Contact your healthcare provider immediately." 
            
        # Sample response - should be mapped to real predictions
        if result1 =="Positive":
            response = {
                "condition": text,
                "description": f"Result for {die} is {test}." + text1,
                "prescription": {
                    "medications": prescriptions[die]["medicine"],
                    "recommendations":  prescriptions[die]["recommendation"],
                    "note":  prescriptions[die]["note"]+".",
                    "advise":  prescriptions[die]["advise"]+".",
                    "warning": "See a doctor if condition worsens."
                }
            }
        else:
            response = {
                "condition": text,
                "description": f"Result for {die} is {test}." + text1,
                "prescription": {
                    "medications": ["You are Fit."],
                    "recommendations": ["No Needed."],
                    "note":  "None",
                    "advise": "None",
                    "warning": "See a doctor if condition worsens."
                }
            }
        return jsonify(response)
    # return render_template('sub.html',al=mk)


# Load hospital data once when server starts
hospital_data = pd.read_csv(r'D:\project\First Aid\first_aid\hospitals_cleaned_india.csv')

# Home page
@app.route("/search/", methods=['GET', 'POST'])
def search_hospitals():
    query = request.args.get('query', '').strip().lower()

    if not query:
        return jsonify([])

    results = hospital_data[
        hospital_data['Hospital Name'].str.lower().str.contains(query, na=False) |
        hospital_data['City'].str.lower().str.contains(query, na=False)
    ]

    hospitals = []
    for _, row in results.iterrows():
        hospitals.append({
            'name': row['Hospital Name'],
            'address': row['Address'],
            'city': row['City'],
            'phone': row['Phone'],
            'pincode': row['Pincode'],
            'state': row['State'],
        })

    return jsonify(hospitals)


if __name__=='__main__':
    app.run(debug=True)
    