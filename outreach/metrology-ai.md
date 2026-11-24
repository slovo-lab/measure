# Metrologists working on AI, software and data: who could find Measure useful

*Русская версия: [metrology-ai.ru.md](metrology-ai.ru.md)*

Written by Claude (AI) on 24 November 2026, at the lab owner's request. **First pass: 19 entries.**

How to read this list:

- It is a list for the lab's owner. Nobody on it has been contacted. Writing to anyone needs the owner's confirmation each time.
- Only public, professional information: organisation, group, role, published work. People are named only where the source itself names them in that role.
- Every entry rests on a source found by search on 24 November 2026. What was read is the search excerpt of each page, not the full page. Before anyone is written to, the page has to be read in full.
- Not found or not searched yet: INRIM beyond its role in Mathmet, VNIIM, KRISS, working group 1 of JCGM, ISO/IEC JTC 1/SC 42, CEN-CENELEC JTC 21.

## Circle 1. People who test measurement software against reference data

| Who | What they do | Why Measure could matter to them | Source |
|---|---|---|---|
| TraCIM, operated at PTB (Germany), with the association TraCIM e.V. | Online services that validate the results of calculations in metrological software against reference results; quality rules are set by the association. | Measure borrows their method and applies it to a kind of software they do not cover: calculators offered to AI agents. They can say where our use of the method is naive. | https://www.dmet.ptb.de/dme/tracim-services |
| The authors of the TraCIM papers: F. Härtig, B. Müller, K. Wendt, M. Franke (PTB), A. Forbes, I. Smith (NPL) | Described online validation of numerical algorithms in metrology (IMEKO, 2014 and 2015). | The same as above; also the paper "Approaches for assigning numerical uncertainty to reference data pairs for software validation" (2015) bears directly on our tolerances and has to be read. | https://imeko.org/proceedings/online-validation-of-metrological-software-using-the-tracim-system ; https://www.euramet.org/research-innovation/search-research-projects/details/project/traceability-for-computationally-intensive-metrology |
| EMN Mathmet, Quality Assurance Tools | A EURAMET expert document (version 1.0.0) with tools for assuring the quality of data, software and guidelines; authors include K. Lines, J.-L. Hippolyte, I. George and P. Harris (NPL). | Measure is a small piece of software and data that claims to be trustworthy. Their tool is a ready checklist to hold it against, and they ask for feedback. | https://euramet.org/european-metrology-networks/mathmet/activities/quality-assurance-tools |
| NPL (United Kingdom), Data Science, modelling and analytics | Says it builds on its work in software testing so that algorithms and software that process data can be shown to be trustworthy. | Closest national-institute group to the question "is the tool's answer right". | https://www.npl.co.uk/data-science/modelling-and-analytics |

## Circle 2. Authors of uncertainty calculators that metrologists use

| Who | What they do | Why Measure could matter to them | Source |
|---|---|---|---|
| NIST Uncertainty Machine: T. Lafarge, A. Possolo, D. Newton, A. Koepke (NIST, USA) | A web application that evaluates measurement uncertainty by the GUM method and by Monte Carlo. | Its authors publicly thank users who found an error in its engine, so reports are welcome there. Our pairs could be put to it by hand; it is not a server for agents. | https://uncertainty.nist.gov/about/about_English.md.html |
| METAS UncLib: developed by M. Wollensack (METAS, Switzerland) | A general library for measurement uncertainty, with a Python wrapper on the package index. Free to use; redistribution is prohibited by its licence. | Could be put through the bench as another library, if the licence allows running it in public tests; read the licence first. | https://www.metas.admin.ch/en/metas-unclib |
| GUM Tree Calculator: Measurement Standards Laboratory of New Zealand | A Python package for data processing with automatic uncertainty, open source (MIT), on the package index. | The easiest next adapter for the bench: open, installable, written by a national institute. No message is needed to do this. | https://github.com/MSLNZ/GTC |
| Suncal: Sandia National Laboratories (USA) | Software for uncertainty propagation by GUM and Monte Carlo, with the evaluation of Type A and Type B components; checks itself against case studies in the GUM and NIST TN 1900. | Another candidate for an adapter, and its authors already test against published examples. | https://www.osti.gov/pages/servlets/purl/1830511 |
| PTB Working Group 8.42 | Practical support in measurement uncertainty: training, seminars and software applications for GUM evaluations. | They teach people to use such calculators; a table of which calculators agree with references is teaching material. | https://www.ptb.de/cms/en/ptb/fachabteilungen/abt8/fb-84/ag-842/measurement-uncertainty-practical-perspective.html |

## Circle 3. Groups working on metrology for AI, machine learning and data

