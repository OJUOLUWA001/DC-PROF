import os
import re
import gradio as gr
from llama_cpp import Llama
from huggingface_hub import hf_hub_download

# ✏️ Pick your model on Hugging Face (a GGUF file that fits your server's RAM)
MODEL_REPO = os.getenv("MODEL_REPO", "bartowski/SmolLM2-360M-Instruct-GGUF")
MODEL_FILE = os.getenv("MODEL_FILE", "SmolLM2-360M-Instruct-Q4_K_M.gguf")

# Downloads the model on first run, then reuses the cached copy
model_path = hf_hub_download(MODEL_REPO, MODEL_FILE)
llm = Llama(model_path=model_path, n_ctx=4096, n_threads=os.cpu_count(), verbose=False)

APP_NAME = "DC_Prof"

ENG = "Engineering"
SCI = "Science"
ART = "Arts"
LAW = "Law"
EDU = "Education"

# What each faculty covers, added to the prompt depending on the student's choice
FOCUS = {
    ENG: (
        "aerospace, mechanical, and electrical and computer engineering basics: the forces of flight, lift and drag, "
        "rockets and orbits; stress and strain, torque, work, energy and power, thermodynamics and fluids; "
        "Ohm's law, Kirchhoff's laws, AC and DC, diodes, transistors, logic gates and binary."
    ),
    SCI: (
        "basic physics (Newton's laws, energy, waves), chemistry (atoms, the periodic table, bonding, acids and bases, "
        "the mole), biology (cells, photosynthesis, respiration, genetics, osmosis, evolution) and maths "
        "(algebra, quadratic equations, differentiation, trigonometry, probability and statistics)."
    ),
    ART: (
        "English grammar and essay writing, literary terms and figures of speech, Nigerian and African literature, "
        "Nigerian and African history, philosophy and logic, linguistics, and drama."
    ),
    LAW: (
        "the Nigerian Constitution and fundamental rights, sources of Nigerian law, the court system, the arms of "
        "government, contract, negligence, criminal law basics, the Land Use Act, and the path to becoming a lawyer."
    ),
    EDU: (
        "learning theories (Piaget, Vygotsky, Skinner), Bloom's taxonomy, lesson planning, teaching methods, "
        "assessment, classroom management, motivation, and the Nigerian education system."
    ),
}

# One extra rule per faculty, added to the prompt
RULES = {
    ENG: "Never give instructions for working on mains electricity, fuel systems, or structures without a qualified person.",
    SCI: "Never give instructions for making dangerous chemicals, explosives, or drugs. For lab work, tell the student to follow the lab safety rules and ask their lab instructor.",
    ART: "Help students understand and plan their writing, but do not write a complete essay for them to hand in as their own.",
    LAW: "Give general information about Nigerian law for study purposes only. This is not legal advice. Tell the student to confirm with their lecturer, the actual law, or a qualified lawyer.",
    EDU: "",
}

