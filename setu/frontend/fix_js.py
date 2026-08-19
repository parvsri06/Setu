import re

with open('setu_ui_proposal.html', 'r', encoding='utf-8') as f:
    content = f.read()

script_start = content.find('<script>')
script_end = content.rfind('</script>')
if script_start < 0 or script_end < 0:
    print("ERROR: Could not find script tags"); exit(1)

js = content[script_start + len('<script>'):script_end].strip()

lang_start = js.find("// ================= LANGUAGE / TRANSLATION =================")
state_start = js.find("// ================= STATE =================")
if lang_start < 0 or state_start < 0:
    print("ERROR: Could not find markers"); exit(1)

lang_line_start = js.rfind("\n", 0, lang_start) + 1

en_dict = r"""// ================= ENGLISH TEXT =================
  const TXT = {
    w_sub: 'Disaster Survey',
    w_tagline: 'Report flood-affected people and damage, even without internet.',
    w_start: 'Start Survey',
    w_offline: 'Offline-ready',
    w_note: 'Your answers are saved on this device and can be transferred through nearby Setu devices when connectivity becomes available.',
    step1: 'Step 1 of 6', step2: 'Step 2 of 6', step3: 'Step 3 of 6', step4: 'Step 4 of 6', step5: 'Step 5 of 6', step6: 'Step 6 of 6',
    s_personal_t: 'Personal Details', s_personal_d: 'Basic information of the affected person / family.',
    s_location_t: 'Location Details', s_location_d: 'Where is the affected area?',
    s_damage_t: 'Disaster & Damage Details', s_damage_d: 'What was damaged?',
    s_casualty_t: 'Casualty Details', s_casualty_d: 'Add one or more affected persons. Choose one status per person.',
    s_camp_t: 'Relief Camp Details', s_camp_d: 'Helps rescue teams know where people are staying.',
    s_review_t: 'Review', s_review_d: 'Check everything before you save.',
    s_saved_t: 'Survey Saved Successfully', s_saved_d: 'Thank you \u2014 this information will help rescue teams.',
    f_name: 'Full Name', f_name_ph: 'Enter full name',
    f_father: "Father's Name", f_father_ph: "Enter father's name",
    f_mobile: 'Mobile Number', f_mobile_ph: 'Enter 10-digit mobile number',
    f_aadhaar: 'Aadhaar Number', f_aadhaar_ph: 'Enter 12-digit Aadhaar number',
    f_family: 'Family ID', f_family_ph: 'Enter Family ID (optional)',
    f_village: 'Village / Town', f_village_ph: 'Enter village/town',
    f_district: 'District', f_district_ph: 'Select district',
    f_po: 'Post Office', f_po_ph: 'Enter post office',
    f_ps: 'Nearest Police Station', f_ps_ph: 'Enter police station',
    f_pin: 'PIN Code', f_pin_ph: 'Enter 6-digit PIN code',
    loc_note: 'Manual location fields only \u2014 no GPS needed.',
    f_dtype: 'Type of Disaster', f_dtype_ph: 'Select disaster type',
    f_dother: 'Specify Other Disaster Type', f_dother_ph: 'Enter disaster type',
    f_ddate: 'Date of Damage',
    f_darea: 'Damage Area',
    f_ddesc: 'Damage Description', f_ddesc_ph: 'Describe the damage',
    f_dphoto: 'Damage Proof / Photos',
    btn_addphoto: '+ Add Damage Photos',
    photo_none: 'No photos added', photo_one: '1 photo added', photo_many: '{n} photos added', photo_opt: 'optional \u00b7 JPG / PNG / WEBP',
    sample_link: "Can't pick photos in this demo? Add sample photos",
    c_name: 'Name', c_name_ph: "Enter person's name",
    c_age: 'Age', c_age_ph: 'Enter age',
    c_gender: 'Gender', c_status: 'Status',
    c_loc: 'Residential / Current Location', c_loc_ph: 'Enter current location',
    c_add: '+ Add Another Person', c_remove: 'Remove Person',
    g_male: 'Male', g_female: 'Female', g_other: 'Other',
    st_alive: 'Alive', st_missing: 'Missing', st_notalive: 'Not Alive',
    camp_q: 'Is the family staying in a relief camp?',
    camp_name: 'Relief Camp Name', camp_name_ph: 'Enter camp name',
    camp_loc: 'Camp Location', camp_loc_ph: 'Enter camp location',
    camp_addr: 'Camp Address', camp_addr_ph: 'Enter camp address',
    camp_land: 'Landmark', camp_land_ph: 'Enter nearby landmark',
    yes: 'Yes', no: 'No',
    r_personal: 'Personal Details', r_location: 'Location', r_damage: 'Disaster / Damage', r_casualty: 'Casualties', r_camp: 'Relief Camp',
    r_name: 'Name', r_father: "Father's Name", r_mobile: 'Mobile', r_aadhaar: 'Aadhaar', r_family: 'Family ID',
    r_village: 'Village / Town', r_district: 'District', r_po: 'Post Office', r_ps: 'Police Station', r_pin: 'PIN Code',
    r_disaster: 'Disaster', r_date: 'Date of Damage', r_area: 'Damage Area', r_desc: 'Description', r_photos: 'Photos',
    r_people: 'People', r_person: 'Person', r_campname: 'Camp Name', r_camploc: 'Camp Location', r_addr: 'Address', r_land: 'Landmark',
    r_incomplete: 'Incomplete', r_edit: 'Edit',
    banner_title: 'Some details need attention',
    saved_id: 'SURVEY ID',
    saved_view: 'View Saved Surveys', saved_new: 'Create New Survey',
    opt: 'Optional',
    err_required: 'This field is required.',
    err_name: 'Enter a valid name \u2014 letters and spaces only.',
    err_mobile: 'Enter a valid 10-digit mobile number starting with 6, 7, 8 or 9.',
    err_aadhaar: 'Aadhaar number must contain exactly 12 digits \u2014 no spaces or symbols.',
    err_pin: 'Enter a valid 6-digit PIN code \u2014 numbers only.',
    err_future: 'Date of damage cannot be in the future.',
    err_age: 'Enter a valid age (0\u2013120).',
    err_cas: 'Every person needs a valid name, age, gender, status and current location.',
    err_camp: 'Camp name and camp location are required.',
    toast_draft: 'Draft saved on this device',
    draft_note: 'Saves on this device \u2014 no internet needed.',
    save_survey: 'Save Survey',
    a_house: 'House', a_shop: 'Shop', a_agri: 'Agricultural Land', a_road: 'Road', a_vehicle: 'Vehicle', a_other: 'Other',
    opt_flood: 'Flood', opt_cyclone: 'Cyclone', opt_landslide: 'Landslide', opt_earthquake: 'Earthquake', opt_fire: 'Fire', opt_storm: 'Storm', opt_other: 'Other',
    btn_draft: 'Save Draft', next: 'Next',
    saved: 'Saved'
  };
  const T = (k) => TXT[k] || k;
  const TR = (v) => {
    const m = { Flood:'opt_flood', Cyclone:'opt_cyclone', Landslide:'opt_landslide', Earthquake:'opt_earthquake', Fire:'opt_fire', Storm:'opt_storm', Other:'opt_other',
      House:'a_house', Shop:'a_shop', 'Agricultural Land':'a_agri', Road:'a_road', Vehicle:'a_vehicle',
      Male:'g_male', Female:'g_female', Alive:'st_alive', Missing:'st_missing', 'Not Alive':'st_notalive', Yes:'yes', No:'no' };
    return m[v] ? T(m[v]) : v;
  };
  // ================= STATE ================="""

