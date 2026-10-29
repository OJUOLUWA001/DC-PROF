
license: mit
title: Dc-Prof
sdk: docker
emoji: 🐢
colorFrom: green
colorTo: green
DC_Prof
A free AI study buddy that explains the basics of Engineering, Science, Arts, Law and Education in simple words, for students and for anyone thinking about venturing into one of these fields.

Team Eco-Friendly · OPEN//BUILD 2026 (OSCA Ile-Ife Hacktoberfest) · Theme: AI belongs to everyone

The problem
Choosing a field, or getting through the first year of one, is hard when there is nobody to ask.

Someone deciding between Engineering, Law, Science, Arts or Education rarely gets a simple, honest first look at what the field actually involves.
First- and second-year students get stuck on basic ideas, such as Ohm's law, osmosis, negligence or Piaget's stages, and can't always reach a lecturer or tutor.
Most AI tools need good internet, data or a paid plan, and they are not built around Nigerian examples, laws or institutions.
Who it is for
Who	Situation
Secondary-school leavers and UTME candidates	Want to understand a field before choosing a course
First- and second-year university students	Stuck on a basic concept and need a clear explanation
Career-changers and curious learners	Want to venture into a new field and need the fundamentals first
What it does
The user picks a faculty, asks a basic question, and DC_Prof answers in a fixed teaching format:

a simple explanation,
the key formula, rule or term, with each part explained,
one everyday example from Nigerian life (markets, okada, generators, school, farming, football),
a worked calculation when one applies,
one short quiz question to check understanding.
If it is not sure, it says so and points the user to a textbook or a lecturer.

Faculty	What it covers
Engineering	Aerospace (forces of flight, lift and drag, rockets, orbits), mechanical (stress and strain, torque, energy, thermodynamics), electrical and computer (Ohm's law, Kirchhoff's laws, AC and DC, logic gates)
Science	Physics basics, chemistry (atoms, bonding, acids and bases, the mole), biology (cells, photosynthesis, osmosis, genetics), maths (quadratics, differentiation, trigonometry, statistics)
Arts	Grammar and essay writing, literary terms, Nigerian and African literature and history, philosophy, logic, linguistics
Law	Nigerian Constitution and fundamental rights, sources of law, courts, contract, negligence, criminal law basics, the Land Use Act, becoming a lawyer
Education	Learning theories, Bloom's taxonomy, lesson planning, assessment, classroom management, the Nigerian education system
Demo
Demo video: <link> Live app: https://-Dc-prof.hf.space

It is hosted on a free Hugging Face Space, so the first load may take a minute while it wakes up. It also runs on an ordinary laptop, and the steps are in Run it yourself

Model
Model	SmolLM2-360M-Instruct by HuggingFaceTB
File used	SmolLM2-360M-Instruct-Q4_K_M.gguf (4-bit, quantised by bartowski)
Licence	Apache-2.0 (checked on the model card)
Why we chose it	It is tiny (360M parameters), so it downloads in minutes and runs on a laptop CPU with no GPU or API key. It is tuned for chat, and its licence allows reuse.
Its role	The tutor. It turns the question, the chosen faculty and the matching reference notes into a structured explanation, streamed word by word.
Limitations
It can be wrong. The model card warns that its output may be inaccurate and should be treated as assistive, not definitive. Always double-check before using an answer in an assignment or exam.
It is weak at arithmetic and multi-step reasoning, as small models usually are. Check every calculation.
English only in practice. Pidgin, Yoruba, Hausa and Igbo are not supported yet.
Limited coverage. There are 110 short reference notes. Questions outside them rely on the model alone and are less reliable.
The notes were written quickly and may contain mistakes, especially Nigerian laws, dates and figures. They should be checked against textbooks and official sources.
Law answers are study information, not legal advice.
Short memory. Only the last three exchanges are kept.
Speed depends on the computer. On a slow CPU, answers take a few seconds to start.
How it works
User picks a faculty and asks a question
              │
              ▼
   respond() finds the best-matching reference notes for that faculty
              │
              ▼
   builds the prompt: teaching rules + faculty topics + faculty safety rule
                      + matching notes + last 3 exchanges + the question
              │
              ▼
   llama.cpp runs SmolLM2-360M on the CPU, and the answer streams into the Gradio chat
Design choice	Why
Small open-weight model on CPU	Anyone with a basic laptop can run it, with no GPU, API key or cost.
Reference notes added to the prompt	A 360M model often guesses. Giving it checked facts for the question improves accuracy. This is a light form of retrieval-augmented generation.
Keyword matching, not embeddings	No second model and no extra RAM. It is easy to read, test and extend.
A rule for each faculty	No dangerous instructions in Engineering and Science, no ghost-written essays in Arts, and a "not legal advice" rule in Law.
Low temperature (0.2)	Keeps explanations steady and factual.
Run it yourself
You need Python 3.11 or 3.12 and about 1 GB of free disk space. The first run downloads the model (a few hundred MB), so you need internet once.

