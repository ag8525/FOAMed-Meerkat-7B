# ------ MODEL PROMPTS ------
BASE_PROMPT = (
    "The following is a multiple-choice question about medical knowledge. "
    "Solve this in a step-by-step fashion, starting by summarizing the available information. "
    "Output a single option from the given options as the final answer. "
    "You are strongly required to follow the specified output format; conclude your response with the phrase "
    "\"the answer is ([option_id]) [answer_string]\".\n\n"
)

RAG_PROMPT = (
    "The following is a multiple-choice question about medical knowledge. "
    "Solve this in a step-by-step fashion, starting by summarizing the available information. "
    "You are given \"retrieved context\"; treat it as optional evidence. "
    "Use retrieved text only if it is clearly relevant and helpful to answering the question. "
    "If all retrieved chunks are irrelevant, ignore them and rely on your own medical knowledge. "
    "Output a single option from the given options as the final answer. "
    "You are strongly required to follow the specified output format; conclude your response with the phrase "
    "\"the answer is ([option_id]) [answer_string]\".\n\n"
)

STEPBACK_PROMPT = (
    "You are an expert medical educator and clinician. Your task is to rephrase a specific, "
    "patient-focused clinical question into 1-3 general, principle-based questions. "
    "These new questions must be ideal for retrieving a foundational medical text that would "
    "help a student to answer the original question."
    "\n\n"
    "Follow these strict output rules:\n"
    "- DO NOT include reasoning, explanations, greetings, or any other conversational text.\n"
    "- DO NOT copy the answer options or restate the original question.\n"
    "- Each step-back question MUST include at least one explicit medical anchor term (condition/pathology/syndrome OR leading differential), e.g., 'acute pericarditis,' 'acute coronary syndrome,' 'porcelain gallbladder.'\n"
    "- Each step-back question MUST include one task keyword: one of {diagnosis, pathophysiology, initial management, risk stratification, imaging, pharmacology, complications, prognosis}.\n"
    "- NO vague expressions like 'this patient', 'this condition', 'these symptoms'.\n"
    "- Each generated question MUST be 25 words or less.\n"
    "- EXCLUDE ALL specific patient details (age, gender, specific lab values, etc.)."
    "- You are strongly required to ONLY output the step-back questions using the following format "
    "\"(1) [step-back question 1]\n(2) [step-back question 2]\n(3) [step-back question 3]\".\n\n"

)

# ------ FEW-SHOT EXAMPLES FOR STEP-BACK PROMPTING ------

FEW_SHOT_EXAMPLES = [
     {
        "specific": """A 43-year-old man comes to the emergency department with nausea, abdominal discomfort, diarrhea, and progressive perioral numbness for the past 24 hours. 3 days ago, he underwent a total thyroidectomy for treatment of papillary thyroid cancer. His only medication is a multivitamin supplement. He appears fatigued. While measuring the patient's blood pressure, the nurse observes a spasm in the patient's hand. Physical examination shows a well-healing surgical wound on the neck. Which of the following ECG findings are most likely in this patient?\n\nOptions:\nA: Torsade de pointes\nB: QT prolongation\nC: U waves\nD: Peaked T waves\nE: PR prolongation""",
        "step_back": "(1) What complications occur after thyroidectomy that can also affect the ECG?\n(2) What electrolyte abnormalities are seen post-thyroidectomy?\n (3) Which electrolyte abnormalities cause QT prolongation versus peaked T waves or U waves on ECG?"
    },
    {
        "specific": """Two hours after undergoing open cholecystectomy for complicated cholecystitis, a 48-year-old woman develops dizziness, lethargy, abdominal pain, and nausea. She has systemic lupus erythematosus and hypertension. Prior to hospitalization, her medications included nifedipine and prednisolone. Her pulse is 112/min and blood pressure is 90/64 mm Hg. Examination shows central obesity. The abdomen is soft and non-tender, and the laparoscopic incisions have no discharge. Her serum cortisol and serum ACTH are decreased. Which of the following additional findings is most likely in this patient?\n\nOptions:\nA: Normal anion gap metabolic acidosis\nB: Hyperkalemia\nC: Hyperglycemia\nD: Hypernatremia\nE: Hyponatremia""",
        "step_back": "(1) What type of post-operative adrenal disorder is characterized by decreased serum cortisol and ACTH levels?\n(2) What electrolyte and glucose abnormalities characterize secondary adrenal insufficiency?"
    },
    {
        "specific": """A 24-year-old female presents to the emergency department with a chief complaint of an inability to urinate. She states that this has been one of many symptoms she has experienced lately. At times she has had trouble speaking and has noticed changes in her vision however these episodes occurred over a month ago and have resolved since then. Two days ago she experienced extreme pain in her face that was exacerbated with brushing her teeth and plucking out facial hairs. The patient has no relevant past medical history, however, the patient admits to being sexually abused by her boyfriend for the past year. Her current medications include ibuprofen for menstrual cramps. On physical exam it is noted that leftward gaze results in only the ipsilateral eye gazing leftward. The patient's initial workup is started in the emergency department. Her vital signs are within normal limits and you note a pale and frightened young lady awaiting further care. Which of the following is the best initial test for this patient's chief complaint?\n\nOptions:\nA: Head CT\nB: Head MRI\nC: Lumbar puncture\nD: Post void residual volumes\nE: Domestic abuse screening and exploring patient's life stressors""",
        "step_back": "(1) How does multiple sclerosis-related neurogenic bladder present?\n(2) In a patient with urinary retention, intermittent speech and vision issues, facial pain, and abducens (CN6)nerve palsy, where is the lesion?\n(3) Which initial test is recommended in the emergency department for multiple neurologic deficits that cannot be localized?"
    }
]
