---
url: https://thesgem.com/2025/01/sgem466-i-love-roc-n-rollbut-not-when-its-hacked/
title: "SGEM#466: I Love ROC-n-Roll…But Not When It’s Hacked"
date: 2025-01-25
audio_url: https://media.blubrry.com/thesgem/content.blubrry.com/thesgem/SGEM466a.mp3
download_date: 2025-08-11
summary: |
  The document discusses the potential for questionable research practices, specifically "AUC-hacking," in the development of clinical prediction models. It highlights the use of ROC curves and AUC as tools for evaluating diagnostic performance, noting that arbitrary thresholds for AUC values (e.g., 0.7, 0.8, 0.9) can incentivize data manipulation to achieve more favorable results. An observational study by White et al. analyzed 306,888 AUC values from PubMed abstracts and found irregular distributions suggesting data manipulation. The study emphasizes the need for greater transparency in research practices, including pre-registered protocols and data sharing, to prevent misleading clinical decision-making based on inflated AUC values. The findings underscore the importance of skepticism and critical evaluation of predictive models in medical literature.
---

**Reference:** White et al. Evidence of questionable research practices in clinical prediction models. BMC Med 2023

**Case:** You are working with a fourth-year medical student who is an avid listener to the Skeptics Guide to Emergency Medicine podcast. They recently listened to an episode examining a paper that used receiver operating characteristic curves or ROC curves to determine the accuracy of a predictive model by looking at the area under the curve or AUC. The student knows from other SGEM podcasts that there has been evidence of p-hacking in the medical literature and wonders if there have been similar instances with ROC curves. They ask you if there is any evidence of ‘ROC’ or ‘AUC-hacking?’

**Background:** To answer that young skeptic’s question, they must understand ROC curves. The ROC is a tool used to evaluate the diagnostic performance of a test or prediction model. The curve is graphed with the true positive rate (sensitivity) on the y-axis and the false positive rate (1-specificity) on the x-axis at various threshold levels for classifying a test result as positive or negative.

ROC curves help clinicians determine how well a test or model can differentiate between patients with and without a condition. A perfect test would have a point at the top-left corner of the graph (sensitivity = 1, specificity = 1).

The area under the curve (AUC) is often used to summarize a prediction model’s discriminatory capacity. A result of 1.0 indicates perfect discrimination, while an AUC of 0.5 suggests performance no better than chance—essentially, a coin toss. By comparing the ROC curves of different tests or models, clinicians can identify which performs better in discrimination.

Interpretation of the AUC often hinges on thresholds. Values of 0.7, 0.8, and 0.9 are commonly labelled as “fair,” “good,” or “excellent.” These descriptors, while convenient, are arbitrary and lack scientific foundation. Their widespread use introduces a strong temptation for researchers to achieve “better” AUC values.

This drive can lead to things like p-hacking, a questionable research practice in which investigators manipulate data or analyses to cross predefined thresholds. P-hacking is not exclusive to AUC but is a well-documented problem in broader research, particularly surrounding the 0.05 p-value significance threshold.

In the context of AUC, p-hacking might include selectively reporting favorable results, re-analyzing data multiple times, or even tweaking model parameters to inflate values. Such practices risk misleading clinicians and compromising patient care by promoting overly optimistic models.

Understanding the prevalence and mechanisms of AUC-related p-hacking is vital for emergency physicians who often rely on clinical prediction tools for critical decisions. As the use of these models grows, so does the importance of transparent and robust research practices.

**Clinical Question:** Is there evidence of questionable research practices, such as data manipulation or “hacking,” in studies developing clinical prediction models?

**Reference:** White et al. Evidence of questionable research practices in clinical prediction models. BMC Med 2023

- **Population:** PubMed abstracts that reported at least one AUC value related to clinical prediction models
  - **Excluded:** Abstracts with fewer than 10 words, pharmacokinetic studies using AUC for unrelated purposes, meta-analyses or pooled analyses, and tutorial papers lacking original findings
- **Exposure:** NA
- **Comparison:** No explicit comparison group was utilized, but the study benchmarked observed AUC distributions against expected smooth patterns.
- **Primary Outcome:** Evidence of irregular distributions, such as excess AUC values just above thresholds (e.g., 0.7, 0.8 or 0.9), that could suggest data manipulation.
- **Type of Study:** Observational study based on secondary data analysis.