Windows (PowerShell)

git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
macOS / Linux

git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
Then open http://localhost:7860 in your browser, pick a faculty and ask a question.

To use another model, set the MODEL_REPO and MODEL_FILE environment variables to any GGUF model on Hugging Face, after checking its licence.

Docker (optional)

docker build -t dc-prof .
docker run -p 7860:7860 dc-prof
Dependencies
llama-cpp-python 0.3.2 (runs the model on CPU), Gradio 5.x (the chat interface) and huggingface_hub (downloads the model). They are listed in requirements.txt.

Files
File	Purpose
app.py	The whole app: model loading, faculty settings, reference notes, matching, prompt building and the chat interface
requirements.txt	Python dependencies
Dockerfile	Optional container build with the model included
LICENSE	MIT licence for our code
Add your own notes
Reference notes live in the NOTES dictionary in app.py. Each note is a set of keywords a question might contain, followed by a short, checked fact:

("osmosis diffusion membrane water concentration",
 "Osmosis is the diffusion of water across a partially permeable membrane, ..."),
Add one under the right faculty, restart the app and ask a matching question.

What's next
Notes reviewed by lecturers for every faculty
More fields, such as Medicine, Social Sciences, Agriculture and Business
Nigerian Pidgin, Yoruba, Hausa and Igbo support
An optional larger model for computers with more RAM
Acknowledgements
Model: SmolLM2-360M-Instruct by HuggingFaceTB (Apache-2.0). GGUF quantisation by bartowski.
Libraries: llama.cpp through llama-cpp-python, Gradio and Hugging Face Hub.
Starter template: the OPEN//BUILD 2026 AI App Starter from OSCA Ile-Ife, which we adapted.
Topic inspiration: the aerospace topic list was inspired by APOGEE, an aerospace question-and-answer page. No code or text was copied from it.
AI-assisted work: we used Claude (Anthropic), an AI assistant, to help write and debug the code, draft the reference notes and draft this README. We tested the app ourselves. The notes are short summaries and should be checked against textbooks and official sources.
Data: no datasets were used, and the app collects and stores no personal data.
Team Eco-Friendly
Agboola David Ojuoluwa, <Lagos State University>
Onwukanjo Chimaroke John, <Lagos State University>
Licence
Our code is released under the MIT Licence. The model has its own licence (Apache-2.0), linked above.
license: mit
title: Dc-Prof
sdk: docker
emoji: 🐢
colorFrom: green
colorTo: green
DC_Prof
A free AI study buddy that explains the basics of Engineering, Science, Arts, Law and Education in simple words, for students and for anyone thinking about venturing into one of these fields.

Team Eco-Friendly · OPEN//BUILD 2026 (OSCA Ile-Ife Hacktoberfest) · Theme: AI belongs to everyone

The problem
Choosing a field, or getting through the first year of one, is hard when there is nobody to ask.

Someone deciding between Engineering, Law, Science, Arts or Education rarely gets a simple, honest first look at what the field actually involves.
First- and second-year students get stuck on basic ideas, such as Ohm's law, osmosis, negligence or Piaget's stages, and can't always reach a lecturer or tutor.
Most AI tools need good internet, data or a paid plan, and they are not built around Nigerian examples, laws or institutions.
Who it is for
Who	Situation
Secondary-school leavers and UTME candidates	Want to understand a field before choosing a course
First- and second-year university students	Stuck on a basic concept and need a clear explanation
Career-changers and curious learners	Want to venture into a new field and need the fundamentals first
What it does
The user picks a faculty, asks a basic question, and DC_Prof answers in a fixed teaching format:

a simple explanation,
the key formula, rule or term, with each part explained,
one everyday example from Nigerian life (markets, okada, generators, school, farming, football),
a worked calculation when one applies,
one short quiz question to check understanding.
If it is not sure, it says so and points the user to a textbook or a lecturer.

Faculty	What it covers
Engineering	Aerospace (forces of flight, lift and drag, rockets, orbits), mechanical (stress and strain, torque, energy, thermodynamics), electrical and computer (Ohm's law, Kirchhoff's laws, AC and DC, logic gates)
Science	Physics basics, chemistry (atoms, bonding, acids and bases, the mole), biology (cells, photosynthesis, osmosis, genetics), maths (quadratics, differentiation, trigonometry, statistics)
Arts	Grammar and essay writing, literary terms, Nigerian and African literature and history, philosophy, logic, linguistics
Law	Nigerian Constitution and fundamental rights, sources of law, courts, contract, negligence, criminal law basics, the Land Use Act, becoming a lawyer
Education	Learning theories, Bloom's taxonomy, lesson planning, assessment, classroom management, the Nigerian education system
Demo
Demo video: <link> Live app: https://-Dc-prof.hf.space

