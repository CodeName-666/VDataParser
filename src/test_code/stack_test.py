import inspect


stack_info = None

def get_stack_info():
    global stack_info
    if stack_info is None:
        stack_info = inspect.stack()
    return stack_info


class MeineKlasse:
    def meine_methode(self):
        # Hier rufe ich die Funktion auf, um den Aufrufort und die Verschachtelungstiefe zu ermitteln
        get_stack_info()
        aufrufender_ort, tiefe = ermittle_aufrufenden_ort()

        print(f'Die Methode wurde aufgerufen von: {aufrufender_ort}')
        print(f'Verschachtelungstiefe: {tiefe}')

    def mmeine_2te_methode(self):
        self.meine_methode()


def ermittle_aufrufenden_ort():
    # Verwende inspect.stack(), um den Aufrufstapel zu erhalten
    aufrufstapel = inspect.stack()

    # Der aufrufende Ort ist im Index 1 des Aufrufstapels
    aufrufender_ort = aufrufstapel[1]

    # Extrahiere Informationen aus dem Rahmenobjekt
    datei_name = aufrufender_ort.filename
    zeilennummer = aufrufender_ort.lineno
    funktion_name = aufrufender_ort.function

    # Extrahiere den Klassenkontext aus dem aufrufenden Rahmen
    klassenkontext = aufrufender_ort[0].f_locals.get('self', None)
    klassenname = klassenkontext.__class__.__name__ if klassenkontext else None
    get_stack_info
    # Bestimme die Verschachtelungstiefe
    tiefe = len(inspect.stack()) - 2

    return (f'Klasse {klassenname}, Datei {datei_name}, Zeile {zeilennummer}, Funktion {funktion_name}', tiefe)

# Beispielaufruf
objekt = MeineKlasse()
objekt.mmeine_2te_methode()