# Trusted reference notes. For each question, the best-matching notes are added to the prompt,
# so the small model answers from checked facts instead of guessing.
# Each entry is (keywords to match against the question, the note itself).
NOTES = {
    ENG: [
        # ---- Aerospace ----
        ("forces flight lift weight thrust drag balance level",
         "Four forces act on an aircraft: lift (up, from the wings), weight (down, gravity), thrust (forward, from engines or propellers) and drag (backward, air resistance). In steady level flight, lift equals weight and thrust equals drag."),
        ("lift wing wings airfoil fly flying flight plane airplane aeroplane equation formula coefficient",
         "Wings make lift by pushing air downward and by having lower pressure above the wing than below it. Lift equation: L = 0.5 x rho x V^2 x S x CL, where rho is air density (kg/m3), V is airspeed (m/s), S is wing area (m2) and CL is the lift coefficient."),
        ("drag resistance parasite induced equation formula coefficient",
         "Drag equation: D = 0.5 x rho x V^2 x S x CD, where CD is the drag coefficient. Parasite drag comes from shape and skin friction and grows with speed. Induced drag comes from making lift and falls as speed rises."),
        ("angle attack stall stalls stalling critical lift loss wing wings",
         "Angle of attack is the angle between the wing's chord line and the oncoming air. Lift rises with it until the critical angle (often about 15 to 18 degrees). Beyond that the airflow separates from the wing and the wing stalls. A stall is a loss of lift, not an engine failure. Recovery: lower the nose to reduce the angle of attack, then add power."),
        ("control surfaces aileron ailerons elevator rudder roll pitch yaw flap flaps slat slats steer",
         "Ailerons roll the aircraft, the elevator pitches the nose up or down, and the rudder yaws the nose left or right. Flaps and slats add lift at low speed so the aircraft can take off and land slower."),
        ("mach speed sound supersonic subsonic transonic hypersonic fast",
         "Mach number = aircraft speed divided by the local speed of sound. The speed of sound is about 340 m/s at sea level and about 295 m/s at airliner cruise altitude, where the air is colder. Subsonic is below Mach 0.8, transonic is about 0.8 to 1.2, supersonic is above 1, hypersonic is above 5."),
        ("bernoulli pressure velocity pitot airspeed airflow",
         "Bernoulli's principle: in steady flow along a streamline, faster-moving air has lower pressure (P + 0.5 x rho x V^2 stays roughly constant). It explains pressure changes around a wing, and a Pitot tube uses it to measure airspeed."),
        ("atmosphere layers troposphere stratosphere altitude high cruise cold temperature thin air",
         "The atmosphere's layers from the ground are the troposphere (to about 11 km, where weather happens and temperature falls about 6.5 C per km), stratosphere, mesosphere, thermosphere and exosphere. Airliners cruise near the top of the troposphere because thin air gives less drag. Space is conventionally said to start at the Karman line, 100 km up."),
        ("jet engine engines turbine compressor combustor turbofan turbojet turboprop",
         "A jet engine works in five steps: intake, compression, combustion, turbine, exhaust. The turbine drives the compressor (and the fan in a turbofan). A turbofan moves extra air around the engine core, which makes it quieter and more fuel-efficient than a turbojet, so most airliners use turbofans."),
        ("rocket rockets thrust newton propellant fuel space launch",
         "A rocket throws exhaust backward at high speed, and by Newton's third law the rocket is pushed forward. Rockets carry their own oxidizer, so they work in a vacuum, unlike jet engines. Thrust is roughly the mass flow rate of the exhaust times the exhaust velocity."),
        ("rocket equation delta tsiolkovsky mass ratio velocity change",
         "Tsiolkovsky rocket equation: delta-v = ve x ln(m0 / mf), where ve is the exhaust velocity, m0 the starting mass and mf the mass after the propellant is burned. Reaching low Earth orbit needs about 9.4 km/s of delta-v including losses. This is why rockets are mostly propellant and use stages."),
        ("isp specific impulse efficiency propellant engine",
         "Specific impulse (Isp), measured in seconds, shows how efficiently an engine uses propellant: higher means more thrust per unit of propellant used. Rough vacuum values: solid motors about 250 s, kerosene and oxygen about 330 s, hydrogen and oxygen about 450 s."),
        ("stage stages staging reusable booster falcon landing",
         "Staging drops empty tanks and engines during ascent so the rest of the rocket accelerates more efficiently. Reusable rockets such as Falcon 9 land their first stage so it can fly again."),
        ("orbit orbits orbital satellite satellites leo geo geostationary velocity speed fall",
         "A satellite stays in orbit because it is falling around the Earth while moving sideways fast enough to keep missing it. Low Earth orbit speed is about 7.8 km/s (about 28,000 km/h). LEO is below about 2,000 km. Geostationary orbit is 35,786 km above the equator, where a satellite matches Earth's rotation and appears fixed in the sky."),
        ("escape velocity gravity leave earth",
         "Escape velocity is the speed needed to leave a body's gravity without more propulsion: v = sqrt(2GM / r). From Earth's surface it is about 11.2 km/s."),
        ("weightless weightlessness float floating astronaut astronauts microgravity",
         "Astronauts float because they and the spacecraft are in free fall together, not because gravity is missing. At the ISS altitude of about 400 km, gravity is still around 90 percent of its strength at the surface."),
        ("reentry heat shield capsule burn plasma return",
         "On re-entry a spacecraft compresses the air in front of it, heating that air to extreme temperatures. Heat shields protect the vehicle: ablative shields char and carry heat away, and the Space Shuttle used insulating tiles."),
        ("parts aircraft fuselage wing empennage tail landing gear structure",
         "Main parts of an aircraft: the fuselage (body), wings, empennage (the tail, with horizontal and vertical stabilizers), engines and landing gear. The wings carry the lift and the tail gives stability and control."),
        ("swept sweep wing wings shock transonic",
         "Swept wings delay the sharp rise in drag caused by shock waves near the speed of sound, which is why jet airliners that cruise near Mach 0.8 have them."),
        ("aspect ratio wingspan span glider",
         "Aspect ratio = wingspan squared divided by wing area. Long, narrow wings (high aspect ratio), like a glider's, have less induced drag."),
        ("glide ratio lift drag efficiency glider gliding",
         "The lift-to-drag ratio (L/D) measures aerodynamic efficiency. A glider's glide ratio equals L/D, so an L/D of 30 means about 30 km travelled forward for every 1 km of height lost in still air."),
        ("g force load factor turn bank acceleration",
         "1 g is 9.81 m/s2. Load factor n = lift divided by weight. In a level turn, n = 1 / cos(bank angle), so a 60 degree bank gives n = 2, meaning the wings carry twice the aircraft's weight."),
        ("avionics fly wire autopilot navigation electronics computer",
         "Avionics are an aircraft's electronic systems: navigation, communication, autopilot and flight displays. Fly-by-wire replaces mechanical cables with electronic signals from computers to the control surfaces."),
        ("hohmann transfer orbit mars interplanetary window",
         "A Hohmann transfer is the most fuel-efficient two-burn way to move between two circular orbits in the same plane. Earth to Mars trips use this idea, with launch windows about every 26 months."),
        ("aerospace aeronautical astronautical career degree engineer study specialty",
         "Aeronautical engineering deals with flight inside the atmosphere, astronautical engineering with spacecraft, and aerospace engineering covers both. Common specialties are aerodynamics, propulsion, structures, materials, avionics, and guidance, navigation and control."),
        ("nigeria nigerian nasrda nigeriasat space agency satellite",
         "Nigeria's space agency is NASRDA (the National Space Research and Development Agency). Nigeria launched its first Earth-observation satellite, NigeriaSat-1, in 2003."),
        # ---- Mechanical ----
        ("stress strain young modulus elasticity deformation hooke spring",
         "Stress = force / area (unit: pascal, Pa). Strain = change in length / original length (no unit). Hooke's law: within the elastic limit, stress is proportional to strain, and the constant is Young's modulus E (stress = E x strain). For a spring, F = k x."),
        ("torque moment force lever arm turning rotation",
         "Torque (moment) = force x perpendicular distance from the pivot: T = F x r, measured in newton-metres (N m). A longer lever arm gives more torque for the same force."),
        ("work energy power joule watt kinetic potential",
         "Work = force x distance moved in the direction of the force (joules). Power = work / time (watts), and also P = F x v. Kinetic energy = 0.5 x m x v^2. Potential energy = m x g x h."),
        ("equilibrium statics balance beam reaction forces moments support",
         "A body is in equilibrium when the sum of all forces on it is zero and the sum of all moments about any point is zero. Statics problems use these two conditions to find unknown support reactions."),
        ("newton laws motion force mass acceleration inertia",
         "Newton's laws: (1) an object stays at rest or in uniform motion unless a net force acts on it; (2) F = m x a (newtons = kg x m/s2); (3) every action has an equal and opposite reaction."),
        ("thermodynamics first law heat internal energy engine efficiency",
         "First law of thermodynamics: energy is conserved, delta U = Q - W (change in internal energy = heat added - work done by the system). Efficiency = useful output / input x 100 percent. No real engine is 100 percent efficient."),
        ("heat transfer conduction convection radiation",
         "Heat moves by conduction (through solids, by contact between particles), convection (in fluids, by moving currents) and radiation (as electromagnetic waves, needing no medium)."),
        ("engine petrol diesel four stroke cylinder piston combustion",
         "A four-stroke engine cycle has intake, compression, power (combustion pushes the piston down) and exhaust. Petrol engines ignite the mixture with a spark plug; diesel engines ignite it with the heat of compression."),
        ("fluid pressure density depth pascal hydraulic brake jack",
         "Pressure = force / area (pascal). Pressure in a fluid at depth h: P = rho x g x h. Pascal's principle: pressure applied to a confined fluid is transmitted equally in all directions, which is how hydraulic jacks and brakes work."),
        ("gear gears ratio speed torque machine pulley lever simple machines mechanical advantage",
         "Gear ratio = teeth on the driven gear / teeth on the driving gear. A larger ratio gives more torque but less speed. Mechanical advantage = load / effort for simple machines such as levers, pulleys and inclined planes."),
        # ---- Electrical and computer ----
        ("ohm law voltage current resistance resistor",
         "Ohm's law: V = I x R, where V is voltage (volts), I is current (amperes) and R is resistance (ohms). Voltage is the push, current is the flow of charge, and resistance opposes the flow."),
        ("power electrical watt appliance energy kwh bill",
         "Electrical power P = V x I = I^2 x R = V^2 / R (watts). Energy = power x time, and electricity is billed in kilowatt-hours (kWh). Example: a 220 V appliance drawing 5 A uses 1100 W."),
        ("kirchhoff law current voltage loop node circuit analysis",
         "Kirchhoff's current law (KCL): the current entering a node equals the current leaving it. Kirchhoff's voltage law (KVL): the voltages around any closed loop add up to zero."),
        ("series parallel resistors total equivalent circuit",
         "Resistors in series: R total = R1 + R2 + ..., and the same current flows through all of them. Resistors in parallel: 1 / R total = 1 / R1 + 1 / R2 + ..., and the same voltage is across each branch."),
        ("capacitor capacitance charge farad inductor inductance",
         "A capacitor stores energy in an electric field: Q = C x V (C in farads), and energy = 0.5 x C x V^2. An inductor stores energy in a magnetic field and opposes changes in current."),
        ("ac dc alternating direct current frequency mains hertz transformer",
         "DC (direct current) flows one way, like from a battery. AC (alternating current) reverses direction regularly; Nigeria's mains supply is about 230 V at 50 Hz. Transformers work only with AC."),
        ("diode transistor semiconductor silicon led rectifier switch amplifier",
         "A diode lets current flow in one direction only, and rectifiers use diodes to turn AC into DC. A transistor is a semiconductor device that works as an electronic switch or an amplifier, and it is the building block of modern chips."),
        ("logic gate gates and or not nand nor xor binary boolean digital bit",
         "Basic logic gates: AND (output 1 only if all inputs are 1), OR (output 1 if any input is 1), NOT (inverts the input), plus NAND, NOR and XOR. Binary uses only 0 and 1; for example binary 1011 = 8 + 2 + 1 = 11 in decimal."),
        ("microcontroller arduino raspberry embedded sensor programming",
         "A microcontroller is a small computer on a single chip (for example the chip on an Arduino board) that reads sensors, runs a program and controls outputs such as LEDs and motors. It is the core of embedded systems."),
        ("nigeria power grid nepa tcn disco genco electricity supply inverter generator",
         "In Nigeria, electricity is generated by GenCos, transmitted by the Transmission Company of Nigeria (TCN) and distributed to customers by DisCos. Many households use inverters or generators as backup when the grid supply fails."),
    ],
    SCI: [
        ("newton laws motion force mass acceleration inertia",
         "Newton's laws: (1) an object stays at rest or in uniform motion unless a net force acts on it; (2) F = m x a (newtons = kg x m/s2); (3) every action has an equal and opposite reaction."),
        ("energy kinetic potential conservation work joule",
         "Energy cannot be created or destroyed, only changed from one form to another. Kinetic energy = 0.5 x m x v^2 and gravitational potential energy = m x g x h. Work done = force x distance (joules)."),
        ("wave waves frequency wavelength speed sound light amplitude",
         "Wave speed v = f x wavelength, where f is frequency in hertz. Sound is a longitudinal wave that needs a medium; light is an electromagnetic wave that can travel through a vacuum at about 3 x 10^8 m/s."),
        ("atom atomic proton neutron electron isotope nucleus number mass",
         "An atom has a nucleus of protons (positive) and neutrons (no charge), with electrons (negative) around it. Atomic number = number of protons. Mass number = protons + neutrons. Isotopes are atoms of the same element with different numbers of neutrons."),
        ("periodic table group period element metal nonmetal noble gas halogen alkali",
         "The periodic table arranges elements by increasing atomic number. Columns are groups (elements in a group have similar properties) and rows are periods. Group 1 are the alkali metals, group 17 the halogens and group 18 the noble gases."),
        ("bond bonding ionic covalent metallic electron share transfer",
         "Ionic bonds form when one atom transfers electrons to another, making oppositely charged ions (like Na+ and Cl- in table salt). Covalent bonds form when atoms share electrons (like in water, H2O). Metallic bonds hold metal atoms together in a sea of free electrons."),
        ("acid base ph neutral alkali indicator litmus neutralisation",
         "The pH scale runs from 0 to 14: below 7 is acidic, 7 is neutral and above 7 is basic (alkaline). pH = -log10 [H+]. An acid plus a base gives a salt and water (neutralisation)."),
        ("mole avogadro molar mass amount chemical calculation stoichiometry equation balance",
         "One mole of any substance contains 6.022 x 10^23 particles (Avogadro's number). Number of moles n = mass / molar mass. A balanced chemical equation shows the mole ratios of reactants and products, because mass is conserved."),
        ("gas pressure volume temperature boyle charles ideal kelvin",
         "Ideal gas law: P x V = n x R x T (R = 8.314 J/mol K, temperature in kelvin). Boyle's law: at constant temperature, pressure x volume stays constant. Convert Celsius to kelvin by adding 273.15."),
        ("photosynthesis chloroplast plant glucose chlorophyll light",
         "Photosynthesis happens in chloroplasts: 6CO2 + 6H2O + light energy -> C6H12O6 + 6O2. Plants use light to turn carbon dioxide and water into glucose and oxygen."),
        ("respiration mitochondria atp aerobic anaerobic energy cell lactic",
         "Aerobic respiration happens mainly in mitochondria: C6H12O6 + 6O2 -> 6CO2 + 6H2O + energy (ATP). Anaerobic respiration releases less energy; in muscles it makes lactic acid, and in yeast it makes ethanol and carbon dioxide."),
        ("cell cells organelle nucleus membrane prokaryote eukaryote wall",
         "Cells are the basic units of life. Eukaryotic cells (plants, animals, fungi) have a nucleus and organelles such as mitochondria; prokaryotic cells (bacteria) have no nucleus. Plant cells also have a cell wall and chloroplasts."),
        ("osmosis diffusion membrane water concentration active transport",
         "Diffusion is the net movement of particles from a region of high concentration to low concentration. Osmosis is the diffusion of water across a partially permeable membrane, from a dilute solution (high water potential) to a more concentrated one. Active transport moves substances against a gradient and needs energy."),
        ("dna rna gene genes chromosome heredity genetics allele mendel dominant recessive punnett",
         "DNA is a double helix whose bases pair A with T and C with G; genes are sections of DNA that code for proteins. Alleles are versions of a gene. A dominant allele shows up in the offspring if present, while a recessive trait shows only with two copies. A Punnett square predicts the offspring ratios."),
        ("evolution natural selection darwin adaptation species variation",
         "Natural selection (Darwin): individuals vary, some variations are inherited, and those better suited to the environment survive and reproduce more, so those traits become more common over generations."),
        ("quadratic equation formula roots discriminant algebra solve",
         "For ax^2 + bx + c = 0, the roots are x = (-b +/- sqrt(b^2 - 4ac)) / (2a). The discriminant b^2 - 4ac tells you: positive means two real roots, zero means one repeated root, negative means no real roots."),
        ("differentiation differentiate derivative calculus gradient rate change power rule integration integral",
         "Differentiation finds the rate of change (gradient) of a function. Power rule: d/dx (x^n) = n x^(n-1), so the derivative of x^3 is 3x^2. Integration reverses differentiation: the integral of x^n is x^(n+1) / (n+1) + C."),
        ("pythagoras triangle trigonometry sine cosine tangent sohcahtoa hypotenuse",
         "Pythagoras: in a right-angled triangle, a^2 + b^2 = c^2, where c is the hypotenuse. SOH CAH TOA: sin = opposite / hypotenuse, cos = adjacent / hypotenuse, tan = opposite / adjacent."),
        ("probability statistics mean median mode average range standard deviation",
         "Probability = favourable outcomes / total outcomes (a value from 0 to 1). Mean = sum of values / number of values; the median is the middle value when sorted; the mode is the most frequent value."),
        ("scientific method hypothesis experiment variable control observation",
         "The scientific method: observe, ask a question, form a testable hypothesis, run a controlled experiment (change one independent variable, measure the dependent variable, keep the others constant), analyse the results, and conclude."),
    ],
    ART: [
        ("figure speech simile metaphor personification hyperbole irony alliteration onomatopoeia oxymoron literary device",
         "Figures of speech: a simile compares using 'like' or 'as'; a metaphor says one thing is another; personification gives human traits to non-human things; hyperbole is deliberate exaggeration; irony says or shows the opposite of what is expected; alliteration repeats starting sounds; onomatopoeia imitates a sound (like 'buzz')."),
        ("genre prose poetry drama novel plot character setting theme point view conflict narrator story",
         "The three main literary genres are prose, poetry and drama. Elements of a story: plot (the events), characters, setting (time and place), theme (the central idea), point of view (who tells the story) and conflict (the struggle that drives the plot)."),
        ("poetry poem rhyme rhythm metre stanza imagery tone verse analyse",
         "Poetry terms: a stanza is a group of lines, rhyme is matching end sounds, metre is the pattern of stressed and unstressed syllables, imagery is language that appeals to the senses, and tone is the poet's attitude. To analyse a poem, ask what it says (theme), how it says it (devices) and why."),
        ("nigerian african literature achebe soyinka adichie okri tutuola novel writer author",
         "Chinua Achebe wrote Things Fall Apart (1958). Wole Soyinka won the Nobel Prize in Literature in 1986, the first African to do so. Chimamanda Ngozi Adichie wrote Half of a Yellow Sun and Americanah. Ben Okri won the Booker Prize in 1991 for The Famished Road. Amos Tutuola wrote The Palm-Wine Drinkard (1952)."),
        ("drama theatre tragedy comedy aristotle play playwright stage",
         "Aristotle named six elements of tragedy: plot, character, thought, diction, melody (music) and spectacle. A tragedy ends in the downfall of its hero, often through a flaw (hamartia), while a comedy usually ends happily. Nigerian playwrights include Wole Soyinka and Ola Rotimi."),
        ("history nigeria independence amalgamation 1914 lugard colonial civil war republic",
         "Key dates in Nigerian history: the 1914 amalgamation of the Northern and Southern Protectorates under Lord Lugard; independence on 1 October 1960; the Nigerian Civil War from 1967 to 1970; and the return to civilian rule on 29 May 1999 (the Fourth Republic)."),
        ("precolonial empire kingdom oyo benin sokoto caliphate kanem bornu hausa yoruba igbo ife",
         "Before colonial rule the area that is now Nigeria had many states, including the Oyo Empire and Ile-Ife (Yoruba), the Kingdom of Benin, the Kanem-Bornu Empire, the Hausa city-states, and the Sokoto Caliphate founded by Usman dan Fodio after his jihad of 1804."),
        ("slave trade abolition scramble africa berlin conference colonialism europe",
         "The Berlin Conference of 1884 to 1885 set rules for European claims in Africa during the 'Scramble for Africa'. Britain banned its slave trade in 1807 and slavery across its empire in the 1830s."),
        ("philosophy branches metaphysics epistemology ethics logic aesthetics socrates plato aristotle",
         "Main branches of philosophy: metaphysics (what exists), epistemology (what we can know), ethics (right and wrong), logic (correct reasoning) and aesthetics (beauty and art). Socrates taught by questioning, Plato was his student and Aristotle was Plato's student."),
        ("logic argument premise conclusion valid sound fallacy deductive inductive reasoning",
         "An argument has premises and a conclusion. A deductive argument is valid if the conclusion must follow from the premises, and sound if it is valid and its premises are true. Inductive arguments make the conclusion probable rather than certain. A fallacy is a flaw in reasoning."),
        ("ethics utilitarianism deontology virtue kant mill bentham moral",
         "Utilitarianism (Bentham, Mill) judges actions by whether they produce the greatest good for the greatest number. Deontology (Kant) judges actions by whether they follow moral duties or rules. Virtue ethics (Aristotle) asks what a good person would do."),
        ("linguistics phonetics phonology morphology syntax semantics pragmatics language",
         "Linguistics studies language: phonetics (speech sounds), phonology (sound patterns), morphology (word structure), syntax (sentence structure), semantics (meaning) and pragmatics (meaning in context)."),
        ("nigerian languages hausa yoruba igbo pidgin english official",
         "Nigeria has over 500 languages. English is the official language, and the three largest indigenous languages are Hausa, Yoruba and Igbo. Nigerian Pidgin is widely spoken across the country."),
        ("grammar parts speech noun pronoun verb adjective adverb preposition conjunction tense agreement sentence",
         "Parts of speech: noun, pronoun, verb, adjective, adverb, preposition, conjunction and interjection. Subject-verb agreement: a singular subject takes a singular verb ('The student writes') and a plural subject takes a plural verb ('The students write')."),
        ("essay writing introduction paragraph thesis conclusion structure argument plagiarism citation reference",
         "A good essay has an introduction with a thesis statement, body paragraphs (each with a topic sentence, evidence and explanation) and a conclusion. Plagiarism is presenting someone else's words or ideas as your own, so always cite sources in a style such as APA, MLA or Harvard."),
        ("religion religious islam christianity traditional worship",
         "Islam, Christianity and African traditional religions are the main faiths practised in Nigeria. Religious studies examines the beliefs, texts, history and practices of religions, usually in a neutral, comparative way."),
    ],
    LAW: [
        ("constitution supremacy supreme law 1999 section void inconsistent",
         "The 1999 Constitution of the Federal Republic of Nigeria (as amended) is the supreme law. Under section 1(3), any other law that is inconsistent with it is void to the extent of the inconsistency."),
        ("sources law nigerian legislation customary english common equity case precedent sharia",
         "Sources of Nigerian law: the Constitution, legislation (Acts of the National Assembly and laws of State Houses of Assembly), received English law (common law, equity and statutes of general application in force in England on 1 January 1900), customary law, Islamic law in some personal matters, and judicial precedent."),
        ("court courts hierarchy supreme appeal high magistrate customary federal jurisdiction",
         "Nigerian court hierarchy: the Supreme Court is the highest, then the Court of Appeal, then the Federal High Court and the High Courts of the states and the FCT, then lower courts such as Magistrate, District, Customary and Sharia courts. The National Industrial Court handles labour matters."),
        ("arms government separation powers executive legislature judiciary national assembly senate house representatives",
         "Nigeria has three arms of government: the executive (the President and ministers), the legislature (the National Assembly, made up of the Senate with 109 members and the House of Representatives with 360 members) and the judiciary (the courts). Separation of powers stops any one arm from holding all the power."),
        ("fundamental rights chapter iv life dignity liberty fair hearing privacy expression assembly movement discrimination property",
         "Chapter IV of the Constitution protects fundamental rights, including life (s.33), dignity of the human person (s.34), personal liberty (s.35), fair hearing (s.36), private and family life (s.37), freedom of thought, conscience and religion (s.38), freedom of expression (s.39), peaceful assembly and association (s.40), freedom of movement (s.41), freedom from discrimination (s.42) and rights over property (s.43 and s.44)."),
        ("fair hearing natural justice audi alteram partem nemo judex innocence presumption trial",
         "Fair hearing (section 36) rests on natural justice: audi alteram partem (hear both sides) and nemo judex in causa sua (no one should judge their own case). Section 36(5) presumes that a person charged with a crime is innocent until proved guilty."),
        ("arrest detention police rights silent lawyer bail suspect",
         "Under section 35 of the Constitution, a person who is arrested has the right to remain silent until they have consulted a lawyer or a person of their choice, and must be told the reasons for the arrest. The Administration of Criminal Justice Act 2015 also sets out rules on arrest and bail."),
        ("contract offer acceptance consideration capacity intention agreement breach damages",
         "A valid contract needs offer, acceptance, consideration (something of value exchanged), intention to create legal relations, and capacity of the parties. If a party breaks the contract, the usual remedy is damages."),
        ("tort negligence duty care breach damage donoghue stevenson neighbour",
         "Negligence is a tort with three elements: the defendant owed the claimant a duty of care, breached it, and caused damage as a result. The duty of care idea comes from Donoghue v Stevenson (1932), the 'neighbour principle', which is widely cited in Nigerian courts."),
        ("crime criminal actus reus mens rea burden proof beyond reasonable doubt offence civil balance probabilities",
         "A crime generally requires actus reus (the guilty act) and mens rea (the guilty mind). In a criminal case the prosecution must prove guilt beyond reasonable doubt; in a civil case the claimant must prove the case on a balance of probabilities."),
        ("precedent stare decisis binding ratio decidendi obiter case law judicial",
         "Under stare decisis, lower courts must follow earlier decisions of higher courts. The ratio decidendi is the legal reasoning that decides the case and is binding; obiter dicta are remarks made in passing and are only persuasive."),
        ("land use act certificate occupancy governor land property title",
         "The Land Use Act 1978 vests all land in each state in the Governor, to hold in trust for the people. A person usually holds land through a right of occupancy, evidenced by a Certificate of Occupancy (C of O)."),
        ("lawyer legal career call bar law school llb barrister solicitor",
         "To become a lawyer in Nigeria you study for the LL.B. degree, attend the Nigerian Law School, pass the Bar Final examinations, and are called to the Nigerian Bar. Nigerian lawyers practise as both barristers and solicitors."),
        ("federal state government federalism states fct local council exclusive concurrent list",
         "Nigeria is a federation of 36 states and the Federal Capital Territory, with local government areas below the states. The Constitution divides legislative powers into the Exclusive Legislative List (federal only) and the Concurrent Legislative List (federal and state)."),
    ],
    EDU: [
        ("piaget stages cognitive development sensorimotor preoperational concrete formal child",
         "Piaget's four stages of cognitive development: sensorimotor (birth to about 2 years), preoperational (about 2 to 7), concrete operational (about 7 to 11) and formal operational (about 11 onwards)."),
        ("vygotsky zone proximal development zpd scaffolding social learning",
         "Vygotsky's zone of proximal development (ZPD) is the gap between what a learner can do alone and what they can do with help. Scaffolding means giving that help (hints, modelling, questions) and gradually removing it as the learner improves."),
        ("behaviourism behaviorism skinner pavlov thorndike conditioning reinforcement punishment",
         "Pavlov described classical conditioning (learning by association). Skinner described operant conditioning, where behaviour is shaped by its consequences: reinforcement makes a behaviour more likely and punishment makes it less likely. Thorndike's law of effect says rewarded behaviour tends to be repeated."),
        ("bloom taxonomy remember understand apply analyse analyze evaluate create objectives cognitive",
         "Bloom's revised taxonomy, from lower to higher thinking skills: remember, understand, apply, analyse, evaluate, create. Teachers use it to write learning objectives with action verbs such as list, explain, solve, compare, judge and design."),
        ("lesson plan note objectives introduction presentation evaluation conclusion materials previous knowledge",
         "A typical lesson plan includes: class, subject, topic and duration; behavioural objectives; previous knowledge; instructional materials; the steps of the lesson (introduction, presentation, development); evaluation questions; a summary or conclusion; and an assignment."),
        ("assessment formative summative diagnostic continuous test examination evaluation feedback",
         "Formative assessment happens during learning to give feedback and improve teaching (quizzes, questions, homework). Summative assessment happens at the end to measure what was learnt (terminal exams). Diagnostic assessment finds learning gaps before teaching. Continuous assessment combines scores gathered over time."),
        ("teaching methods lecture discussion demonstration project inquiry discovery cooperative role play",
         "Common teaching methods: lecture, discussion, demonstration, role play, project, inquiry or discovery, and cooperative (group) learning. Good teachers choose the method that fits the objective and the learners instead of always lecturing."),
        ("classroom management discipline rules routines behaviour reinforcement attention",
         "Good classroom management uses clear rules and routines, consistent consequences, praise for good behaviour, an interesting lesson, and moving around the room (proximity). Preventing problems works better than punishing them."),
        ("maslow hierarchy needs motivation intrinsic extrinsic self actualisation",
         "Maslow's hierarchy of needs: physiological, safety, love and belonging, esteem, and self-actualisation. A hungry or frightened learner struggles to learn. Intrinsic motivation comes from interest in the task itself; extrinsic motivation comes from rewards or pressure."),
        ("nigerian education system ube basic primary secondary tertiary policy junior senior",
         "Nigeria moved from the 6-3-3-4 system to the 9-3-4 system: nine years of basic education (primary plus junior secondary), three years of senior secondary and four years of tertiary study. Universal Basic Education (UBE) was launched in 1999."),
        ("teacher registration trcn licence qualification profession certificate",
         "The Teachers Registration Council of Nigeria (TRCN) registers and licenses teachers, so professional teachers are expected to hold TRCN certification in addition to their teaching qualification."),
        ("study tips revision memory active recall spaced repetition learning techniques exam",
         "Research supports retrieval practice (testing yourself instead of re-reading) and spaced practice (studying a little across many days instead of cramming). Explaining a topic aloud in your own words also shows what you do not yet understand."),
        ("inclusive special education disability needs learners differentiation",
         "Inclusive education means learners with different abilities and needs learn together in the same classroom with the support they need. Differentiation means adjusting the content, activities or support so each learner can succeed."),
        ("curriculum syllabus scheme work objectives subject",
         "A curriculum is the planned set of learning experiences in a course or school, including objectives, content, methods and assessment. A syllabus is the outline of topics for one subject, and a scheme of work spreads that syllabus across the weeks of a term."),
    ],
}