It is hosted on a free Hugging Face Space, so the first load may take a minute while it wakes up. It also runs on an ordinary laptop, and the steps are in Run it yourself

Model
Model	SmolLM2-360M-Instruct by HuggingFaceTB
File used	SmolLM2-360M-Instruct-Q4_K_M.gguf (4-bit, quantised by bartowski)
Licence	Apache-2.0 (checked on the model card)
Why we chose it	It is tiny (360M parameters), so it downloads in minutes and runs on a laptop CPU with no GPU or API key. It is tuned for chat, and its licence allows reuse.
Its role	The tutor. It turns the question, the chosen faculty and the matching reference notes into a structured explanation, streamed word by word.
Limitations
It can be wrong. The model card warns that its output may be inaccurate and should be treated as assistive, not definitive. Always double-check before using an answer in an assignment or exam.
It is weak at arithmetic and multi-step reasoning, as small models usually are. Check every calculation.
English only in practice. Pidgin, Yoruba, Hausa and Igbo are not supported yet.
Limited coverage. There are 110 short reference notes. Questions outside them rely on the model alone and are less reliable.
The notes were written quickly and may contain mistakes, especially Nigerian laws, dates and figures. They should be checked against textbooks and official sources.
Law answers are study information, not legal advice.
Short memory. Only the last three exchanges are kept.
Speed depends on the computer. On a slow CPU, answers take a few seconds to start.
How it works
User picks a faculty and asks a question
              │
              ▼
   respond() finds the best-matching reference notes for that faculty
              │
              ▼
   builds the prompt: teaching rules + faculty topics + faculty safety rule
                      + matching notes + last 3 exchanges + the question
              │
              ▼
   llama.cpp runs SmolLM2-360M on the CPU, and the answer streams into the Gradio chat
Design choice	Why
Small open-weight model on CPU	Anyone with a basic laptop can run it, with no GPU, API key or cost.
Reference notes added to the prompt	A 360M model often guesses. Giving it checked facts for the question improves accuracy. This is a light form of retrieval-augmented generation.
Keyword matching, not embeddings	No second model and no extra RAM. It is easy to read, test and extend.
A rule for each faculty	No dangerous instructions in Engineering and Science, no ghost-written essays in Arts, and a "not legal advice" rule in Law.
Low temperature (0.2)	Keeps explanations steady and factual.
Run it yourself
You need Python 3.11 or 3.12 and about 1 GB of free disk space. The first run downloads the model (a few hundred MB), so you need internet once.

Windows (PowerShell)

git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
macOS / Linux

git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
Then open http://localhost:7860 in your browser, pick a faculty and ask a question.

To use another model, set the MODEL_REPO and MODEL_FILE environment variables to any GGUF model on Hugging Face, after checking its licence.

Docker (optional)

docker build -t dc-prof .
docker run -p 7860:7860 dc-prof
Dependencies
llama-cpp-python 0.3.2 (runs the model on CPU), Gradio 5.x (the chat interface) and huggingface_hub (downloads the model). They are listed in requirements.txt.

Files
File	Purpose
app.py	The whole app: model loading, faculty settings, reference notes, matching, prompt building and the chat interface
requirements.txt	Python dependencies
Dockerfile	Optional container build with the model included
LICENSE	MIT licence for our code
Add your own notes
Reference notes live in the NOTES dictionary in app.py. Each note is a set of keywords a question might contain, followed by a short, checked fact:

("osmosis diffusion membrane water concentration",
 "Osmosis is the diffusion of water across a partially permeable membrane, ..."),
Add one under the right faculty, restart the app and ask a matching question.

What's next
Notes reviewed by lecturers for every faculty
More fields, such as Medicine, Social Sciences, Agriculture and Business
Nigerian Pidgin, Yoruba, Hausa and Igbo support
An optional larger model for computers with more RAM
Acknowledgements
Model: SmolLM2-360M-Instruct by HuggingFaceTB (Apache-2.0). GGUF quantisation by bartowski.
Libraries: llama.cpp through llama-cpp-python, Gradio and Hugging Face Hub.
Starter template: the OPEN//BUILD 2026 AI App Starter from OSCA Ile-Ife, which we adapted.
Topic inspiration: the aerospace topic list was inspired by APOGEE, an aerospace question-and-answer page. No code or text was copied from it.
AI-assisted work: we used Claude (Anthropic), an AI assistant, to help write and debug the code, draft the reference notes and draft this README. We tested the app ourselves. The notes are short summaries and should be checked against textbooks and official sources.
Data: no datasets were used, and the app collects and stores no personal data.
Team Eco-Friendly
Agboola David Ojuoluwa, <Lagos State University>
Onwukanjo Chimaroke John, <Lagos State University>
Licence
Our code is released under the MIT Licence. The model has its own licence (Apache-2.0), linked above.
