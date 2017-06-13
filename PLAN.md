Petra -> Visma
==============
Kan läsa från databas direkt ur Petra, får då med batchnummer. Detta är
unikt och ökande, alla finns med. Kan producera tabell med alla batchnummer
över ett visst värde.

Uppdelat i Batch, Journal, Transaction

Frågor
------
* Hur registreras en kontantgåva i annan valuta i Petra? (Finns motsvarighet
  till Vismas kvantitet?)


Visma -> Petra
==============

Korrekthet
----------
Vissa transaktioner kommer först till Petra, andra först till Visma. Bara de
som inte finns sedan tidigare ska föras över till det andra systemet. Skulle
kunna märka dem på något sätt i namnet så att tex. verifikationer från Petra
som finns med i en .si-fil ignoreras ifall de har Petraexport in namnet. När
man skapar .si-filer för import till Visma kan man på liknande sätt ignorera
verifikationer som har Vismaexport i namnet.

TODO
----
* Hitta namn på konto/projekt/cc i SIE-filen när man ska mata in
* Undersöka konstiga tecken. (mappen teckenfel)
* Spara/hålla koll på senaste verifikation för varje serie
* x Lägga till i tabeller direkt i gränssnittet
* x Ändra Windows-genväg till att starta i programmappen
