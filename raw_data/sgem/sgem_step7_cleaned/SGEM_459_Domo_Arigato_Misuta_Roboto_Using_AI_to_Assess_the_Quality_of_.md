---
url: https://thesgem.com/2024/11/sgem459-domo-arigato-misuta-roboto-using-ai-to-assess-the-quality-of-the-medical-literature/
title: "SGEM#459: Domo Arigato Misuta Roboto – Using AI to Assess the Quality of the Medical Literature"
date: 2024-11-09
audio_url: https://media.blubrry.com/thesgem/content.blubrry.com/thesgem/SGEM_459.mp3
download_date: 2025-08-11
---
**Case:** The Mayo Clinic Department of Emergency Medicine is planning its next journal club. It has recently been boosted by adding Dr. Chris Carpenter to the faculty who created the amazing JC at Washington University. A resident has been assigned to report on the PRISMA quality checklist for the SRMA they will discuss. She has been playing around with ChatGPT 3.5 from OpenAI and wonders if it could do this task quickly and, more importantly, accurately.

**Background:** In recent years, large language models (LLMs), such as GPT-4 and Claude, have shown remarkable potential in automating and improving various aspects of medical research. One intriguing area of exploration is their ability to assist in critical appraisal, a cornerstone of evidence-based medicine (EBM). Critical appraisal involves evaluating the quality, validity, and applicability of studies using structured tools like PRISMA, AMSTAR, and PRECIS-2. 
- **PRISMA (Preferred Reporting Items for Systematic Reviews and Meta-Analyses):** This is a set of guidelines designed to help authors improve the reporting of systematic reviews and meta-analyses. It includes a checklist of 27 items that focus on the transparency and completeness of the review process, such as the identification, screening, and inclusion of studies, the synthesis of results, and how potential biases are addressed.
- **AMSTAR (A Measurement Tool to Assess Systematic Reviews):** This is a tool used to evaluate the methodological quality of systematic reviews of healthcare interventions. It consists of a checklist of 11 items that assess the robustness of a systematic review’s design and execution. The tool covers key areas like the use of comprehensive search strategies, inclusion criteria, methods for assessing the risk of bias, and the appropriateness of data synthesis.
- **PRECIS-2 (Pragmatic-Explanatory Continuum Indicator Summary):** This is an assessment tool used to evaluate how “pragmatic” or “explanatory” a randomized controlled trial (RCT) is. It is designed to help researchers design trials that better align with their research goals, whether they aim to inform real-world clinical practice (pragmatic) or control for as many variables as possible to test an intervention under ideal conditions (explanatory). The tool uses nine domains (e.g., eligibility criteria, recruitment, primary outcome, etc.) to rate how closely the trial conditions resemble real-world clinical settings.
Traditionally, these tasks have been manual, often requiring significant expertise and time to ensure accuracy. However, as LLMs have evolved, their ability to interpret and analyze complex textual data presents a unique opportunity to enhance the efficiency of these appraisals. Research into the accuracy of LLMs, when used for appraising clinical trials and systematic reviews, is still in its early stages but holds promise for the future of automated medical literature assessment. Given that assessing the validity and quality of clinical research is essential for ensuring that decisions are based on reliable evidence, this development raises important questions. Can these advanced AI tools perform critical appraisals with the same accuracy and reliability as human experts? More importantly, how can they augment human decision-making in medical research?

**Clinical Question:** Can large language models accurately assess critical appraisal tools when evaluating systematic reviews and randomized controlled trials?

**Reference:** Woelfle T et al. Benchmarking Human–AI collaboration for common evidence appraisal tools. J Clin Epi Sept 202400289-0/fulltext).

- **Population:** Systematic reviews and RCTs that were evaluated by critical appraisal tools (PRISMA, AMSTAR, and PRECIS-2).
- **Intervention:** Five different LLMs (Claude-3-Opus, Claude-2, GPT-4, GPT-3.5, Mixtral-8x22B) assessing these studies.
- **Comparison:** Comparisons were made against individual human raters, human consensus ratings, and human-AI collaboration.
- **Outcome:** Accuracy, and identification of potential areas for improving efficiency via human-AI collaboration.