**Authors’ Conclusions:** “The AUCs for some models are over-inflated, which risks exposing patients to sub-optimal clinical decision-making. Greater modeling transparency is needed, including published protocols, and data and code sharing.”

**Quality Checklist for Observational Study:**

1. Did the study address a clearly focused issue? Yes
2. Did the authors use an appropriate method to answer their question? Yes
3. Was the cohort recruited in an acceptable way? Yes
4. Was the exposure accurately measured to minimize bias? Yes
5. Was the outcome accurately measured to minimize bias? Yes
6. Have the authors identified all-important confounding factors? No
7. Was the follow up of subjects complete enough? Not applicable
8. How precise are the results? Very precise
9. Do you believe the results? Yes
10. Can the results be applied to the local population? Yes
11. Do the results of this study fit with other available evidence? Yes
12. Conflicts of interest and funding of the study? GSC was supported by Cancer Research UK and no COIs were declared.

**Results:** Their PubMed search identified 96,000 abstracts. Many abstracts reported multiple AUCs, often from competing models, which provide 306,888 AUC values.

**Key Result:** Irregular distribution of AUC values, particularly just above thresholds strongly suggests hacking.

**1) Abstract-Only Focus:** The authors’ decision to examine only abstracts rather than full texts can introduce several limitations that may affect the validity and generalizability of their findings. Abstracts are designed to provide a concise summary of the most important or favorable findings from the study. Researchers may highlight the best-performing AUC values in the abstract while leaving less favorable results in the full text. By the authors only examining abstracts, this study may have captured an incomplete and potentially skewed view of the reporting practices surrounding AUC values.

**2) Publication Bias:** This refers to the tendency for studies with statistically significant or favorable results to be more likely to be published than those with null or unfavorable findings. In this study, the authors identified patterns suggestive of “AUC-hacking,” but they did not fully explore how publication bias might contribute to these patterns. Journals, editors, and peer reviewers may favor studies reporting high AUC values (e.g., above 0.8) because they demonstrate stronger predictive accuracy. This preference could encourage researchers to selectively report higher AUC values, leaving less impressive results unpublished or underemphasized.

**3) Arbitrary Thresholds:** It is important to remember while the thresholds for AUC provide a useful framework for categorizing model performance, their arbitrary origins and lack of scientific justification highlight the need for caution when interpreting them. For example, one source might define 0.7 to 0.8 as “acceptable,” while another might call it “fair.” The lack of a universal definition or a theoretical rationale behind these thresholds underscores their subjective nature. The use of thresholds to stratify AUC can encourage AUC-hacking behavior. The thresholds also do not account for the context in which a clinical prediction model is being applied, such as the balance between sensitivity and specificity, the clinical consequences of false positives or false negatives, or the underlying prevalence of the condition being predicted.

**4) Clinical Decision-Making:** We should not be making clinical decisions on one summary statistic like a p-value, NNT, or the AUC. However, inflated AUC values may lead to overoptimistic assessments of model performance, potentially resulting in suboptimal clinical decisions and harming patient care. This includes misinformed clinical decisions, unnecessary or harmful interventions, and missed diagnoses.

**5) Do Better:** We must do better at all stages of research. This includes pre-registered protocols, detailed methodology, data sharing, code sharing, improving peer review and advocating for validation of clinical prediction models. We need to address the issue of AUC-hacking and improve the quality of research. There needs to be greater transparency of clinical prediction models.

**Comment on Authors’ Conclusion Compared to SGEM Conclusion:** We generally agree with the authors’ conclusions.

**SGEM Bottom Line:** AUC-hacking is likely occurring in the publication of clinical prediction models.

**Case Resolution:** Tell the student there is evidence of AUC-hacking, and we should do a didactic session on the topic next week to share with the other medical students.

**Clinical Application:** AUC-hacking represents another potential bias in the medical literature we should consider when evaluating a publication.

**What Do I Tell the Student?** Keep listening to the SGEM and be skeptical, even of studies reporting AUC.