from app.evaluate import check_speech, check_text


def cat(user, expected, lang):
    r = check_text(user, [expected], lang)
    return r.grade, r.categories


def test_exact_and_capitalisation():
    assert cat("Ich habe einen Hund.", "Ich habe einen Hund.", "de") == ("correct", [])
    assert cat("ich habe einen hund", "Ich habe einen Hund.", "de") == ("almost", ["capitalization"])


def test_gender_case_and_articles():
    assert cat("Die Tisch ist groß", "Der Tisch ist groß.", "de") == ("wrong", ["gender"])
    assert cat("Ich habe ein Hund", "Ich habe einen Hund.", "de") == ("wrong", ["case"])
    assert cat("Tisch", "der Tisch", "de") == ("wrong", ["gender"])
    assert cat("le maison est grande", "La maison est grande.", "fr") == ("wrong", ["gender"])
    assert cat("le ecole", "l'école", "fr")[1] == ["gender"]


def test_word_order():
    assert cat("Heute ich spiele Fußball", "Heute spiele ich Fußball.", "de") == ("wrong", ["word_order"])


def test_conjugation_endings_spelling():
    assert cat("Er wohnen in Berlin", "Er wohnt in Berlin.", "de")[1] == ["conjugation"]
    assert cat("Il travailles à Lyon", "Il travaille à Lyon.", "fr")[1] == ["conjugation"]
    assert cat("La maison est grand", "La maison est grande.", "fr")[1] == ["endings"]
    assert cat("Ich habe einen Hunt", "Ich habe einen Hund.", "de") == ("almost", ["spelling"])


def test_accents_and_umlaut_fallbacks():
    assert cat("je suis etudiant", "Je suis étudiant.", "fr") == ("almost", ["accents"])
    assert cat("das Maedchen", "das Mädchen", "de") == ("almost", ["accents"])


def test_missing_word():
    assert cat("je mange pas de viande", "Je ne mange pas de viande.", "fr")[1] == ["missing_word"]


def test_alternatives_accepted():
    r = check_text("In Berlin wohne ich", ["Ich wohne in Berlin.", "In Berlin wohne ich."], "de")
    assert r.grade == "correct"


def test_speech_scoring_with_digits():
    assert check_speech(["ich stehe um 7 Uhr auf"], "Ich stehe um sieben Uhr auf.", "de").grade == "correct"
    r = check_speech(["ich habe einen"], "Ich habe einen Hund.", "de")
    assert r.grade == "almost" and r.detail["missed"] == ["Hund"]
    assert check_speech([""], "Bonjour !", "fr").grade == "wrong"