def _terms(text):
    # lowercase words of 2+ letters with a trailing "s" removed, so "wings" matches "wing"
    return {w[:-1] if w.endswith("s") else w for w in re.findall(r"[a-z0-9]+", text.lower()) if len(w) > 1}


INDEX = {faculty: [(_terms(keys), note) for keys, note in items] for faculty, items in NOTES.items()}


def find_notes(faculty, question, limit=3):
    q = _terms(question)
    scored = [(len(q & terms), note) for terms, note in INDEX.get(faculty, []) if q & terms]
    scored.sort(key=lambda x: -x[0])
    if not scored:
        return []
    # keep only notes that match nearly as well as the best one, so weak matches don't add noise
    top = scored[0][0]
    return [note for score, note in scored[:limit] if score >= top * 0.6]


# ✏️ This is your product: who the AI is, what it does, and its rules
SYSTEM = """You are DC_Prof, a friendly and patient study buddy for Nigerian university students.

For every answer:
1. Explain the concept in simple words.
2. If a formula, rule, or key term applies, state it clearly and explain each part.
3. Give one everyday example from Nigerian life (for example markets, okada, generators and power supply, school, church or mosque, farming, or football).
4. If a calculation applies, show it step by step and include units.
5. End with one short quiz question.

Rules:
- If you are not sure, say "I'm not sure" and suggest checking a textbook or asking a lecturer.
- Remind the student to double-check facts and calculations before using them in an assignment, exam, or project.
- Only answer study-related questions. Politely decline everything else.
- If the question belongs to a different faculty, answer briefly and tell the student they can switch the faculty in the dropdown."""