**Authors’ Conclusions:** "Current LLMs alone appraised evidence worse than humans. Human-AI collaboration may reduce workload for the second human rater for the assessment of reporting (PRISMA) and methodological rigor (AMSTAR) but not for complex tasks such as PRECIS-2.”

**Results:** They assessed 112 SRMAs and 56 RCTs. Humans performed the best, reporting the highest accuracy for all three assessment tools. Of the LLMs, Claude-3-Opus consistently performed the best across PRISMA and AMSTAR, indicating that it may be the most reliable LLM for these tasks.
GPT-3.5, despite being an older and smaller model, performed better than newer LLMs like GPT-4 and Claude-3-Opus on the more complex PRECIS-2 tasks.
The collaborative human-AI approach yielded superior performance compared to individual LLMs, with accuracies reaching 96% for PRISMA and 95% for AMSTAR when humans and LLMs worked together.
**Key Results:** Large language models alone performed worse than humans while a collaborative approach between humans and LLMs showed potential for reducing the workload for human raters by identifying high-certainty ratings, especially for PRISMA and AMSTAR.

**Commentary:**  
**1. Bias in Training Data and Prompts:** LLMs rely on the data they were trained on, which may introduce unseen biases. In addition, the behavior of the model is impacted by the information it was fed (prompts). As an example, when the LLMs were required to pull relevant quotes, they did not follow the instructions, often pulling too many or pulling quotes from analyses they had already performed rather than the source material.

**2. Limited Contextual Understanding by LLMs:** LLMs may lack the nuanced judgment needed for assessing methodological quality in complex trials. This was illustrated by LLMs having a low accuracy while the addition of a human rater increased the accuracy. LLMs still don’t process in the same way as humans, but when we are the gold standard is that something we want to match or is there a benefit to re-evaluating our responses after the LLM goes through to see if we are making errors? The authors identify a prospective evaluation as a potential next step in understanding how LLMs perform and how to improve assessments.

**3. Lack of Transparency in LLM Decision Processes:** Transparency in decision-making LLMs presents significant challenges. A key issue is the “black box” nature of these systems. This often makes it difficult to explain how they reach their decisions even to experts. LLMs can generate sophisticated outputs from simple prompts but, the underlying reasons are opaque. AI often misunderstands or simplifies tasks, creating outputs that are sometimes unpredictable and difficult to interpret, further complicating transparency. This raises concerns about trust in the LLMs results.

**4. Cost, Time, and Financial:** When the bandwidth is throttled (only so many times you can use it per day and limits on the length of the paper that can be evaluated) and the cost gets high ($115) this limits the utility – and cost/time are balanced with quality with the newer models being costly and the older being less expensive but throttled.

**5. Newer Appraisal Tools:** The last few years have seen a dramatic acceleration in the development of LLMs, transforming them from experimental tools into mainstream applications. This rapid improvement is primarily driven by advances in neural networks, scaling in model size, and more sophisticated training techniques. LLMs like ChatGPT have achieved unprecedented adoption rates, reaching millions of users within months of release due to their versatility and effectiveness in a wide variety of tasks. They can now perform more complex problem-solving capabilities, demonstrating learning abilities that were unthinkable just a few years ago. It is reasonable to expect LLMs to continue to improve and become more accurate in assessing critical appraisal tools.

**Comment on Authors’ Conclusion Compared to SGEM Conclusion:** We generally agree with the authors’ conclusions.

**SGEM Bottom Line:** Large language models alone are not reliable enough to replace human raters for complex evidence appraisals. However, the human-AI collaboration strategy shows promise, especially for simpler tasks like PRISMA and AMSTAR, by reducing the workload for human raters without sacrificing accuracy.

**Case Resolution:** You ask the resident for a tutorial on LLMs and use it to evaluate the SRMA adherence to the PRISMA guidelines. That way you will learn how to use some AI for critical appraisal while ensuring the program’s output is accurate based on your expertise.

**Clinical Application:** LLMs for critical appraisal are interesting but not ready for prime time.

**What Do I Tell the Resident?** Hey, using AI for critical appraisal sounds like a cool idea. I don’t know much about LLMs. Can we do the evaluation together? I would like to learn more about this new technology and ensure it provides the right information for our journal club.