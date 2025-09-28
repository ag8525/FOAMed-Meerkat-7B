---
url: https://thesgem.com/2024/07/sgem448-more-than-a-feeling-gestalt-vs-cdt-for-predicting-sepsis/
title: "SGEM#448: More than A Feeling – Gestalt vs CDT for Predicting Sepsis"
date: 2024-07-27
audio_url: https://media.blubrry.com/thesgem/content.blubrry.com/thesgem/SGEM448.mp3
download_date: 2025-08-11
---
**Reference:** Knack et al. Early Physician Gestalt Versus Usual Screening Tools for the Prediction of Sepsis in Critically Ill Emergency Patients. [Ann Emerg Med 2024](https://pubmed.ncbi.nlm.nih.gov/38530675/)

**Date**: July 25, 2024

**Guest Skeptic:**Dr. Justin Morgenstern is an emergency physician and the creator of the #FOAMed project called [www.First10EM.com](http://www.first10em.com/)

**Case:** Your hospital is running Morbidity and Mortality (M&M) rounds after a few recent cases in which the diagnosis of sepsis was identified late, and antibiotics were delayed. They are planning on instituting a mandatory screening tool at triage, and one of the main purposes of the meeting is to compare the available tools, such as qSOFA and MEWS. As the local evidence-based medicine (EBM) nerd, they ask for your opinion on the evidence.

**Background:** Sepsis is a life-threatening organ dysfunction caused by a dysregulated host response to infection. It is a medical emergency that requires prompt recognition and treatment to improve patient outcomes.We have covered the topic of sepsis many times on the SGEM ([SGEM#69](http://thesgem.com/2014/04/sgem69-cry-me-a-river-early-goal-directed-therapy-process-trial/), SGEM#90, [SGEM#92](https://thesgem.com/2014/10/sgem92-arise-up-arise-up-egdt-vs-usual-care-for-sepsis/), [SGEM#113](http://thesgem.com/2015/03/sgem113-egdt-promises-promises/), SGEM#168, [SGEM#174](http://thesgem.com/2017/04/sgem174-dont-believe-the-hype-vitamin-c-cocktail-for-sepsis/), SGEM Xtra, SGEM#346, SGEM#371 and [SGEM Peds Xtra](https://thesgem.com/2023/11/sgem-xtra-say-what-you-need-to-say-but-dont-say-sepsis-screening/)).

There is a lot of emphasis on identifying sepsis early, with the idea that early intervention will save lives. However, despite a strong push for early antibiotics, the evidence of benefit is mostly lacking. There is observational data that is widely cited to suggest that early completion of sepsis bundles improves outcomes but considering that physicians don’t purposefully delay antibiotics in patients with known sepsis, this data is severely limited by multiple confounders [1].

![](https://i0.wp.com/thesgem.com/wp-content/uploads/2018/02/Paramedics.jpg?resize=300%2C200&ssl=1)A randomized control trial (RCT) done in the prehospital setting enrolled 2,698 patients. They were randomized to ceftriaxone 2gm intravenous (IV) in the ambulance or usual cares (fluids and supplementary oxygen) until arrive to the ED. The primary outcome reported was no statistical difference in mortality at 28 days (8% in both groups) despite giving antibiotics 96 minutes earlier [2]. All of the secondary outcomes (mortality at 90 days, misdiagnoses, hospital length of stay, ICU admission rate, ICU length of stay, and quality of life) also did not show a statistical difference between the intervention group and the control group ([SGEM#207](https://thesgem.com/2018/02/sgem207-ahh-dont-push-it-pre-hospital-iv-antibiotics-for-sepsis/)).

Thus, early identification of sepsis might not be as important as sometimes stated in guidelines. However, getting the right diagnosis is clearly important for our patients, and as good as we are, no clinician is perfect. Acknowledging our imperfections, many have suggested that screening tools or decision tools might help increase accuracy when screening for sepsis. Many such tools exist, such as the Systemic Inflammatory Response Syndrome ([SIRS](https://www.mdcalc.com/calc/1096/sirs-sepsis-septic-shock-criteria)), Sequential Organ Failure Assessment ([SOFA](https://www.mdcalc.com/calc/691/sequential-organ-failure-assessment-sofa-score)), quick SOFA ([qSOFA](https://www.mdcalc.com/calc/2654/qsofa-quick-sofa-score-sepsis)) and theModified Early Warning ([MEWS](https://www.mdcalc.com/calc/1875/modified-early-warning-score-mews-clinical-deterioration)) score.

Unfortunately, the enthusiasm for decision instruments often outstrips the evidence. For a decision instrument to benefit patients, it needs to have more than a high sensitivity. It needs to change physician practice for the better. It needs to be better than current clinical practice, or just plain clinical judgement. There is an article published in AEM, with an author list that includes the who’s who of decision rules – from Jeff Kline to Nathan Kupperman to my BFF Chris Carpenter. That document tells us *“Before widespread implementation, CDRs should be compared to clinical judgement.”* [3]

Unfortunately, most of our rules haven’t cleared this basic evidentiary hurdle. Dave Schriger and colleagues reviewed publications in the Annals of Emergency Medicine from 1998 to 2015 and found that only 11% of the studies compared decision aids to clinical judgement [4]. In those that did compare to clinical judgement, physician judgement was superior in 29% and equivalent or mixed in 46%. The decision aid only outperformed clinical judgement in 10% of papers (or two total trials). A similar review by Sanders et al 2015 concludes that clinical decision rules *“are rarely superior to clinical judgement and there is generally a trade-off between the proportion classified as not having disease and the proportion of missed diagnoses.”* [5]

Therefore, before widespread use of sepsis tools like qSOFA or the MEWS score, we really need to see comparisons to clinical judgment. That brings us to the current study, which aims at comparing a number of these tools to initial clinical judgment in the emergency department.

---

### **Clinical Question: What is the accuracy of standardized screening tools and a machine learning model to predict a hospital discharge diagnosis of sepsis, compared with physician gestalt in the hyperacute period immediately after patient presentation among undifferentiated patients with critical illness in the emergency department (ED)?**

---

**Reference:**  Knack et al. Early Physician Gestalt Versus Usual Screening Tools for the Prediction of Sepsis in Critically Ill Emergency Patients. [Ann Emerg Med 2024](https://pubmed.ncbi.nlm.nih.gov/38530675/)

* **Population:** Critically ill, adult (18 and older), undifferentiated medical patients presenting to the specialized four bed resuscitation area in this emergency department.
  + **Excluded:** Patients with trauma, and obvious causes of illness, defined as cardiac arrest, STEMI, suspected stroke, and patients in active labour. They also excluded patients being transferred from outside facilities.
* **Intervention:** Faculty emergency physicians were asked *“what is the likelihood that this patient has sepsis?”*and asked to rate the likelihood on a scale from 0 to 100. They were asked 15 and 60 minutes after the patient’s presentation.
  + To calculate statistics, they decided anything above 50% was consistent with the diagnosis of sepsis, but it is not clear that is a good assumption, which we will discuss below.
* **Comparison:** The physician gestalt was compared to SIRS, SOFA, qSOFA, MEWS, and a logistic regression machine learning model using Least Absolute Shrinkage and Selection Operator (LASSO) for variable selection.
* **Outcome:** A final diagnosis of sepsis, based on ICD 10 codes at discharge.
* **Type of Study:** This is a single center prospective observational trial.

> **Authors’ Conclusions:** *“**Among adults presenting to an ED with an undifferentiated critical illness, physician gestalt in the first 15 minutes of* *the encounter outperformed other screening methods in identifying sepsis”.*

**![](https://i0.wp.com/thesgem.com/wp-content/uploads/2014/04/checklist-cartoon.gif?resize=150%2C150&ssl=1)Quality Checklist for** **Observational Study:**

1. Did the study address a clearly focused issue? Yes
2. Did the authors use an appropriate method to answer their question? Yes
3. Was the cohort recruited in an acceptable way? Yes
4. Was the exposure accurately measured to minimize bias? No
5. Was the outcome accurately measured to minimize bias? No
6. Have the authors identified all-important confounding factors? **Unsure**
7. Was the follow up of subjects complete enough? Yes
8. How precise are the results? The confidence intervals are tight enough to believe
9. Do you believe the results? Yes
10. Can the results be applied to the local population? **Unsure**
11. Do the results of this study fit with other available evidence? Yes
12. Funding of the Study: The authors did not report any specific funding sources and declared no conflicts of interest.

**Results:** They included 2,484 patients, with a median age of 53, 60% being male and 11% (257/2,484) were ultimately diagnosed with sepsis. Most physician judgment (94%) was completed by physicians with only 6% being completed by residents. They were missing a lot of data for the other screening tools. The median visual analog scale (VAS) score in patients with sepsis was 81, as compared to 8 in those without sepsis.

---

### **Key Result: Physician gestalt was better than all the decision tools, both at 15 and 60 minutes.**

---

* **Primary Outcome:** Sepsis diagnosis

**![](https://i0.wp.com/thesgem.com/wp-content/uploads/2024/07/448-table.png?resize=936%2C330&ssl=1)**

![](https://i0.wp.com/thesgem.com/wp-content/uploads/2015/04/Screen-Shot-2015-04-25-at-3.11.12-PM.png?resize=889%2C162&ssl=1)

**1. Lack of Gold Standard:** What is the true definition of sepsis, and do we even have a gold standard? In this study, the (fool’s) gold standard was the chart containing an ICD 10 code of sepsis at the time of discharge. But how many of these patients truly had sepsis? More importantly, not all sepsis is created equal. I might care a lot about identifying septic shock or severe sepsis, but if these patients fell out of those more severe categories, do we even care? Finally, discharge diagnosis it a poor gold standard, because it is possible that patients could have developed sepsis later in their hospital stay. Imagine a patient with intestinal ischemic as the cause of their initial presentation. Even if that patient later develops sepsis, we have done the patient no good by labelling them sepsis in the ED and missing their dying intestines.

In fact, they provide us with a table of the 10 patients who were ultimately diagnosed with sepsis but “*missed*” by the initial clinician. The exact case I invented, a patient with intestinal ischemia and zero SIRS criteria, is represented as a miss. Perhaps most importantly, antibiotics were given in the ED to every single ‘miss’, which really makes you wonder about the definition of ‘missed sepsis’ being used.

**2. VAS Score:** They asked physicians to rate the chances of sepsis from 0 to 100. That is a reasonable question for research purposes, but it is entirely unclear what these numbers mean for clinical care. If a patient has a 60% chance of sepsis, do you empirically treat as sepsis, or wait for more information? 40%? 20%? It is likely that different clinicians will act at different thresholds. For their stats, they decided that anything above 50% meant the patient had sepsis, but they didn’t ask the clinicians for their interpretation. Would the treating physicians have agreed? It is possible that they were giving empiric antibiotics to patients with even a 20% chance of sepsis, which would make the 50% cutoff meaningless. Therefore, although this is a theoretically interesting question, a much more important question is how gestalt compares to rules in terms of clinical actions. In other words, the question we want answered is *“based on your gestalt, are you going to empirically treat as if this is sepsis?”*, whatever the risk threshold is.

**3. Generalizability:** This study only looked at critically ill patients. As I think this study demonstrates, we are very good at identifying and treating sepsis in patients who look like they need the ICU when they arrive in the ED. The more difficult group of patients are those who present atypically but get much sicker in the 24 hours after their initial examination. It is possible, but obviously completely unproven, that objective tools or artificial intelligence could help identify risk factors clinicians are overlooking in these harder to diagnose patients.

This hospital also functions unlikely most of our EDs. Lab results were reported on these patients in less than 15 minutes from arrival. These clinicians had more data points going into their judgement than most of us would have. That being said, the scores all need lots of data points, and even in this data rich environment, most of these patients could have their sepsis scores calculated.

**4. Hawthorne Effect**: These clinicians were specifically being asked about sepsis. The simple act of asking might influence their estimates. For example, you might have left the room of a patient in shock, with a working diagnosis of pulmonary embolism (PE), but when asked about sepsis realize that It should be on the differential, upgrade your judgement, and add antibiotics. If the research assistants weren’t present, it is possible that clinicians could have missed more cases. The decision tools would not suffer from this same bias.

Another potential bias is a straw-person decision rule comparison. The authors mention it in their limitations, but the comparison to SIRS or SOFA is somewhat nonsensical, because those scores don’t diagnose sepsis. A diagnosis of sepsis requires a positive SIRS or SOFA score plus a clinical diagnosis of infection. In other words, the definition of sepsis always relies on clinical judgment (no matter what bean counters looking at data retrospectively want to say). Therefore, these tools probably function better in clinical practice, where they are combined with clinical judgment, than they did in this study, making it false comparison.

**5. Decision Tools Calculated Retrospectively:** There are major questions about the accuracy of the decision tool results, given that the scores were only calculated retrospectively based on chart review. Very few patients had enough data record to completely these scores. At 15 minutes, although 100% of patients had enough information for a qSOFA, only 59% could have a MEWS calculated, 7% for SIRS, and 2% for the full SOFA score. The numbers remained similarly slow by 1 hour.

A more philosophical question would be why are we so obsessed with decision tools? There has been an absolute explosion in the number of decision tools available in emergency medicine in the last two decades, but as is demonstrated in this study, almost none of them outperform basic clinical judgement. This is one of the reasons I wrote a provocative blog post called “[Clinical Decision Rules are Ruining Medicine](https://first10em.com/clinical-decision-rules/)”.

**Comment on Authors’ Conclusion Compared to SGEM Conclusion:** Although there are some limitations that limit our certainty, we agree with the conclusion that physician judgement appears to outperform the available screening tools in the early identification of sepsis in critically ill patients.

---

### **SGEM Bottom Line: Despite the many limitations of the human mind, we should not underestimate the accuracy of physician judgement. We are highly trained and run algorithms that are likely more complex than the average decision tool. For the diagnosis of sepsis, you are going to have to rely on your training, rather than any specific decision tool.**

---

**Case Resolution:**  As the EBM nerd in the group, you talk the hospital administration off the cliff, explaining the problems with using the ‘retrospective-scope’ to shape patient care, and discussing the many limitations of the available screening tools. Thanks to this new publication, you are able to emphasize the accuracy physician judgement, and so instead of forcing already over-burdened triage nurses from completing sepsis screening tools, you just empower them to call the physician to the bedside for any patient they are worried about.

![](https://i0.wp.com/thesgem.com/wp-content/uploads/2019/01/Justin-Morgenstern-e1547853552685-150x150.jpg?resize=150%2C150&ssl=1)

Dr. Justin Morgenstern

**Clinical Application:** Physician judgement is our best tool for early identification of sepsis.

**What Do I Tell My Patient?**  These critically ill patients usually aren’t that interested in how we make the diagnosis, as long as we get the diagnosis correct. I will tell them that based on my judgement, I think that an infection is the most likely cause of their illness, but that it is also important to keep one’s mind open, and that I will be reassessing them frequently to ensure they are improving.

**Keener Kontest**: Last week’s winner was Corey Hazekamp. He knew French obstetrician François Chaussier is credited with introducing the bag-valve mask device in 1780 for the resuscitation of neonates.

Listen to the podcast to hear this week’s keener contest question. Email your answer to [TheSGEM@gmail.com](mailto:TheSGEM@gmail.com) with “*Keener*” in the subject line. The first correct answer will get a shout out on the SGEM next episode.

---

### **Remember to be skeptical of anything you learn, even if you heard it on the Skeptics’ Guide to Emergency Medicine.**

---

**References:**

1. Seymour CW, Gesten F, Prescott HC, Friedrich ME, Iwashyna TJ, Phillips GS, Lemeshow S, Osborn T, Terry KM, Levy MM. Time to Treatment and Mortality during Mandated Emergency Care for Sepsis. N Engl J Med. 2017 Jun 8;376(23):2235-2244. doi: 10.1056/NEJMoa1703058. Epub 2017 May 21. PMID: 28528569; PMCID: PMC5538258.
2. Alam N, Oskam E, Stassen PM, Exter PV, van de Ven PM, Haak HR, Holleman F, Zanten AV, Leeuwen-Nguyen HV, Bon V, Duineveld BAM, Nannan Panday RS, Kramer MHH, Nanayakkara PWB; PHANTASi Trial Investigators and the ORCA (Onderzoeks Consortium Acute Geneeskunde) Research Consortium the Netherlands. Prehospital antibiotics in the ambulance for sepsis: a multicentre, open label, randomised trial. Lancet Respir Med. 2018 Jan;6(1):40-50. doi: 10.1016/S2213-2600(17)30469-1. Epub 2017 Nov 28. PMID: 29196046.
3. Finnerty NM, Rodriguez RM, Carpenter CR, Sun BC, Theyyunni N, Ohle R, Dodd KW, Schoenfeld EM, Elm KD, Kline JA, Holmes JF, Kuppermann N. Clinical Decision Rules for Diagnostic Imaging in the Emergency Department: A Research Agenda. Acad Emerg Med. 2015 Dec;22(12):1406-16. doi: 10.1111/acem.12828. Epub 2015 Nov 14. PMID: 26567885.
4. Schriger DL, Elder JW, Cooper RJ. Structured Clinical Decision Aids Are Seldom Compared With Subjective Physician Judgment, and Are Seldom Superior. Ann Emerg Med. 2017 Sep;70(3):338-344.e3. doi: 10.1016/j.annemergmed.2016.12.004. Epub 2017 Feb 24. PMID: 28238497.
5. Sanders S, Doust J, Glasziou P. A systematic review of studies comparing diagnostic clinical prediction rules with clinical judgment. PLoS One. 2015 Jun 3;10(6):e0128233. doi: 10.1371/journal.pone.0128233. PMID: 26039538; PMCID: PMC4454557.