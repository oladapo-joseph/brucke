"""German A1 — hand-written units for stages 1–8."""
from .schema import A, G, L, N, P, Q, S, SND, V, W

UNITS = [
    # ------------------------------------------------------------------ 1
    {
        "stage": 1,
        "title": "Sounds & Letters",
        "native": "Laute & Buchstaben",
        "can_do": [
            "Say the alphabet and spell your name out loud",
            "Read any German word aloud using about 15 spelling rules",
            "Say ä, ö, ü, ß, ch and the German r",
            "Greet people and say please / thank you",
        ],
        "grammar": [
            G("The alphabet: same letters, new names",
              "German uses the same 26 letters as English, plus **ä, ö, ü** and **ß**. "
              "The letters look familiar, but their *names* are different. Most are easy, "
              "but a few are traps for English speakers, so the app drills these extra:",
              [["Letter", "German name", "Sounds like", "⚠ Don't confuse with"],
               ["E", "E", "*ay* (English A)", "English E"],
               ["I", "I", "*ee* (English E)", "English I"],
               ["A", "A", "*ah*", "English A"],
               ["J", "Jot", "*yot*", "G"],
               ["V", "Vau", "*fow*", "W"],
               ["W", "We", "*vay*", "V"],
               ["Y", "Ypsilon", "*ÜP-see-lon*", "I"],
               ["Z", "Zett", "*tset*", "C, S"]], at="letters"),
            G("Spelling out loud",
              "Spelling is a real-life skill: names, emails, booking a table. Germans spell letter by letter: "
              "*Mein Name ist Sam: **S – A – M**.*\nUseful phrases:\n"
              "**Wie schreibt man das?** = How do you spell that?\n"
              "**Können Sie das buchstabieren?** = Can you spell that?\n"
              "For a double letter, say **Doppel-**: *Anna* = **A – Doppel-N – A**.", at="sentences"),
            G("German is spelled the way it sounds",
              "Good news: once you know about **15 rules**, you can read almost any German word aloud. "
              "Letters are rarely silent. Every vowel in *Käse* is spoken: **KÄ-se**.", at="sounds"),
            G("Umlauts and ß",
              "The two dots change the sound: **a → ä**, **o → ö**, **u → ü**.\n"
              "No German keyboard? Type **ae, oe, ue** (the app accepts them, with a gentle note) "
              "or use the accent bar.\n**ß** is just a sharp *ss*: *Straße* = street.",
              [["Letter", "Sounds like", "Example"],
               ["ä", "e in *bed*", "Käse"],
               ["ö", "say *ay* with round lips", "schön"],
               ["ü", "say *ee* with round lips", "müde"],
               ["ei", "*eye*", "Wein"],
               ["ie", "*ee*", "Liebe"],
               ["w", "English *v*", "Wasser"],
               ["v", "English *f*", "Vater"],
               ["z", "*ts*", "Zeit"]], at="letters:last"),
            G("Nouns always start with a capital letter",
              "Every German noun is capitalised: *der Hund*, *das Haus*, *die Stadt*. "
              "That makes nouns easy to spot in a sentence.", at="words"),
        ],
        "letters": [
            L("A", "A", "ah", "Apfel", "apple", "EH"),
            L("B", "Be", "bay", "Brot", "bread", "PDW"),
            L("C", "Ce", "tsay", "Cent", "cent", "ZSK", "German C is called 'tsay', like the ts in 'cats'."),
            L("D", "De", "day", "Dach", "roof", "TB"),
            L("E", "E", "ay (like English A!)", "Ei", "egg", "IA", "The German E sounds like the English letter A. Classic trap!"),
            L("F", "Ef", "eff", "Fisch", "fish", "VS"),
            L("G", "Ge", "gay (hard g)", "Garten", "garden", "JK", "Always a hard g as in 'go', never like English G."),
            L("H", "Ha", "hah", "Haus", "house", "AK"),
            L("I", "I", "ee (like English E!)", "Insel", "island", "EÜ", "The German I sounds like the English letter E."),
            L("J", "Jot", "yot", "ja", "yes", "GIY", "J is 'yot', and it sounds like English y: ja = 'yah'.", say="Jot"),
            L("K", "Ka", "kah", "Kind", "child", "QHC"),
            L("L", "El", "el", "Lampe", "lamp", "RN"),
            L("M", "Em", "em", "Milch", "milk", "N"),
            L("N", "En", "en", "Nacht", "night", "M"),
            L("O", "O", "oh", "Oma", "grandma", "UÖ"),
            L("P", "Pe", "pay", "Papa", "dad", "BT"),
            L("Q", "Qu", "koo", "Quatsch", "nonsense", "KU", "Q is called 'koo'. 'Qu' is said 'kv': Quatsch = 'kvatch'.", say="Q"),
            L("R", "Er", "air (throaty)", "rot", "red", "LE"),
            L("S", "Es", "ess", "Sonne", "sun", "ZßF", "S before a vowel sounds like English z: Sonne = 'ZON-nuh'."),
            L("T", "Te", "tay", "Tee", "tea", "DP"),
            L("U", "U", "oo", "Uhr", "clock", "OÜ"),
            L("V", "Vau", "fow", "Vogel", "bird", "WF", "V is called 'fow', and usually sounds like f: Vogel = 'FOH-gel'.", say="Vau"),
            L("W", "We", "vay", "Wasser", "water", "VB", "W is called 'vay', and sounds like English v.", say="We"),
            L("X", "Ix", "icks", "Xylofon", "xylophone", "SZ"),
            L("Y", "Ypsilon", "ÜP-see-lon", "Yoga", "yoga", "IÜJ", "Y has a long name: Ypsilon.", say="Ypsilon"),
            L("Z", "Zett", "tset", "Zug", "train", "CS", "Z sounds like ts, even at the start: Zug = 'tsook'.", say="Zett"),
            L("Ä", "Ä", "eh", "Käse", "cheese", "AE", "Spell it as 'Ä' or 'A-Umlaut'."),
            L("Ö", "Ö", "ur (round lips)", "Öl", "oil", "OE"),
            L("Ü", "Ü", "ee with round lips", "Übung", "exercise", "UIY"),
            L("ß", "Eszett", "ess-TSET", "Fuß", "foot", "SZ", "ß is called 'Eszett' or 'scharfes S' (sharp s). There's no capital in normal writing.", say="Eszett"),
        ],
        "sounds": [
            SND("ä", "Käse", "cheese", "Like the 'e' in 'bed', held a little longer."),
            SND("ö", "schön", "beautiful", "Say 'ay' as in 'say', then round your lips."),
            SND("ü", "müde", "tired", "Say 'ee', then round your lips as if for 'oo'."),
            SND("ß", "Straße", "street", "A sharp, hissing 'ss'."),
            SND("ei", "Wein", "wine", "Like English 'eye'. Trick: ei sounds like the second letter, i."),
            SND("ie", "Liebe", "love", "Like 'ee' in 'see'. Trick: ie sounds like the second letter, e."),
            SND("eu", "Freund", "friend", "Like 'oy' in 'boy'. äu sounds the same."),
            SND("ch (soft)", "ich", "I", "After i/e/ä/ö/ü: a soft hiss, like the 'h' in 'huge'."),
            SND("ch (hard)", "Buch", "book", "After a/o/u: throaty, like Scottish 'loch'."),
            SND("w", "Wasser", "water", "German w sounds like English 'v'."),
            SND("v", "Vater", "father", "German v usually sounds like 'f'."),
            SND("z", "Zeit", "time", "Like 'ts' in 'cats', even at the start of a word."),
            SND("st / sp", "Stadt", "city", "At the start of a word, s sounds like 'sh': 'shtadt'."),
            SND("r", "rot", "red", "A soft gargle at the back of the throat."),
            SND("j", "ja", "yes", "German j sounds like English 'y'."),
        ],
        "vocab": [
            W("Hallo", "hello"),
            W("Tschüss", "bye"),
            W("ja", "yes"),
            W("nein", "no"),
            W("danke", "thank you", en_alt=["thanks"]),
            W("bitte", "please"),
            W("Entschuldigung", "excuse me / sorry", en_alt=["excuse me", "sorry"]),
            W("Guten Morgen", "good morning"),
            W("Guten Tag", "good day / hello", en_alt=["good day"]),
            W("Guten Abend", "good evening"),
            W("Auf Wiedersehen", "goodbye (formal)", en_alt=["goodbye"]),
        ],
        "sentences": [
            S("Danke schön!", "Thank you very much!", en_alt=["Thanks a lot!"]),
            S("Bitte schön.", "You're welcome."),
            S("Wie bitte?", "Pardon?", en_alt=["Sorry?", "Excuse me?"]),
            S("Ja, bitte.", "Yes, please."),
            S("Nein, danke.", "No, thank you.", en_alt=["No, thanks."]),
            S("Guten Morgen, Frau Schmidt!", "Good morning, Mrs Schmidt!"),
            S("Wie schreibt man das?", "How do you spell that?", en_alt=["How is that written?"]),
            S("Können Sie das buchstabieren?", "Can you spell that?", en_alt=["Could you spell that?"]),
        ],
        "reading": P(
            "Am Morgen",
            "Anna: Guten Morgen!\nHerr Weber: Guten Morgen, Anna! Kaffee?\nAnna: Ja, bitte. Danke schön!\n"
            "Herr Weber: Bitte schön. Tschüss!\nAnna: Tschüss!",
            "Anna: Good morning! / Mr Weber: Good morning, Anna! Coffee? / Anna: Yes, please. Thank you very much! / "
            "Mr Weber: You're welcome. Bye! / Anna: Bye!",
            [Q("What time of day is it?", ["Morning", "Evening", "Night", "Afternoon"], 0),
             Q("What does Anna say when she's offered coffee?", ["Yes, please", "No, thanks", "Pardon?", "Goodbye"], 0)],
        ),
        "writing_prompt": "Write a tiny dialogue: greet someone, accept something politely, thank them and say goodbye.",
        "writing_model": "Hallo! Guten Tag! – Tee? – Ja, bitte. Danke schön! – Bitte schön. – Tschüss!",
    },
    # ------------------------------------------------------------------ 2
    {
        "stage": 2,
        "title": "Hello, I am…",
        "native": "Hallo, ich bin …",
        "can_do": [
            "Say your name, where you come from and where you live",
            "Ask someone the same, both formally and informally",
            "Use 'sein' (to be) and regular verb endings",
        ],
        "grammar": [
            G("Verb endings follow the person",
              "German verbs change their ending to match **who** is doing the action. "
              "Learn the pattern once and it works for most verbs.",
              [["", "wohnen (live)", "sein (be) ⚠ irregular"],
               ["ich", "wohn**e**", "bin"], ["du", "wohn**st**", "bist"], ["er / sie / es", "wohn**t**", "ist"],
               ["wir", "wohn**en**", "sind"], ["ihr", "wohn**t**", "seid"], ["sie / Sie", "wohn**en**", "sind"]]),
            G("du or Sie?",
              "**du** = informal *you* (friends, family, children, people your age online).\n"
              "**Sie** = formal *you* (strangers, work, officials). It is always written with a capital **S**, "
              "and the verb takes the *wir* form: *Wie heißen **Sie**?*"),
            G("The verb is always the 2nd building block",
              "In a German statement the conjugated verb sits in **position 2**.\n"
              "*Ich* **wohne** *in Berlin.* · *In Berlin* **wohne** *ich.*\n"
              "A question word goes first and the verb is still 2nd: *Wo* **wohnst** *du?*"),
        ],
        "vocab": [
            W("ich", "I", "pron"),
            W("du", "you (informal)", "pron"),
            W("Sie", "you (formal)", "pron"),
            W("er", "he", "pron"),
            W("sie", "she / they", "pron", en_alt=["she", "they"]),
            W("wir", "we", "pron"),
            V("sein", "to be", ["bin", "bist", "ist", "sind", "seid"]),
            V("heißen", "to be called", ["heiße", "heißt"], ex=("Ich heiße Max.", "My name is Max.")),
            V("kommen", "to come", ["komme", "kommst", "kommt"]),
            V("wohnen", "to live (reside)", ["wohne", "wohnst", "wohnt"], en_alt=["to live"]),
            W("woher", "where from", "q"),
            W("wo", "where", "q"),
            W("wie", "how", "q"),
            N("der Name", "name", "m", "die Namen"),
            N("das Land", "country", "n", "die Länder"),
            N("die Stadt", "city", "f", "die Städte", en_alt=["town"]),
        ],
        "sentences": [
            S("Ich heiße Anna.", "My name is Anna.", en_alt=["I am called Anna."]),
            S("Wie heißt du?", "What's your name?", en_alt=["What is your name?"]),
            S("Wie heißen Sie?", "What's your name? (formal)", en_alt=["What is your name?"]),
            S("Ich bin Student.", "I am a student.", alt=["Ich bin Studentin."], en_alt=["I'm a student."]),
            S("Woher kommst du?", "Where are you from?", en_alt=["Where do you come from?"]),
            S("Ich komme aus England.", "I come from England.", en_alt=["I'm from England."]),
            S("Ich wohne in Berlin.", "I live in Berlin.", alt=["In Berlin wohne ich."]),
            S("Wo wohnst du?", "Where do you live?"),
            S("Freut mich!", "Nice to meet you!", en_alt=["Pleased to meet you!"]),
        ],
        "reading": P(
            "Das bin ich",
            "Hallo! Ich heiße Lena. Ich komme aus Österreich, aber ich wohne in Hamburg. "
            "Ich bin Lehrerin. Und du? Wie heißt du und woher kommst du?",
            "Hello! My name is Lena. I come from Austria, but I live in Hamburg. I am a teacher. "
            "And you? What's your name and where are you from?",
            [Q("Where does Lena come from?", ["Austria", "Hamburg", "England", "Berlin"], 0),
             Q("Where does she live?", ["Hamburg", "Vienna", "Berlin", "Austria"], 0),
             Q("What is her job?", ["Teacher", "Student", "Doctor", "Cook"], 0)],
        ),
        "writing_prompt": "Introduce yourself in 3 sentences: your name, where you come from, and where you live.",
        "writing_model": "Ich heiße Sam. Ich komme aus England. Ich wohne in London.",
    },
    # ------------------------------------------------------------------ 3
    {
        "stage": 3,
        "title": "Things & their gender",
        "native": "Der, die, das",
        "can_do": [
            "Name everyday objects with the right article",
            "Use ein / eine and kein / keine",
            "Make plurals with 'die'",
        ],
        "grammar": [
            G("Every noun has a gender — learn it with the colour",
              "German has three genders. The app colours and shapes them everywhere:\n"
              "■ **der** = masculine (blue square)\n● **die** = feminine (rose circle)\n"
              "▲ **das** = neuter (green triangle)\n◆ **die** = plural (violet diamond, always *die*)\n"
              "Always learn a noun **with** its article: *der Tisch*, never just *Tisch*.",
              [["", "masculine", "feminine", "neuter", "plural"],
               ["the", "der", "die", "das", "die"], ["a", "ein", "eine", "ein", "—"],
               ["no / not a", "kein", "keine", "kein", "keine"]]),
            G("Gender clues from the ending",
              "Not perfect, but very useful:\n**-e** → usually *die* (die Lampe, die Tasche)\n"
              "**-ung, -heit, -keit, -ion** → always *die*\n**-chen, -lein** → always *das* (das Mädchen!)\n"
              "**-er** for people → *der* (der Lehrer)"),
            G("kein = not a / no",
              "To say *not a* or *no*, put **k** in front of *ein*: *Das ist **kein** Apfel.* "
              "Use **nicht** for everything else: *Das Buch ist **nicht** neu.*"),
            G("Your English already knows German",
              "English and German are siblings. About 1,500 years ago some consonants shifted in German, "
              "and the shift is regular. Learn these swaps and you can decode hundreds of words you've never seen:",
              [["English", "German", "Examples"],
               ["t", "z / ss", "ten → **z**ehn · water → Wa**ss**er · eat → e**ss**en"],
               ["d", "t", "door → **T**ür · drink → **t**rinken · old → al**t**"],
               ["p", "f / pf", "apple → A**pf**el · sleep → schla**f**en · ship → Schi**f**f"],
               ["k", "ch", "book → Bu**ch** · make → ma**ch**en · milk → Mil**ch**"],
               ["v", "b", "have → ha**b**en · give → ge**b**en"],
               ["y", "g / j", "day → Ta**g** · year → **J**ahr · way → We**g**"]]),
        ],
        "vocab": [
            N("der Tisch", "table", "m", "die Tische"),
            N("der Stuhl", "chair", "m", "die Stühle"),
            N("der Hund", "dog", "m", "die Hunde"),
            N("der Apfel", "apple", "m", "die Äpfel"),
            N("der Mann", "man", "m", "die Männer"),
            N("die Tür", "door", "f", "die Türen"),
            N("die Lampe", "lamp", "f", "die Lampen"),
            N("die Katze", "cat", "f", "die Katzen"),
            N("die Tasche", "bag", "f", "die Taschen"),
            N("die Frau", "woman", "f", "die Frauen", en_alt=["wife", "Mrs"]),
            N("das Buch", "book", "n", "die Bücher"),
            N("das Haus", "house", "n", "die Häuser"),
            N("das Fenster", "window", "n", "die Fenster"),
            N("das Handy", "mobile phone", "n", "die Handys", en_alt=["phone", "cell phone"]),
            N("das Mädchen", "girl", "n", "die Mädchen"),
            A("groß", "big / tall", en_alt=["big", "tall"]),
            A("klein", "small", en_alt=["little"]),
            A("neu", "new"),
            A("alt", "old"),
        ],
        "sentences": [
            S("Das ist ein Tisch.", "That is a table.", en_alt=["This is a table.", "It's a table."]),
            S("Das ist eine Lampe.", "That is a lamp.", en_alt=["This is a lamp."]),
            S("Das Buch ist neu.", "The book is new."),
            S("Die Katze ist klein.", "The cat is small."),
            S("Der Hund ist groß.", "The dog is big."),
            S("Das ist kein Apfel.", "That is not an apple.", en_alt=["That isn't an apple."]),
            S("Wo ist meine Tasche?", "Where is my bag?"),
            S("Die Bücher sind alt.", "The books are old."),
        ],
        "reading": P(
            "Mein Zimmer",
            "Mein Zimmer ist klein. Da ist ein Tisch und ein Stuhl. Auf dem Tisch ist eine Lampe. "
            "Das Fenster ist groß. Meine Katze schläft auf dem Bett.",
            "My room is small. There is a table and a chair. On the table there is a lamp. "
            "The window is big. My cat sleeps on the bed.",
            [Q("What is on the table?", ["A lamp", "A cat", "A book", "A phone"], 0),
             Q("What is big?", ["The window", "The room", "The table", "The cat"], 0),
             Q("Who sleeps on the bed?", ["The cat", "The dog", "The girl", "Nobody"], 0)],
        ),
        "writing_prompt": "Describe 3 things in the room around you. Use der / die / das and an adjective (groß, klein, neu, alt).",
        "writing_model": "Der Tisch ist groß. Die Lampe ist neu. Das Fenster ist klein.",
    },
    # ------------------------------------------------------------------ 4
    {
        "stage": 4,
        "title": "Numbers & having",
        "native": "Zahlen & haben",
        "can_do": [
            "Count to 100 and give your age",
            "Say what you have with 'haben'",
            "Ask what something costs",
        ],
        "grammar": [
            G("haben = to have",
              "Your second most important verb. Note the small surprise: *du **hast***, *er **hat***.",
              [["", "haben"], ["ich", "habe"], ["du", "hast"], ["er / sie / es", "hat"],
               ["wir", "haben"], ["ihr", "habt"], ["sie / Sie", "haben"]]),
            G("Building numbers 0–100",
              "Learn **0–12** by heart. From 13 it's a pattern: **13–19 = number + zehn**, "
              "**tens = number + zig**. Watch the three little irregulars:",
              [["", "Pattern", "⚠ Irregular"],
               ["13–19", "drei**zehn**, vier**zehn**, fünf**zehn**", "**sech**zehn (16), **sieb**zehn (17)"],
               ["tens", "vier**zig**, fünf**zig**, acht**zig**", "drei**ß**ig (30), **sech**zig, **sieb**zig"],
               ["100", "hundert / einhundert", ""]]),
            G("Numbers 21–99 are said backwards",
              "German says the ones first: **21 = einundzwanzig** (*one-and-twenty*), "
              "**35 = fünfunddreißig**, **99 = neunundneunzig**. It's all one word.\n"
              "Tip for listening: catch the **last** part first (the tens), then add the first part.\n"
              "On the phone, Germans often say **zwo** instead of *zwei* so it isn't confused with *drei*."),
            G("First taste of the accusative",
              "After *haben* the object changes, **but only for masculine nouns**:\n"
              "*Ich habe **einen** Hund.* (der Hund → einen)\n*Ich habe **eine** Katze.* (no change)\n"
              "*Ich habe **ein** Buch.* (no change)"),
        ],
        "vocab": [
            W("null", "zero", "num"),
            W("eins", "one", "num"), W("zwei", "two", "num"), W("drei", "three", "num"),
            W("vier", "four", "num"), W("fünf", "five", "num"), W("sechs", "six", "num"),
            W("sieben", "seven", "num"), W("acht", "eight", "num"), W("neun", "nine", "num"),
            W("zehn", "ten", "num"), W("elf", "eleven", "num"), W("zwölf", "twelve", "num"),
            W("dreizehn", "thirteen", "num"), W("sechzehn", "sixteen", "num"), W("siebzehn", "seventeen", "num"),
            W("zwanzig", "twenty", "num"), W("einundzwanzig", "twenty-one", "num"),
            W("dreißig", "thirty", "num"), W("vierzig", "forty", "num"), W("fünfzig", "fifty", "num"),
            W("sechzig", "sixty", "num"), W("siebzig", "seventy", "num"), W("achtzig", "eighty", "num"),
            W("neunzig", "ninety", "num"),
            W("hundert", "hundred", "num", en_alt=["one hundred"]),
            V("haben", "to have", ["habe", "hast", "hat", "habt"]),
            N("das Jahr", "year", "n", "die Jahre"),
            N("die Zeit", "time", "f", "die Zeiten"),
            V("kosten", "to cost", ["kostet"]),
            W("wie viel", "how much", "q"),
        ],
        "sentences": [
            S("Wie alt bist du?", "How old are you?"),
            S("Ich bin dreißig Jahre alt.", "I am thirty years old.", en_alt=["I'm thirty years old."]),
            S("Sie ist fünfundvierzig Jahre alt.", "She is forty-five years old.", en_alt=["She's forty-five."]),
            S("Das kostet siebzehn Euro.", "That costs seventeen euros.", en_alt=["It costs seventeen euros."]),
            S("Ich habe einen Hund.", "I have a dog.", en_alt=["I've got a dog."]),
            S("Hast du Zeit?", "Do you have time?", en_alt=["Have you got time?"]),
            S("Er hat zwei Katzen.", "He has two cats."),
            S("Wir haben keine Zeit.", "We have no time.", en_alt=["We don't have time."]),
            S("Das kostet fünf Euro.", "That costs five euros.", en_alt=["It costs five euros."]),
            S("Wie viel kostet das?", "How much does that cost?", en_alt=["How much is that?"]),
        ],
        "reading": P(
            "Tom",
            "Tom ist fünfundzwanzig Jahre alt. Er hat einen Bruder und zwei Schwestern. "
            "Sein Bruder ist achtzehn. Tom hat keine Katze, aber er hat einen Hund.",
            "Tom is twenty-five years old. He has a brother and two sisters. His brother is eighteen. "
            "Tom doesn't have a cat, but he has a dog.",
            [Q("How old is Tom?", ["25", "52", "18", "15"], 0),
             Q("How many sisters does he have?", ["Two", "One", "None", "Three"], 0),
             Q("Which pet does Tom have?", ["A dog", "A cat", "Two cats", "No pet"], 0)],
        ),
        "writing_prompt": "Write 3 sentences: how old you are, something you have, and something you don't have (kein/keine).",
        "writing_model": "Ich bin dreißig Jahre alt. Ich habe ein Handy. Ich habe keine Katze.",
    },
    # ------------------------------------------------------------------ 5
    {
        "stage": 5,
        "title": "Family",
        "native": "Die Familie",
        "can_do": [
            "Introduce the members of your family",
            "Use mein, dein, sein, ihr and unser",
            "Ask about someone else's family",
        ],
        "grammar": [
            G("Possessives behave like ein",
              "*mein* (my), *dein* (your), *sein* (his), *ihr* (her), *unser* (our) take the same endings as *ein*:\n"
              "**mein** Vater · **meine** Mutter · **mein** Kind · **meine** Eltern (plural)",
              [["", "masc ■", "fem ●", "neut ▲", "plural ◆"],
               ["my", "mein", "meine", "mein", "meine"], ["your", "dein", "deine", "dein", "deine"],
               ["his", "sein", "seine", "sein", "seine"], ["her", "ihr", "ihre", "ihr", "ihre"]]),
            G("Siblings in one word",
              "*Geschwister* means brothers and sisters together. It is always plural: "
              "*Hast du Geschwister?*"),
        ],
        "vocab": [
            N("die Familie", "family", "f", "die Familien"),
            N("die Mutter", "mother", "f", "die Mütter"),
            N("der Vater", "father", "m", "die Väter"),
            N("die Eltern", "parents", "pl"),
            N("der Bruder", "brother", "m", "die Brüder"),
            N("die Schwester", "sister", "f", "die Schwestern"),
            N("die Geschwister", "siblings", "pl", en_alt=["brothers and sisters"]),
            N("das Kind", "child", "n", "die Kinder"),
            N("der Sohn", "son", "m", "die Söhne"),
            N("die Tochter", "daughter", "f", "die Töchter"),
            N("die Oma", "grandma", "f", "die Omas", en_alt=["grandmother"]),
            N("der Opa", "grandpa", "m", "die Opas", en_alt=["grandfather"]),
            A("verheiratet", "married"),
            W("mein", "my", "det"),
            W("dein", "your (informal)", "det", en_alt=["your"]),
        ],
        "sentences": [
            S("Das ist meine Mutter.", "This is my mother.", en_alt=["That is my mother."]),
            S("Mein Vater heißt Peter.", "My father's name is Peter.", en_alt=["My father is called Peter."]),
            S("Hast du Geschwister?", "Do you have siblings?", en_alt=["Do you have brothers and sisters?"]),
            S("Ich habe einen Bruder.", "I have a brother."),
            S("Meine Schwester ist verheiratet.", "My sister is married."),
            S("Sie hat zwei Kinder.", "She has two children."),
            S("Wie heißt dein Sohn?", "What's your son's name?", en_alt=["What is your son called?"]),
            S("Unsere Eltern wohnen in München.", "Our parents live in Munich."),
        ],
        "reading": P(
            "Meine Familie",
            "Meine Familie ist nicht groß. Mein Vater heißt Klaus und meine Mutter heißt Petra. "
            "Ich habe eine Schwester. Sie heißt Julia und sie ist verheiratet. Julia hat einen Sohn, Ben. "
            "Ben ist drei Jahre alt.",
            "My family is not big. My father is called Klaus and my mother is called Petra. I have a sister. "
            "She is called Julia and she is married. Julia has a son, Ben. Ben is three years old.",
            [Q("What is the mother's name?", ["Petra", "Julia", "Klaus", "Ben"], 0),
             Q("Who is married?", ["Julia", "Ben", "The writer", "Nobody"], 0),
             Q("Who is Ben?", ["Julia's son", "The father", "The brother", "Julia's husband"], 0)],
        ),
        "writing_prompt": "Describe your family in 4 sentences. Use mein/meine and say a name or an age.",
        "writing_model": "Meine Familie ist klein. Meine Mutter heißt Ada. Ich habe einen Bruder. Er ist zwanzig Jahre alt.",
    },
    # ------------------------------------------------------------------ 6
    {
        "stage": 6,
        "title": "My day",
        "native": "Mein Tag",
        "can_do": [
            "Describe your daily routine",
            "Use regular, stem-changing and separable verbs",
            "Start a sentence with a time word and keep the verb 2nd",
        ],
        "grammar": [
            G("Some verbs change their vowel",
              "With *du* and *er/sie/es* a few common verbs change their stem vowel:\n"
              "**essen** → du **isst**, er **isst** · **schlafen** → du **schläfst**, er **schläft** · "
              "**nehmen** → du **nimmst**, er **nimmt**"),
            G("Separable verbs split in two",
              "Verbs like **aufstehen** (to get up) break apart. The prefix jumps to the **end**:\n"
              "*Ich* **stehe** *um sieben Uhr* **auf**.\nThink of it as a sentence bracket: verb … prefix."),
            G("Time first? The verb is still 2nd",
              "If you start with *Heute*, *Morgen* or *Um acht Uhr*, the verb stays in position 2 and the subject "
              "moves behind it:\n*Ich spiele heute Fußball.* → ***Heute*** **spiele** *ich Fußball.*"),
        ],
        "vocab": [
            V("arbeiten", "to work", ["arbeite", "arbeitest", "arbeitet"]),
            V("lernen", "to learn", ["lerne", "lernst", "lernt"]),
            V("machen", "to do / to make", ["mache", "machst", "macht"], en_alt=["to do", "to make"]),
            V("spielen", "to play", ["spiele", "spielst", "spielt"]),
            V("trinken", "to drink", ["trinke", "trinkst", "trinkt"]),
            V("essen", "to eat", ["esse", "isst", "esst"]),
            V("schlafen", "to sleep", ["schlafe", "schläfst", "schläft"]),
            V("aufstehen", "to get up", ["stehe", "stehst", "steht", "auf"]),
            V("gehen", "to go", ["gehe", "gehst", "geht"]),
            A("heute", "today"),
            A("morgen", "tomorrow"),
            A("oft", "often"),
            A("gern", "gladly / like to", en_alt=["gladly"]),
            N("die Uhr", "clock / o'clock", "f", "die Uhren", en_alt=["clock", "o'clock"]),
        ],
        "sentences": [
            S("Ich lerne Deutsch.", "I am learning German.", en_alt=["I learn German.", "I'm learning German."]),
            S("Was machst du heute?", "What are you doing today?"),
            S("Er arbeitet in Köln.", "He works in Cologne."),
            S("Ich stehe um sieben Uhr auf.", "I get up at seven o'clock.", alt=["Um sieben Uhr stehe ich auf."]),
            S("Heute spiele ich Fußball.", "Today I am playing football.",
              alt=["Ich spiele heute Fußball."], en_alt=["I'm playing football today."]),
            S("Sie trinkt gern Kaffee.", "She likes to drink coffee.", en_alt=["She likes drinking coffee."]),
            S("Wir essen um acht Uhr.", "We eat at eight o'clock."),
            S("Schläfst du gut?", "Do you sleep well?"),
        ],
        "reading": P(
            "Mein Tag",
            "Ich stehe um sechs Uhr auf. Ich trinke einen Kaffee und esse ein Brot. "
            "Um acht Uhr arbeite ich. Am Abend lerne ich Deutsch. Dann schlafe ich – gut!",
            "I get up at six o'clock. I drink a coffee and eat some bread. At eight o'clock I work. "
            "In the evening I learn German. Then I sleep – well!",
            [Q("When does the writer get up?", ["At six", "At seven", "At eight", "At nine"], 0),
             Q("What do they do in the evening?", ["Learn German", "Play football", "Work", "Drink coffee"], 0)],
        ),
        "writing_prompt": "Describe your day in 4 sentences. Start at least one sentence with a time (Um … Uhr / Heute).",
        "writing_model": "Ich stehe um sieben Uhr auf. Um acht Uhr trinke ich Kaffee. Heute arbeite ich. Am Abend lerne ich Deutsch.",
    },
    # ------------------------------------------------------------------ 7
    {
        "stage": 7,
        "title": "Food & drink",
        "native": "Essen & Trinken",
        "can_do": [
            "Order food and drink in a café",
            "Say what you'd like with 'möchten'",
            "Use the accusative (den / einen) when ordering",
        ],
        "grammar": [
            G("Ordering = accusative",
              "What you order is the *object*. Only masculine nouns change:\n"
              "*der Kaffee* → *Ich möchte **einen** Kaffee.*\n*die Suppe* → *Ich nehme **die** Suppe.*",
              [["", "masc ■", "fem ●", "neut ▲"], ["subject", "der / ein", "die / eine", "das / ein"],
               ["object (acc.)", "**den / einen**", "die / eine", "das / ein"]]),
            G("möchten = would like",
              "The polite way to order: *ich **möchte**, du **möchtest**, er **möchte***. "
              "A second verb goes to the **end**: *Was möchtest du **trinken**?*"),
            G("kein or nicht?",
              "**kein** replaces *ein* or no article: *Ich esse **kein** Fleisch.*\n"
              "**nicht** negates everything else: *Der Kaffee ist **nicht** heiß.*"),
        ],
        "vocab": [
            N("das Brot", "bread", "n", "die Brote"),
            N("der Kaffee", "coffee", "m"),
            N("der Tee", "tea", "m"),
            N("das Wasser", "water", "n"),
            N("die Milch", "milk", "f"),
            N("der Käse", "cheese", "m"),
            N("das Ei", "egg", "n", "die Eier"),
            N("die Suppe", "soup", "f", "die Suppen"),
            N("das Bier", "beer", "n"),
            N("der Kuchen", "cake", "m", "die Kuchen"),
            N("das Fleisch", "meat", "n"),
            N("die Rechnung", "bill", "f", "die Rechnungen", en_alt=["check", "invoice"]),
            V("möchten", "would like", ["möchte", "möchtest"]),
            V("nehmen", "to take / to have (food)", ["nehme", "nimmst", "nimmt"], en_alt=["to take"]),
            A("lecker", "tasty", en_alt=["delicious"]),
        ],
        "sentences": [
            S("Ich möchte einen Kaffee, bitte.", "I would like a coffee, please.", en_alt=["I'd like a coffee, please."]),
            S("Ich nehme die Suppe.", "I'll have the soup.", en_alt=["I'll take the soup."]),
            S("Was möchtest du trinken?", "What would you like to drink?"),
            S("Ich esse kein Fleisch.", "I don't eat meat."),
            S("Die Rechnung, bitte!", "The bill, please!", en_alt=["The check, please!"]),
            S("Der Kuchen ist sehr lecker.", "The cake is very tasty.", en_alt=["The cake is very delicious."]),
            S("Haben Sie Wasser?", "Do you have water?", en_alt=["Have you got water?"]),
            S("Zusammen oder getrennt?", "Together or separately?", en_alt=["Together or separate?"]),
        ],
        "reading": P(
            "Im Café",
            "Kellner: Guten Tag! Was möchten Sie?\nGast: Ich möchte einen Tee und einen Kuchen, bitte.\n"
            "Kellner: Mit Milch?\nGast: Nein, danke. Ohne Milch.\nKellner: Gern. Sonst noch etwas?\n"
            "Gast: Nein, das ist alles. Die Rechnung, bitte!",
            "Waiter: Hello! What would you like? / Guest: I'd like a tea and a cake, please. / Waiter: With milk? / "
            "Guest: No, thank you. Without milk. / Waiter: Sure. Anything else? / Guest: No, that's all. The bill, please!",
            [Q("What does the guest order?", ["Tea and cake", "Coffee and cake", "Tea with milk", "Soup"], 0),
             Q("Does the guest want milk?", ["No", "Yes", "Only a little", "They don't say"], 0)],
        ),
        "writing_prompt": "You're in a café. Write 3–4 lines ordering a drink and some food, and ask for the bill.",
        "writing_model": "Guten Tag! Ich möchte einen Kaffee und ein Brot, bitte. Ich esse kein Fleisch. Die Rechnung, bitte!",
    },
    # ------------------------------------------------------------------ 8
    {
        "stage": 8,
        "title": "Time & days",
        "native": "Uhrzeit & Wochentage",
        "can_do": [
            "Tell the time, including the tricky 'halb'",
            "Name the days and make plans",
            "Use am (days) and um (clock times)",
        ],
        "grammar": [
            G("halb means half TO the next hour",
              "⚠ The classic trap: **halb drei** = **2:30** (half *towards* three), not 3:30.\n"
              "*Viertel nach drei* = 3:15 · *Viertel vor drei* = 2:45"),
            G("am + day, um + time",
              "**am** Montag (on Monday) · **um** acht Uhr (at eight) · **am** Wochenende (at the weekend).\n"
              "All days are masculine: *der Montag*."),
        ],
        "vocab": [
            N("der Montag", "Monday", "m"), N("der Dienstag", "Tuesday", "m"),
            N("der Mittwoch", "Wednesday", "m"), N("der Donnerstag", "Thursday", "m"),
            N("der Freitag", "Friday", "m"), N("der Samstag", "Saturday", "m"),
            N("der Sonntag", "Sunday", "m"),
            N("die Woche", "week", "f", "die Wochen"),
            N("das Wochenende", "weekend", "n", "die Wochenenden"),
            N("die Stunde", "hour", "f", "die Stunden"),
            A("spät", "late"),
            A("früh", "early"),
            W("halb", "half", "num"),
            V("beginnen", "to begin / to start", ["beginne", "beginnst", "beginnt"], en_alt=["to start", "to begin"]),
        ],
        "sentences": [
            S("Wie spät ist es?", "What time is it?"),
            S("Es ist halb drei.", "It's half past two.", en_alt=["It is two thirty.", "It is half past two."]),
            S("Am Montag arbeite ich.", "On Monday I work.", alt=["Ich arbeite am Montag."], en_alt=["I work on Monday."]),
            S("Der Kurs beginnt um neun Uhr.", "The course starts at nine o'clock.", en_alt=["The class begins at nine."]),
            S("Am Wochenende habe ich Zeit.", "At the weekend I have time.", alt=["Ich habe am Wochenende Zeit."],
              en_alt=["On the weekend I have time."]),
            S("Hast du am Freitag Zeit?", "Are you free on Friday?", en_alt=["Do you have time on Friday?"]),
            S("Bis morgen!", "See you tomorrow!", en_alt=["Until tomorrow!"]),
        ],
        "reading": P(
            "Meine Woche",
            "Am Montag und am Dienstag arbeite ich bis fünf Uhr. Am Mittwoch lerne ich Deutsch – der Kurs beginnt "
            "um halb sieben. Am Freitag spiele ich Fußball. Am Wochenende schlafe ich lange!",
            "On Monday and Tuesday I work until five o'clock. On Wednesday I learn German – the course starts at "
            "half past six. On Friday I play football. At the weekend I sleep in!",
            [Q("When does the German course start?", ["6:30", "7:30", "5:00", "6:00"], 0),
             Q("What happens on Friday?", ["Football", "German course", "Work until five", "Sleeping in"], 0)],
        ),
        "writing_prompt": "Write your plan for next week: 4 sentences using am + day and um + time.",
        "writing_model": "Am Montag arbeite ich. Am Dienstag lerne ich um sieben Uhr Deutsch. Am Freitag habe ich Zeit. Am Sonntag schlafe ich lange.",
    },
]