def respond(message, history, faculty):
    system = f"{SYSTEM}\n\nThe student is in the Faculty of {faculty}. Focus on basics such as: {FOCUS[faculty]}"
    if RULES[faculty]:
        system += f"\nExtra rule for this faculty: {RULES[faculty]}"

    # find reference notes for this question (or, for a short follow-up, the previous question)
    notes = find_notes(faculty, message)
    if not notes and history:
        last_user = next((str(m["content"]) for m in reversed(history) if m["role"] == "user"), "")
        notes = find_notes(faculty, last_user)
    if notes:
        system += "\n\nTrusted reference notes. Base your answer on these facts when they are relevant:\n"
        system += "\n".join(f"- {n}" for n in notes)

    # keep the last 3 exchanges so the prompt stays small and fast
    past = [{"role": m["role"], "content": m["content"]} for m in history[-6:]]
    messages = [{"role": "system", "content": system}, *past, {"role": "user", "content": message}]

    reply = ""
    for chunk in llm.create_chat_completion(messages=messages, max_tokens=500, temperature=0.2, stream=True):
        reply += chunk["choices"][0]["delta"].get("content", "")
        yield reply


demo = gr.ChatInterface(
    fn=respond,
    type="messages",
    title="DC_PROf",
    description=(
        "Pick your faculty (Engineering, Science, Arts, Law or Education) and ask about any basic concept "
        "you're stuck on. Always double-check answers before using them in an assignment."
    ),
    additional_inputs=[
        gr.Dropdown(choices=[ENG, SCI, ART, LAW, EDU], value=ENG, label="Your faculty"),
    ],
    examples=[
        ["What are the four forces acting on an aeroplane?", ENG],
        ["Explain Ohm's law with an example", ENG],
        ["What is osmosis?", SCI],
        ["How do I solve a quadratic equation?", SCI],
        ["What is the difference between a simile and a metaphor?", ART],
        ["What happened in the 1914 amalgamation of Nigeria?", ART],
        ["What are fundamental rights in the Nigerian Constitution?", LAW],
        ["What makes a contract valid?", LAW],
        ["What are Piaget's stages of development?", EDU],
        ["What is a lesson plan made of?", EDU],
    ],
    cache_examples=False,
    theme=gr.themes.Soft(primary_hue="green", secondary_hue="emerald", neutral_hue="slate"),
)

if __name__ == "__main__":
    # localhost on your own computer; the Dockerfile sets HOST=0.0.0.0 so the container is reachable
    host = os.getenv("HOST", "localhost")
    demo.queue(max_size=20).launch(server_name=host, server_port=int(os.getenv("PORT", 7860)))