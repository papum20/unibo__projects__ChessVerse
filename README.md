# ChessVerse

University project for software engineering 2023-2024, at University of Bologna. An online ReallyBadChess game.  
The project's purpose was to create something apparently working; the code, structure and everything here is very ugly.  

## Install

Clone this repo and launch the provided `docker-compose.yml`.  
You first need to setup environment variables: `server-nginx/chessverse.env`, `env/credentials.env` (there's a script for generating random ones), `.env`.  
We also provide a `chessverse.conf.template` file for a nginx server; note that it contaians some variables: our approach is to use `envsubst` and the env file `chessverse.env`.  
This setup doesn't expose any port, but assumes the use of a proxy server (e.g. nginx), which would communicate with the chessverse containers on the `default` network; change it if you use another network.  

## Doc

We endeavour to keep the documentation clear, consistent and updated at all time, so both our team and whoever wants to look at out project can understand it, or at least its structure, despite the large amount of files, services etc.  
All documentation shall be put in the `doc/` folder.  

Here are the main points ant paths about it:
*	schemas:
	-	`infrastructure.drawio`
	-	`mockup*.jpg`
	-	`repository-structure.md`
	-	`schema*.jpg`
*	agile definitions:
	-	`definitions.md`
*	folders containing sprints information:
	-	`backlogs`
	-	`goals`
	-	`retrospective`
	-	`review`
	-	`slides`
*	project and development:
	-	`code`: actual documentation for the code
	-	`workflow`: conventions about our development process

## Project development methods

**Membri del Team:**
- Giuseppe Spathis (PO) - 0001043077
- Luca Gabellini (SM) - 001020370
- Nico Wu (Dev) - 0001028979
- Francesco Licchelli (Dev) - 0001041426
- Daniele D'Ugo (Dev) - 0001027741
- Cono Cirone (Dev) - 0001029785

---

**Descrizione del Progetto:**

Il sito web proposto è un ambiente di gioco online che offre l'opportunità di giocare a una o più varianti degli scacchi. Gli utenti hanno la possibilità di sfidarsi in partite, sia contro l'intelligenza artificiale del computer che contro altri giocatori umani. La piattaforma consente agli utenti di cercarsi reciprocamente, concordare le modvalità e i tempi di gioco, nonché salvare e visualizzare i risultati delle partite.

Inoltre, l'app fornirà una classifica generale (leaderboard) per tenere traccia delle prestazioni dei giocatori nel tempo. Sarà possibile collegarsi a social network per commentare le partite, cercare partner e, se desiderato, giocare in modalità "mob". Per quanto riguarda l'accesso ai servizi offerti, la maggior parte sarà riservata ai membri iscritti. Tuttavia, alcuni servizi saranno accessibili anche a non soci.

---

**Sviluppo:**
- Modalità di comunicazione intergruppo: Telegram e Mattermost
- Riunioni Scrum: 3 volte alla settimana
- Linguaggio di Programmazione: Python, javascript
- Database: MySQL