| Who | What they do | Why Measure could matter to them | Source |
|---|---|---|---|
| EMN Mathmet (EURAMET); chair F. Pennecchi (INRIM, Italy) | The European network for mathematics and statistics in metrology; its stated aim is trust in algorithms, software tools and data. Artificial intelligence is one of its themes; its research agenda was updated in June 2026. | Measure is a small worked case of exactly that aim, for tools given to AI agents. | https://www.euramet.org/european-metrology-networks/mathmet/strategy/strategic-agenda |
| NPL, Data Science and AI Department | Tools for the traceability of measurement information through AI systems; led the AI section of Mathmet's research agenda; one of three lead partners of the UK's AI Standards Hub. Its Centre for AI Measurement is asking for evidence on methods for testing AI systems. | An open call for evidence is a door: the day's findings (servers that do not start, answers given where none exists) are evidence of that kind. Check whether the call is still open. | https://www.npl.co.uk/research/data-science-and-ai/trustworthy-ai ; https://www.npl.co.uk/data-science |
| NPL authors T. Adel, S. Bilson, M. Levene, A. Thompson | "Trustworthy Artificial Intelligence in the Context of Metrology" (2024). | Background reading; shows how a national institute frames the subject. | https://arxiv.org/abs/2406.10117 |
| PTB | Published an AI strategy ("Metrology and AI", 2022); coordinated the European project QUMPHY on uncertainty for machine learning with medical signals (to June 2026), which aimed at standard benchmark datasets. | People there build benchmarks with a metrologist's care; they can judge ours. | https://oar.ptb.de/files/download/310.20220199.pdf ; https://www.qumphy.ptb.de/ |
| LNE (France), AI evaluation; department head A. Delaborde; N. Fischer on uncertainty for learning methods | Evaluates and certifies AI systems in its laboratory LEIA; says it has more than 15 years of experience in evaluating AI systems. | They evaluate AI systems for a living; agent tools are a part of such systems that is rarely evaluated on its own. | https://www.lne.fr/en/testing/evaluation-artificial-intelligence-systems ; https://www.academie-technologies.fr/wp-content/uploads/2024/03/metrologie_numerique_innovation_ST24_100124.pdf |
| NIST, Center for AI Standards and Innovation (USA) | Works on "AI measurement science"; drafted NIST AI 800-2, practices for automated benchmark evaluations of language models and agent systems (comments closed 31 March 2026). | That document describes how such evaluations should be done and reported. Read it and hold Measure's reports against it before the first monthly round. | https://www.nist.gov/blogs/caissi-research-blog/accelerating-ai-innovation-through-measurement-science |
| EURAMET, "Building Trustworthy AI for European Science" | An online consultation (15 September to 15 October 2026) on scientific needs for assessing AI; its results inform a European research call in 2027. | Shows where European metrology money for this subject will go in 2027. Closed now; watch for the call. | https://www.euramet.org/publications-media-centre/events/detail/event/building-trustworthy-ai-for-european-science-data-quality-uncertainty-quantification-and-standards |

## Circle 4. Committees, networks and meetings

| Who | What they do | Why Measure could matter to them | Source |
|---|---|---|---|
| CIPM Forum on Metrology and Digitalization; chair C. Denz (PTB) | Advises the CIPM on the SI Digital Framework: machine-readable units, values and uncertainties, including machine-actionable conversion between unit systems. | Measure tests unit conversion as agents actually receive it. The framework's reference services could become a source of reference answers. | https://www.bipm.org/committees/fo/forum-dig |
| CODATA group on digital representation of units of measurement | Called for machine-readable units (Hanisch and others, Nature, 2022). | The same subject from the data side; background reading. | https://codata.org/codata-isc-and-metrology-in-the-digital-era |
| IMEKO TC21, Mathematical Tools for Measurements | Runs the conference on advanced mathematical and computational tools in metrology; the 2026 meeting (Faro, 27 to 29 October) listed AI in measurement systems and trustworthiness among its themes. The IMEKO World Congress is in Rimini, 30 August to 3 September 2027, and paper submission is open. | The natural place for a short paper on Measure's method and first rounds. Check the deadline. | https://conferences.imeko.org/event/18/ ; https://imeko.org/secretariat |
| Centro Español de Metrología (Spain) | Has a digitalisation plan; with ENAC and UNE it is to support the Spanish AI strategy through the quality infrastructure; organises the 8th Spanish Metrology Congress. | The national institute of the country where the lab's owner lives; a contact in his own language. No group on AI was found in this search. | https://www.une.org/salainformaciondocumentos/NP_Reunion_Infraestructura_calidad_2025.pdf ; https://www.cem.es/sites/default/files/2022-03/Folleto%20Digitalizaci%C3%B3n.pdf |

## What follows from the list, in the lab's own hands

1. Add the GUM Tree Calculator to the bench. It needs no one's permission and gives the results table a tool that metrologists know.
2. Read three documents before the first monthly round: the 2015 paper on uncertainty of reference data pairs, Mathmet's quality tool for software, and NIST AI 800-2.
3. Check two dates: NPL's call for evidence and the paper deadline for the 2027 IMEKO World Congress.
