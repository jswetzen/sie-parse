Petra -> Visma
==============
Kan läsa från databas direkt ur Petra, får då med batchnummer. Detta är
unikt och ökande, alla finns med. Kan producera tabell med alla batchnummer
över ett visst värde.

Uppdelat i Batch, Journal, Transaction


Visma -> Petra
==============

Korrekthet
==========
Vissa transaktioner kommer först till Petra, andra först till Visma. Bara de
som inte finns sedan tidigare ska föras över till det andra systemet. Skulle
kunna märka dem på något sätt i namnet så att tex. verifikationer från Petra
som finns med i en .si-fil ignoreras ifall de har Petraexport in namnet. När
man skapar .si-filer för import till Visma kan man på liknande sätt ignorera
verifikationer som har Vismaexport i namnet.
