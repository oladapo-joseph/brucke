"""French A1 — hand-written units for stages 1–8.

French starts two weeks after German, so these notes link back to German where it helps
(ü = u, the throaty r, halb drei vs deux heures et demie, …).
"""
from .schema import A, G, L, N, P, Q, S, SND, V, W

UNITS = [
    # ------------------------------------------------------------------ 1
    {
        "stage": 1,
        "title": "Sounds & Letters",
        "native": "Les sons",
        "can_do": [
            "Say the alphabet and spell your name out loud, accents included",
            "Know which letters are silent at the end of a word",
            "Make the three nasal vowels: an, on, in",
            "Greet people politely",
        ],
        "grammar": [
            G("The alphabet: same letters, new names",
              "French uses the same 26 letters as English. The *names* differ, and some names are swapped "
              "compared with English: French **G** sounds like English *J*, and French **J** sounds like English *G*. "
              "You'll also meet letter names you already know from German.",
              [["Letter", "French name", "Sounds like", "⚠ Watch out"],
               ["E", "e", "*uh*", "not English E"],
               ["I", "i", "*ee*", "English E"],
               ["G", "gé", "*zhay*", "sounds like English J"],
               ["J", "ji", "*zhee*", "sounds like English G"],
               ["U", "u", "German *ü*", "not *you*"],
               ["H", "hache", "*ash*", "and h is silent in words"],
               ["W", "double vé", "*doo-bluh-vay*", "a 'double V', not 'double U'"],
               ["Y", "i grec", "*ee-grek*", "'Greek i'"]], at="letters"),
            G("Spelling out loud",
              "French spells accents out loud: *café* = **C – A – F – E accent aigu**.\n"
              "**Comment ça s'écrit ?** = How do you spell that?\n"
              "**Vous pouvez épeler, s'il vous plaît ?** = Can you spell it, please?\n"
              "For a double letter, say **deux**: *Anne* = **A – deux N – E**.", at="sentences"),
            G("The last letter is often silent",
              "French writes more than it says. A final **-s, -t, -d, -x, -e** is usually silent: "
              "*peti~~t~~*, *Pari~~s~~*, *gran~~d~~*. Exceptions: **c, r, f, l** are often spoken "
              "(think **CaReFuL**): *sac*, *bonjour*, *neuf*, *sel*.", at="sounds"),
            G("Nasal vowels: air through the nose",
              "When a vowel is followed by **n** or **m** (and then no vowel), you don't say the n. "
              "The vowel goes through your nose instead.",
              [["Spelling", "Sound", "Example"], ["an / en", "nasal 'ah'", "enfant"],
               ["on", "nasal 'oh'", "bonjour"], ["in / ain / un", "nasal 'a' (as in *bag*)", "vin"]]),
            G("You already know two sounds from German",
              "French **u** (*tu*) = German **ü** (*müde*): say *ee* with round lips.\n"
              "French **eu** (*deux*) ≈ German **ö** (*schön*).\nThe French **r** is gargled in the throat, like the German one."),
            G("Accents are part of the spelling",
              "**é** = crisp *ay* (café) · **è / ê** = *e* in *bed* (fête) · **ç** = soft *s* (garçon).\n"
              "Use the accent bar, or the app will flag a missing accent as a small 'accents' slip.\n"
              "When you spell a word, you name the accent: **é** = *e accent aigu*, **è** = *e accent grave*, "
              "**ê** = *e accent circonflexe*, **ç** = *c cédille*.", at="letters:last"),
        ],
        "letters": [
            L("A", "a", "ah", "ami", "friend", "ER"),
            L("B", "bé", "bay", "bonjour", "hello", "PDV"),
            L("C", "cé", "say", "carte", "card / map", "SK", "C is called 'say', like the English word."),
            L("D", "dé", "day", "dix", "ten", "TB"),
            L("E", "e", "uh", "euro", "euro", "IAU", "The French E is a short 'uh', not English 'ee'.", say="e"),
            L("F", "effe", "eff", "fille", "girl / daughter", "VS"),
            L("G", "gé", "zhay (like English J!)", "gare", "train station", "JK", "G is called 'zhay'. It sounds like the English letter J.", say="gé"),
            L("H", "hache", "ash", "homme", "man", "AK", "H is called 'ash', and it's silent in words: homme = 'om'.", say="hache"),
            L("I", "i", "ee (like English E!)", "ici", "here", "EY", "The French I sounds like the English letter E."),
            L("J", "ji", "zhee (like English G!)", "jour", "day", "GI", "J is called 'zhee'. It sounds like the English letter G.", say="ji"),
            L("K", "ka", "kah", "kilo", "kilo", "QC"),
            L("L", "elle", "el", "lait", "milk", "R"),
            L("M", "emme", "em", "main", "hand", "N"),
            L("N", "enne", "en", "nuit", "night", "M"),
            L("O", "o", "oh", "oui", "yes", "U"),
            L("P", "pé", "pay", "pain", "bread", "BT"),
            L("Q", "qu", "kü", "quatre", "four", "KU", "Q is called 'kü' (with the German ü sound)."),
            L("R", "erre", "air (throaty)", "rouge", "red", "LA"),
            L("S", "esse", "ess", "soleil", "sun", "CZ"),
            L("T", "té", "tay", "table", "table", "DP"),
            L("U", "u", "German ü", "une", "one / a", "OIQ", "U sounds like German ü: say 'ee' with round lips."),
            L("V", "vé", "vay", "vin", "wine", "WB"),
            L("W", "double vé", "doo-bluh-vay", "wagon", "train carriage", "VY", "W is literally 'double V' in French.", say="double vé"),
            L("X", "ixe", "eeks", "xylophone", "xylophone", "SZ"),
            L("Y", "i grec", "ee-grek", "yaourt", "yogurt", "IJ", "Y is 'i grec': 'Greek i'.", say="i grec"),
            L("Z", "zède", "zed", "zoo", "zoo", "SX", say="zède"),
            L("é", "e accent aigu", "ay", "café", "coffee", "èêE", "Spell it as 'e accent aigu' (acute accent).", say="e accent aigu"),
            L("è", "e accent grave", "eh", "mère", "mother", "éêE", "Spell it as 'e accent grave' (grave accent).", say="e accent grave"),
            L("ê", "e accent circonflexe", "eh", "fête", "party", "éèE", "The 'hat' on ê: 'e accent circonflexe'.", say="e accent circonflexe"),
            L("ç", "c cédille", "s", "garçon", "boy", "CS", "The hook under ç: 'c cédille'. It makes c sound like s.", say="c cédille"),
        ],
        "sounds": [
            SND("é", "café", "coffee", "A crisp 'ay', shorter than in English 'say'."),
            SND("è / ê", "fête", "party", "Like the 'e' in 'bed'."),
            SND("u", "tu", "you", "Same as German ü: say 'ee' with rounded lips."),
            SND("ou", "vous", "you (formal)", "Like 'oo' in 'food'."),
            SND("oi", "moi", "me", "Sounds like 'wa'."),
            SND("an / en", "enfant", "child", "Nasal 'ah'. Don't say the n."),
            SND("on", "bonjour", "hello", "Nasal 'oh'."),
            SND("in / ain", "vin", "wine", "Nasal 'a' as in 'bag'."),
            SND("eau / au", "beau", "beautiful", "A pure 'oh'."),
            SND("ch", "chat", "cat", "Like English 'sh'."),
            SND("gn", "montagne", "mountain", "Like 'ny' in 'canyon'."),
            SND("ç", "garçon", "boy", "The cedilla makes c a soft 's'."),
            SND("r", "rouge", "red", "A soft gargle in the throat, like German r."),
            SND("eu", "deux", "two", "Close to German ö."),
            SND("silent end", "petit", "small", "The final t is silent: 'puh-tee'."),
        ],
        "vocab": [
            W("bonjour", "hello / good morning", en_alt=["hello", "good morning", "good day"]),
            W("bonsoir", "good evening"),
            W("salut", "hi / bye (informal)", en_alt=["hi"]),
            W("au revoir", "goodbye"),
            W("merci", "thank you", en_alt=["thanks"]),
            W("s'il vous plaît", "please (formal)", en_alt=["please"]),
            W("oui", "yes"),
            W("non", "no"),
            W("pardon", "sorry / pardon", en_alt=["sorry", "pardon"]),
            W("excusez-moi", "excuse me"),
            W("à bientôt", "see you soon"),
        ],
        "sentences": [
            S("Merci beaucoup !", "Thank you very much!", en_alt=["Thanks a lot!"]),
            S("De rien.", "You're welcome."),
            S("Pardon ?", "Pardon?", en_alt=["Sorry?"]),
            S("Oui, s'il vous plaît.", "Yes, please."),
            S("Non, merci.", "No, thank you.", en_alt=["No, thanks."]),
            S("Bonne journée !", "Have a nice day!", en_alt=["Have a good day!"]),
            S("Comment ça s'écrit ?", "How do you spell that?", en_alt=["How is that written?"]),
            S("Vous pouvez épeler, s'il vous plaît ?", "Can you spell it, please?", en_alt=["Could you spell it, please?"]),
        ],
        "reading": P(
            "À la boulangerie",
            "Client : Bonjour madame !\nBoulangère : Bonjour monsieur ! Un croissant ?\n"
            "Client : Oui, s'il vous plaît. Merci beaucoup !\nBoulangère : De rien. Bonne journée !\nClient : Au revoir !",
            "Customer: Hello madam! / Baker: Hello sir! A croissant? / Customer: Yes, please. Thank you very much! / "
            "Baker: You're welcome. Have a nice day! / Customer: Goodbye!",
            [Q("What is the customer offered?", ["A croissant", "A coffee", "Bread", "Wine"], 0),
             Q("What does the baker wish the customer?", ["A nice day", "Good evening", "Good luck", "See you soon"], 0)],
        ),
        "writing_prompt": "Write a tiny dialogue at a bakery: greet, accept something politely, thank, and say goodbye.",
        "writing_model": "Bonjour ! – Un café ? – Oui, s'il vous plaît. Merci beaucoup ! – De rien. – Au revoir !",
    },
    # ------------------------------------------------------------------ 2
    {
        "stage": 2,
        "title": "Hello, I am…",
        "native": "Bonjour, je suis…",
        "can_do": [
            "Say your name, where you come from and where you live",
            "Choose between tu and vous",
            "Use être (to be) and regular -er verbs",
        ],
        "grammar": [
            G("être = to be",
              "Irregular and essential. Notice that many forms *sound* alike: *es* and *est* are both 'eh'.",
              [["", "être"], ["je", "suis"], ["tu", "es"], ["il / elle", "est"],
               ["nous", "sommes"], ["vous", "êtes"], ["ils / elles", "sont"]]),
            G("je → j' before a vowel",
              "French hates two vowels colliding: *je habite* → **j'habite**. "
              "Same for *le/la → l'*, *de → d'*, *me → m'*."),
            G("tu or vous?",
              "**tu** = friends, family, kids (like German *du*). **vous** = formal *or* plural (like *Sie*/*ihr*).\n"
              "No article before a job: *Je suis **étudiant**.* (not *un étudiant*)"),
        ],
        "vocab": [
            W("je", "I", "pron"), W("tu", "you (informal)", "pron"), W("vous", "you (formal / plural)", "pron"),
            W("il", "he", "pron"), W("elle", "she", "pron"), W("nous", "we", "pron"),
            V("être", "to be", ["suis", "es", "est", "sommes", "êtes", "sont"]),
            V("s'appeler", "to be called", ["appelle", "appelles", "appelez"]),
            V("habiter", "to live (reside)", ["habite", "habites", "habitons", "habitez"], en_alt=["to live"]),
            V("venir", "to come", ["viens", "vient", "venez"]),
            W("où", "where", "q"),
            W("comment", "how", "q"),
            N("le nom", "name", "m", "les noms"),
            N("le pays", "country", "m", "les pays"),
            N("la ville", "city / town", "f", "les villes", en_alt=["city", "town"]),
        ],
        "sentences": [
            S("Je m'appelle Léa.", "My name is Léa.", en_alt=["I am called Léa."]),
            S("Tu t'appelles comment ?", "What's your name?", alt=["Comment tu t'appelles ?"], en_alt=["What is your name?"]),
            S("Comment vous appelez-vous ?", "What's your name? (formal)", en_alt=["What is your name?"]),
            S("Je suis étudiant.", "I am a student.", alt=["Je suis étudiante."], en_alt=["I'm a student."]),
            S("Tu viens d'où ?", "Where are you from?", alt=["D'où viens-tu ?"], en_alt=["Where do you come from?"]),
            S("Je viens d'Angleterre.", "I come from England.", en_alt=["I'm from England."]),
            S("J'habite à Paris.", "I live in Paris."),
            S("Tu habites où ?", "Where do you live?", alt=["Où habites-tu ?"]),
            S("Enchanté !", "Nice to meet you!", alt=["Enchantée !"], en_alt=["Pleased to meet you!"]),
        ],
        "reading": P(
            "C'est moi",
            "Bonjour ! Je m'appelle Camille. Je viens de Belgique, mais j'habite à Lyon. "
            "Je suis professeure. Et toi ? Tu t'appelles comment ? Tu viens d'où ?",
            "Hello! My name is Camille. I come from Belgium, but I live in Lyon. I am a teacher. "
            "And you? What's your name? Where are you from?",
            [Q("Where does Camille come from?", ["Belgium", "Lyon", "England", "Paris"], 0),
             Q("Where does she live?", ["Lyon", "Brussels", "Paris", "Belgium"], 0),
             Q("What is her job?", ["Teacher", "Student", "Baker", "Doctor"], 0)],
        ),
        "writing_prompt": "Introduce yourself in 3 sentences: your name, where you come from, and where you live.",
        "writing_model": "Je m'appelle Sam. Je viens d'Angleterre. J'habite à Londres.",
    },
    # ------------------------------------------------------------------ 3
    {
        "stage": 3,
        "title": "Things & their gender",
        "native": "Le, la, les",
        "can_do": [
            "Name everyday objects with le / la / l'",
            "Use un / une / des",
            "Say what something is not with ne … pas",
        ],
        "grammar": [
            G("Two genders, same colours",
              "French has only two genders: ■ **le** (masculine, blue) and ● **la** (feminine, rose). "
              "Before a vowel both become **l'**, which hides the gender, so the app still shows the colour.\n"
              "◆ **les** = plural.",
              [["", "masc ■", "fem ●", "plural ◆"], ["the", "le / l'", "la / l'", "les"], ["a / some", "un", "une", "des"]]),
            G("⚠ Gender does NOT carry over from German",
              "*der Tisch* (m) → *la table* (f) · *das Buch* (n) → *le livre* (m) · *die Tür* (f) → *la porte* (f).\n"
              "Learn each French noun with **its own** article and colour."),
            G("Ending clues",
              "**-tion, -té, -ette, -ure, -ence** → usually *la*\n**-ment, -age, -eau, -isme** → usually *le*"),
            G("ne … pas wraps the verb",
              "Negation is a sandwich around the verb: *Ce **n'**est **pas** une pomme.* · *Je **ne** suis **pas** prof.*"),
            G("Your English already knows French",
              "After 1066, French was spoken at the English court for 300 years, so around **a third of English words come from French**. "
              "These patterns let you guess new words:",
              [["French", "English", "Examples"],
               ["-tion", "-tion", "la nation, l'addition, la question"],
               ["-té", "-ty", "la liberté → liberty · la qualité → quality"],
               ["-eux / -euse", "-ous", "délicieux → delicious · nerveux → nervous"],
               ["é- at the start", "s-", "l'école → school · l'étudiant → student"],
               ["ê / â / ô (circumflex)", "a lost **s**", "la fenêtre → fenestra · la forêt → forest · l'hôpital → hospital"],
               ["-ment", "-ly", "rapidement → rapidly · finalement → finally"]]),
        ],
        "vocab": [
            N("le livre", "book", "m", "les livres"),
            N("le chat", "cat", "m", "les chats"),
            N("le chien", "dog", "m", "les chiens"),
            N("le stylo", "pen", "m", "les stylos"),
            N("le téléphone", "phone", "m", "les téléphones"),
            N("le sac", "bag", "m", "les sacs"),
            N("la table", "table", "f", "les tables"),
            N("la chaise", "chair", "f", "les chaises"),
            N("la porte", "door", "f", "les portes"),
            N("la maison", "house", "f", "les maisons", en_alt=["home"]),
            N("la fenêtre", "window", "f", "les fenêtres"),
            N("la pomme", "apple", "f", "les pommes"),
            N("l'école", "school", "f", "les écoles"),
            N("l'arbre", "tree", "m", "les arbres"),
            A("grand", "big / tall", en_alt=["big", "tall"]),
            A("petit", "small", en_alt=["little"]),
        ],
        "sentences": [
            S("C'est un livre.", "It's a book.", en_alt=["That is a book.", "This is a book."]),
            S("C'est une chaise.", "It's a chair.", en_alt=["That is a chair."]),
            S("La maison est grande.", "The house is big."),
            S("Le chat est petit.", "The cat is small."),
            S("Ce n'est pas une pomme.", "It's not an apple.", en_alt=["That is not an apple."]),
            S("Où est mon sac ?", "Where is my bag?"),
            S("Les livres sont sur la table.", "The books are on the table."),
            S("Il y a une lampe.", "There is a lamp."),
        ],
        "reading": P(
            "Ma chambre",
            "Ma chambre est petite. Il y a une table et une chaise. Sur la table, il y a un livre et un stylo. "
            "La fenêtre est grande. Mon chat dort sur le lit.",
            "My room is small. There is a table and a chair. On the table there is a book and a pen. "
            "The window is big. My cat sleeps on the bed.",
            [Q("What is on the table?", ["A book and a pen", "A lamp", "The cat", "A phone"], 0),
             Q("What is big?", ["The window", "The room", "The table", "The bed"], 0),
             Q("Where does the cat sleep?", ["On the bed", "On the table", "On the chair", "Outside"], 0)],
        ),
        "writing_prompt": "Describe 3 things around you with le / la and an adjective (grand(e), petit(e)).",
        "writing_model": "La table est grande. Le livre est petit. Il y a une chaise.",
    },
    # ------------------------------------------------------------------ 4
    {
        "stage": 4,
        "title": "Numbers & having",
        "native": "Les nombres & avoir",
        "can_do": [
            "Count and give your age (with avoir!)",
            "Say what you have and don't have",
            "Ask how much something costs",
        ],
        "grammar": [
            G("avoir = to have",
              "", [["", "avoir"], ["j'", "ai"], ["tu", "as"], ["il / elle", "a"],
                   ["nous", "avons"], ["vous", "avez"], ["ils / elles", "ont"]]),
            G("Numbers 0–69: mostly regular",
              "Learn **0–16** by heart (*onze, douze, treize, quatorze, quinze, seize*). "
              "From 17 you join with a hyphen: **dix-sept, dix-huit, dix-neuf**.\n"
              "Tens: *vingt, trente, quarante, cinquante, soixante*. Add the ones with a hyphen: **trente-deux**, "
              "except for 1, which takes **et**: **vingt et un**, **trente et un**."),
            G("70–99: French counts in twenties",
              "Here French gets creative. There's no word for 70, 80 or 90 (in France):\n"
              "**70 = soixante-dix** (*sixty-ten*) · **80 = quatre-vingts** (*four-twenties*) · "
              "**90 = quatre-vingt-dix** (*four-twenties-ten*).",
              [["Number", "French", "Literally"],
               ["70", "soixante-dix", "60 + 10"], ["71", "soixante et onze", "60 + 11"],
               ["75", "soixante-quinze", "60 + 15"], ["80", "quatre-vingts", "4 × 20"],
               ["81", "quatre-vingt-un", "4 × 20 + 1 (no s, no et)"], ["90", "quatre-vingt-dix", "4 × 20 + 10"],
               ["99", "quatre-vingt-dix-neuf", "4 × 20 + 19"]]),
            G("Age uses 'have', not 'be'",
              "French says *I **have** thirty years*: **J'ai trente ans.**\n"
              "(German uses *sein* like English: *Ich bin dreißig*. Watch the switch!)"),
            G("After a negative: de",
              "*un, une, des* become **de / d'** after *ne … pas*:\n*J'ai **un** chien.* → *Je n'ai **pas de** chien.*"),
        ],
        "vocab": [
            W("zéro", "zero", "num"),
            W("un", "one", "num"), W("deux", "two", "num"), W("trois", "three", "num"),
            W("quatre", "four", "num"), W("cinq", "five", "num"), W("six", "six", "num"),
            W("sept", "seven", "num"), W("huit", "eight", "num"), W("neuf", "nine", "num"),
            W("dix", "ten", "num"), W("onze", "eleven", "num"), W("douze", "twelve", "num"),
            W("treize", "thirteen", "num"), W("quatorze", "fourteen", "num"), W("quinze", "fifteen", "num"),
            W("seize", "sixteen", "num"), W("dix-sept", "seventeen", "num"),
            W("vingt", "twenty", "num"), W("vingt et un", "twenty-one", "num", alt=["vingt-et-un"]),
            W("trente", "thirty", "num"), W("quarante", "forty", "num"), W("cinquante", "fifty", "num"),
            W("soixante", "sixty", "num"), W("soixante-dix", "seventy", "num"),
            W("quatre-vingts", "eighty", "num"), W("quatre-vingt-dix", "ninety", "num"),
            W("cent", "hundred", "num", en_alt=["one hundred"]),
            V("avoir", "to have", ["ai", "as", "a", "avons", "avez", "ont"]),
            N("l'an", "year", "m", "les ans"),
            N("le temps", "time", "m", en_alt=["weather"]),
            W("combien", "how much / how many", "q", en_alt=["how much", "how many"]),
        ],
        "sentences": [
            S("Tu as quel âge ?", "How old are you?", alt=["Quel âge as-tu ?"]),
            S("J'ai trente ans.", "I am thirty years old.", en_alt=["I'm thirty."]),
            S("Elle a quarante-cinq ans.", "She is forty-five years old.", en_alt=["She's forty-five."]),
            S("Ça coûte soixante-dix euros.", "That costs seventy euros.", en_alt=["It costs seventy euros."]),
            S("J'ai un chien.", "I have a dog.", en_alt=["I've got a dog."]),
            S("Tu as le temps ?", "Do you have time?"),
            S("Il a deux chats.", "He has two cats."),
            S("Nous n'avons pas de temps.", "We have no time.", en_alt=["We don't have time."]),
            S("Ça coûte cinq euros.", "That costs five euros.", en_alt=["It costs five euros."]),
            S("C'est combien ?", "How much is it?", en_alt=["How much is that?"]),
        ],
        "reading": P(
            "Hugo",
            "Hugo a vingt-cinq ans. Il a un frère et deux sœurs. Son frère a dix-huit ans. "
            "Hugo n'a pas de chat, mais il a un chien.",
            "Hugo is twenty-five years old. He has a brother and two sisters. His brother is eighteen. "
            "Hugo doesn't have a cat, but he has a dog.",
            [Q("How old is Hugo?", ["25", "18", "52", "15"], 0),
             Q("How many sisters does he have?", ["Two", "One", "None", "Three"], 0),
             Q("Which pet does Hugo have?", ["A dog", "A cat", "Two cats", "No pet"], 0)],
        ),
        "writing_prompt": "Write 3 sentences: your age, something you have, and something you don't have (pas de).",
        "writing_model": "J'ai trente ans. J'ai un téléphone. Je n'ai pas de chat.",
    },
    # ------------------------------------------------------------------ 5
    {
        "stage": 5,
        "title": "Family",
        "native": "La famille",
        "can_do": [
            "Introduce the members of your family",
            "Use mon / ma / mes and son / sa / ses",
            "Ask about someone else's family",
        ],
        "grammar": [
            G("Possessives match the THING, not the owner",
              "*sa mère* = **his** mother **or** her mother. *Sa* is feminine because **mère** is feminine.\n"
              "Before a vowel, use *mon/ton/son* even for feminine words: **mon** amie.",
              [["", "masc ■", "fem ●", "plural ◆"], ["my", "mon", "ma", "mes"], ["your (tu)", "ton", "ta", "tes"],
               ["his / her", "son", "sa", "ses"], ["our", "notre", "notre", "nos"]]),
        ],
        "vocab": [
            N("la famille", "family", "f", "les familles"),
            N("la mère", "mother", "f", "les mères"),
            N("le père", "father", "m", "les pères"),
            N("les parents", "parents", "pl"),
            N("le frère", "brother", "m", "les frères"),
            N("la sœur", "sister", "f", "les sœurs"),
            N("l'enfant", "child", "m", "les enfants"),
            N("le fils", "son", "m", "les fils"),
            N("la fille", "daughter / girl", "f", "les filles", en_alt=["daughter", "girl"]),
            N("la grand-mère", "grandmother", "f", "les grands-mères", en_alt=["grandma"]),
            N("le grand-père", "grandfather", "m", "les grands-pères", en_alt=["grandpa"]),
            A("marié", "married"),
            W("mon", "my (masc.)", "det", en_alt=["my"]),
            W("ma", "my (fem.)", "det", en_alt=["my"]),
        ],
        "sentences": [
            S("C'est ma mère.", "This is my mother.", en_alt=["That is my mother."]),
            S("Mon père s'appelle Pierre.", "My father's name is Pierre.", en_alt=["My father is called Pierre."]),
            S("Tu as des frères et sœurs ?", "Do you have siblings?", en_alt=["Do you have brothers and sisters?"]),
            S("J'ai un frère.", "I have a brother."),
            S("Ma sœur est mariée.", "My sister is married."),
            S("Elle a deux enfants.", "She has two children."),
            S("Comment s'appelle ton fils ?", "What's your son's name?", en_alt=["What is your son called?"]),
            S("Nos parents habitent à Marseille.", "Our parents live in Marseille."),
        ],
        "reading": P(
            "Ma famille",
            "Ma famille n'est pas grande. Mon père s'appelle Marc et ma mère s'appelle Sophie. "
            "J'ai une sœur. Elle s'appelle Julie et elle est mariée. Julie a un fils, Léo. Léo a trois ans.",
            "My family is not big. My father is called Marc and my mother is called Sophie. I have a sister. "
            "She is called Julie and she is married. Julie has a son, Léo. Léo is three years old.",
            [Q("What is the mother's name?", ["Sophie", "Julie", "Marc", "Léo"], 0),
             Q("Who is married?", ["Julie", "Léo", "The writer", "Nobody"], 0),
             Q("How old is Léo?", ["Three", "Thirteen", "Two", "Thirty"], 0)],
        ),
        "writing_prompt": "Describe your family in 4 sentences. Use mon / ma / mes.",
        "writing_model": "Ma famille est petite. Ma mère s'appelle Ada. J'ai un frère. Il a vingt ans.",
    },
    # ------------------------------------------------------------------ 6
    {
        "stage": 6,
        "title": "My day",
        "native": "Ma journée",
        "can_do": [
            "Describe your daily routine",
            "Conjugate -er verbs and the irregulars aller and faire",
            "Say what you like doing with aimer + infinitive",
        ],
        "grammar": [
            G("-er verbs: most endings are silent",
              "*je parle, tu parles, il parle, ils parlent* all **sound the same**. Only *nous* and *vous* sound different.",
              [["", "parler"], ["je", "parl**e**"], ["tu", "parl**es**"], ["il / elle", "parl**e**"],
               ["nous", "parl**ons**"], ["vous", "parl**ez**"], ["ils / elles", "parl**ent** (silent!)"]]),
            G("aller & faire: learn them by heart",
              "**aller** (go): vais, vas, va, allons, allez, vont\n**faire** (do/make): fais, fais, fait, faisons, faites, font"),
            G("Word order is calm",
              "Unlike German, French keeps **subject + verb** together, even after a time word: "
              "*Aujourd'hui, **je joue** au foot.*"),
        ],
        "vocab": [
            V("travailler", "to work", ["travaille", "travailles", "travaillons", "travaillez"]),
            V("parler", "to speak", ["parle", "parles", "parlons", "parlez"], en_alt=["to talk"]),
            V("manger", "to eat", ["mange", "manges", "mangeons", "mangez"]),
            V("jouer", "to play", ["joue", "joues", "jouons", "jouez"]),
            V("boire", "to drink", ["bois", "boit", "buvons", "buvez"]),
            V("dormir", "to sleep", ["dors", "dort", "dormons", "dormez"]),
            V("se lever", "to get up", ["lève", "lèves", "levons"]),
            V("aller", "to go", ["vais", "vas", "va", "allons", "allez", "vont"]),
            V("faire", "to do / to make", ["fais", "fait", "faisons", "faites", "font"], en_alt=["to do", "to make"]),
            V("aimer", "to like / to love", ["aime", "aimes", "aimons", "aimez"], en_alt=["to like", "to love"]),
            A("aujourd'hui", "today"),
            A("demain", "tomorrow"),
            A("souvent", "often"),
        ],
        "sentences": [
            S("J'apprends le français.", "I am learning French.", en_alt=["I learn French.", "I'm learning French."]),
            S("Qu'est-ce que tu fais aujourd'hui ?", "What are you doing today?"),
            S("Il travaille à Lyon.", "He works in Lyon."),
            S("Je me lève à sept heures.", "I get up at seven o'clock."),
            S("Aujourd'hui, je joue au foot.", "Today I'm playing football.", alt=["Je joue au foot aujourd'hui."],
              en_alt=["I'm playing football today."]),
            S("Elle aime boire du café.", "She likes to drink coffee.", en_alt=["She likes drinking coffee."]),
            S("Nous mangeons à huit heures.", "We eat at eight o'clock."),
            S("Tu dors bien ?", "Do you sleep well?"),
        ],
        "reading": P(
            "Ma journée",
            "Je me lève à six heures. Je bois un café et je mange du pain. À huit heures, je travaille. "
            "Le soir, j'apprends le français. Ensuite, je dors – bien !",
            "I get up at six o'clock. I drink a coffee and eat some bread. At eight o'clock I work. "
            "In the evening I learn French. Then I sleep – well!",
            [Q("When does the writer get up?", ["At six", "At seven", "At eight", "At nine"], 0),
             Q("What do they do in the evening?", ["Learn French", "Play football", "Work", "Go out"], 0)],
        ),
        "writing_prompt": "Describe your day in 4 sentences. Include one sentence with j'aime + a verb.",
        "writing_model": "Je me lève à sept heures. Je bois un café. Aujourd'hui, je travaille. J'aime jouer au foot.",
    },
    # ------------------------------------------------------------------ 7
    {
        "stage": 7,
        "title": "Food & drink",
        "native": "Manger & boire",
        "can_do": [
            "Order politely with je voudrais",
            "Use du / de la / des for 'some'",
            "Ask for the bill",
        ],
        "grammar": [
            G("'Some' has a gender: du, de la, de l', des",
              "French needs an article for unspecified amounts:\n*Je mange **du** pain* (le pain) · *Je bois **de la** soupe* (la soupe) · "
              "*Je bois **de l'**eau* · *Je mange **des** pommes*.\nAfter a negative they all become **de**: *Je ne mange **pas de** viande.*"),
            G("je voudrais = I would like",
              "The polite way to order (German: *ich möchte*). A second verb stays in the infinitive right after it: "
              "*Je voudrais **boire** un thé.*"),
        ],
        "vocab": [
            N("le pain", "bread", "m"), N("le café", "coffee", "m"), N("le thé", "tea", "m"),
            N("l'eau", "water", "f"), N("le lait", "milk", "m"), N("le fromage", "cheese", "m"),
            N("l'œuf", "egg", "m", "les œufs"), N("la soupe", "soup", "f"), N("la bière", "beer", "f"),
            N("le gâteau", "cake", "m", "les gâteaux"), N("la viande", "meat", "f"),
            N("l'addition", "bill", "f", en_alt=["check"]),
            V("vouloir", "to want", ["veux", "veut", "voulez", "voudrais"]),
            V("prendre", "to take / to have (food)", ["prends", "prend", "prenez"], en_alt=["to take"]),
            A("délicieux", "delicious", en_alt=["tasty"]),
        ],
        "sentences": [
            S("Je voudrais un café, s'il vous plaît.", "I would like a coffee, please.", en_alt=["I'd like a coffee, please."]),
            S("Je prends la soupe.", "I'll have the soup.", en_alt=["I'll take the soup."]),
            S("Qu'est-ce que tu veux boire ?", "What do you want to drink?", en_alt=["What would you like to drink?"]),
            S("Je ne mange pas de viande.", "I don't eat meat."),
            S("L'addition, s'il vous plaît !", "The bill, please!", en_alt=["The check, please!"]),
            S("Le gâteau est délicieux.", "The cake is delicious.", en_alt=["The cake is tasty."]),
            S("Vous avez de l'eau ?", "Do you have water?", en_alt=["Have you got water?"]),
            S("Je mange du pain.", "I eat bread.", en_alt=["I'm eating bread.", "I eat some bread."]),
        ],
        "reading": P(
            "Au café",
            "Serveur : Bonjour ! Vous désirez ?\nCliente : Je voudrais un thé et un gâteau, s'il vous plaît.\n"
            "Serveur : Avec du lait ?\nCliente : Non, merci. Sans lait.\nServeur : Très bien. Et avec ça ?\n"
            "Cliente : C'est tout. L'addition, s'il vous plaît !",
            "Waiter: Hello! What would you like? / Customer: I'd like a tea and a cake, please. / Waiter: With milk? / "
            "Customer: No, thank you. Without milk. / Waiter: Very good. Anything else? / Customer: That's all. The bill, please!",
            [Q("What does the customer order?", ["Tea and cake", "Coffee and cake", "Tea with milk", "Soup"], 0),
             Q("Does she want milk?", ["No", "Yes", "A little", "She doesn't say"], 0)],
        ),
        "writing_prompt": "You're in a French café. Write 3–4 lines: order a drink and food, say what you don't eat, ask for the bill.",
        "writing_model": "Bonjour ! Je voudrais un café et du pain, s'il vous plaît. Je ne mange pas de viande. L'addition, s'il vous plaît !",
    },
    # ------------------------------------------------------------------ 8
    {
        "stage": 8,
        "title": "Time & days",
        "native": "L'heure & les jours",
        "can_do": [
            "Tell the time",
            "Name the days and make plans",
            "Say what you do regularly with le + day",
        ],
        "grammar": [
            G("Telling time is friendly",
              "*Il est deux heures **et demie*** = 2:30 (literally *two hours and a half*).\n"
              "⚠ German says *halb drei* for the same time. French counts **up** from the hour, German counts **towards** the next.\n"
              "*et quart* = quarter past · *moins le quart* = quarter to"),
            G("Days: lowercase, masculine, and 'le' means 'every'",
              "*lundi* = (this) Monday · ***le** lundi* = **on Mondays** (every Monday).\nDays and months are **not** capitalised in French."),
        ],
        "vocab": [
            N("lundi", "Monday", "m"), N("mardi", "Tuesday", "m"), N("mercredi", "Wednesday", "m"),
            N("jeudi", "Thursday", "m"), N("vendredi", "Friday", "m"), N("samedi", "Saturday", "m"),
            N("dimanche", "Sunday", "m"),
            N("l'heure", "hour / time (o'clock)", "f", "les heures", en_alt=["hour", "o'clock"]),
            N("la semaine", "week", "f", "les semaines"),
            N("le week-end", "weekend", "m", "les week-ends"),
            N("le matin", "morning", "m"),
            A("tard", "late"),
            A("tôt", "early"),
            V("commencer", "to begin / to start", ["commence", "commences", "commençons"], en_alt=["to start", "to begin"]),
        ],
        "sentences": [
            S("Quelle heure est-il ?", "What time is it?"),
            S("Il est deux heures et demie.", "It's half past two.", en_alt=["It is two thirty."]),
            S("Le lundi, je travaille.", "On Mondays I work.", alt=["Je travaille le lundi."], en_alt=["I work on Mondays."]),
            S("Le cours commence à neuf heures.", "The class starts at nine o'clock.", en_alt=["The course begins at nine."]),
            S("Le week-end, j'ai du temps.", "At the weekend I have time.", en_alt=["On the weekend I have time."]),
            S("Tu es libre vendredi ?", "Are you free on Friday?"),
            S("À demain !", "See you tomorrow!"),
        ],
        "reading": P(
            "Ma semaine",
            "Le lundi et le mardi, je travaille jusqu'à cinq heures. Le mercredi, j'apprends le français : "
            "le cours commence à six heures et demie. Le vendredi, je joue au foot. Le week-end, je dors tard !",
            "On Mondays and Tuesdays I work until five o'clock. On Wednesdays I learn French: the class starts at "
            "half past six. On Fridays I play football. At the weekend I sleep late!",
            [Q("When does the French class start?", ["6:30", "5:30", "5:00", "7:30"], 0),
             Q("What happens on Fridays?", ["Football", "French class", "Work until five", "Sleeping late"], 0)],
        ),
        "writing_prompt": "Write your plan for next week: 4 sentences with days and times (à … heures).",
        "writing_model": "Lundi, je travaille. Mardi, j'apprends le français à sept heures. Vendredi, je suis libre. Dimanche, je dors tard.",
    },
]
