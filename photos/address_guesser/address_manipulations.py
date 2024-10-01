import re

class AddressManipulations:
    # List of replacements and varients
    REPLACEMENTS = {
        "fasor": ["fasoron", "fasorra", "fasorról", "fasorban", "fasorba", "fasorból", "fasornál", "fasorhoz", "fasortól", "fasori"],
        "körút" : ["körúton" , "körútra", "körútról", "körútból", "körútnál", "körúthoz", "körúttól", "körúti" ],
        "park": ["parkon", "parkra", "parkról", "parkban", "parkba", "parkból", "parknál", "parkhoz", "parktól"],
        "sétány": ["sétányon", "sétányra", "sétányról", "sétányba", "sétányból", "sétánynál", "sétányhoz", "sétánytól"],
        "tere": ["terén", "terére", "teréről", "terébe", "teréből", "terénél", "teréhez", "terétől", "terei"],
        "tér": ["téren", "térre", "térről", "térbe", "térből", "térnél", "térhez", "tértől", "téri"],
        "utca": ["utcán", "utcára", "utcáról", "utcában", "utcába", "utcából", "utcánál", "utcához", "utcától", "utcai"],
        "út": ["úton", "útra", "útról", "útban", "útba", "útból", "útnál", "úthoz", "úttól", "úti"],
        "útja": ["útján", "útjára", "útjáról", "útjában", "útjába", "útjából", "útjánál", "útjához", "útjától", "útjai"],
    }

    NER_FIXES_REPLACEMENT = {
        "[LOC-B]pesti alsó rakpart[LOC-E]": ["pesti alsó \[LOC-B\]rak\[LOC-E\]part"],
        "[LOC-B]budai Vár[LOC-E]": ["budai \[LOC-B\]Vár\[LOC-E\]"],
        "[LOC-B]Szent István-bazilika[LOC-E]": ["\[LOC-B\]Szent István-bazili\[LOC-E\]ka"],
        "székház[LOC-E]": ["szék\[LOC-E\]ház"],
        "rakpart[LOC-E]": ["rak\[LOC-E\]part"],
        "[LOC-B]Főposta[LOC-E]": ["\[LOC-B\]Főpost\[LOC-E\]a"],
        "[LOC-B]Párizsi udvar[LOC-E]": ["\[LOC-B\]Párizs\[LOC-E\]i \[LOC-B\]udvar\[LOC-E\]"],
        "[LOC-B]Vigadó[LOC-E]": ["\[LOC-B\]Vig\[LOC-E\]adó"],
        "[LOC-B]Ferenciek tere[LOC-E]": ["\[LOC-B\]Ferenc\[LOC-E\]iek \[LOC-B\]tere\[LOC-E\]"],
        "[LOC-B]Dunakorzó[LOC-E]": ["\[LOC-B\]Dunak\[LOC-E\]orzó"],
        "Palota[LOC-E]": ["Palot\[LOC-E\]a"],
        "[LOC-B]József nádor tér[LOC-E]": ["\[LOC-B\]József nád\[LOC-E\]or \[LOC-B\]tér\[LOC-E\]"],
        " köz[LOC-E]": ["\[LOC-E\] \[LOC-B\]köz\[LOC-E\]"],
        "[LOC-B]Káptalandomb[LOC-E]": ["\[LOC-B\]K\[LOC-E\]áptalan\[LOC-B\]##domb\[LOC-E\]"],

    }

    def __init__(self):
        pass

    def replace_public_places_variants(self, text):
        for replacement, variants in self.REPLACEMENTS.items():
            for variant in variants:
                text = re.sub(rf'\b{variant}\b', replacement, text)
        return text

    def fix_NER_errors(self, text):
        for replacement, variants in self.NER_FIXES_REPLACEMENT.items():
            for variant in variants:
                text = re.sub(rf'{variant}', replacement, text)
        return text

    def remove_fortepan_attribution_text(self, text):
        text = re.sub(rf'A kép forrását kérjük így adja meg:.*', '', text)
        text = re.sub(rf'Forrás/source:.*', '', text)
        text = re.sub(rf'Forrás:.*', '', text)
        
        return text