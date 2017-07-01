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
====
* Lägg bara in de konton som behövs i SI-filen. Då kan man även fråga om något
  saknas.
* Hitta om det saknas ett fält i tabellerna. Det kan tex. bli svårt att hitta
  felet om Acct_Kto saknar V_Kto men har KONTO osv. Kanske kan CSVDict utelämna
  fält om det är tomt i filen. Så ser man om det saknas när man försöker komma
  åt.
* Spara CSV-filer sorterade på nyckel
* Hitta namn på konto/projekt/cc i SIE-filen när man ska mata in
* Spara/hålla koll på senaste verifikation för varje serie
* Undersöka konstiga tecken. (mappen teckenfel)
* x Se till så att nödvändig information matas in om det saknas i tabellerna.
* x Lägga till i tabeller direkt i gränssnittet
* x Ändra Windows-genväg till att starta i programmappen