new_js = js[:lang_line_start] + en_dict + '\n  ' + js[state_start:]

# Update CAPTIONS
cap_match = re.search(r'const CAPTIONS = \[.*?\];', new_js, re.DOTALL)
if cap_match:
    new_captions = """  const CAPTIONS = [
    { t: 'Welcome', b: 'One clear action: Start Survey.' },
    { t: 'Personal Details', b: 'Only what rescue teams need to identify a person.' },
    { t: 'Location', b: 'Manual administrative location.' },
    { t: 'Disaster & Damage', b: 'Disaster type, date, damage areas, description, and optional photos.' },
    { t: 'Casualties', b: 'One card per affected person. Alive / Missing / Not Alive.' },
    { t: 'Relief Camp', b: 'A single Yes/No question.' },
    { t: 'Review', b: 'Shows exactly what you entered. Tap Edit to change a section, then Save.' },
    { t: 'Survey Saved', b: 'A clean success confirmation with the Survey ID.' }
  ];"""
    new_js = new_js[:cap_match.start()] + new_captions + new_js[cap_match.end():]

# Remove language selector listener
new_js = re.sub(r'// =+ LANGUAGE SELECTOR =+\s*const langSel = .*?\n\s*}\s*\n\s*\n\s*// =+ INIT =+\s*applyLang\(\);', '// ================= INIT =================', new_js, flags=re.DOTALL)

# Remove leftover L10N.xxx.xxx lines
new_js = re.sub(r'\n  L10N\.\w+\.\w+ = .*?;', '', new_js)

# Remove curLang
new_js = new_js.replace("let curLang = 'en';\n", "")
new_js = new_js.replace("try { curLang = localStorage.getItem('setu_lang') || 'en'; } catch (e) {}\n", "")

# Fix renderSavedList
new_js = new_js.replace(
    "  function renderSavedList() {\n    const box = document.getElementById('saved-list');\n    if (!box) return;\n    box.innerHTML = '';",
    "  function renderSavedList() { return;"
)

# Remove saved-list-card refs
new_js = re.sub(r"\n   
