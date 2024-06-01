
# Bienvenue sur le Calculateur de Classement ELO FFAM
Ce projet propose un outil de classement basé sur un classement Elo applicable aux pilotes de course de drone français participant à la coupe de France de Drone Racing.

# Classement en cours
Mis a jour le 01 Juin 2024

|#|ELO|LICENCE|PSEUDO|PRENOM|NOM DE FAMILLE|
|:-|:-|:-:|:-:|:-:|:-:|
|01|1882|2102235|AVALT|Arthur|VALTIER|
|02|1869|1701954|FENOMAN|Bailleau|GUILLAUME|
|03|1845|1303854|PASTIS|Dorian|COUAILLES|
|04|1838|1401260|KILLIAN|Killian|ROUSSEAU|
|05|1792|2000421|AVASSIN|Lucas|BEAUDOUIN|
|06|1789|1702320|YAYOU|Swan|VERSMISSEN|
|07|1750|1900076|BEAR RACER|Arthur|POLI|
|08|1723|1700078|SUPER EWEN|Ewen|GOIN|
|09|1685|1803004|VIOFLY|Thibault|BILLARD|
|10|1684|2301745|MATHOU|Mathias|ALBORGHETTI|
|11|1676|2302066|LEVIO|Thimote|LEVIONAIS|
|12|1622|1604142|GPW|Jerome|ULRICH|
|13|1610|1802658|SARPOON|Aurelien|DUVAL|
|14|1595|1227815|FRALOU|Franck|ALBORGHETTI|
|15|1546|2300281|YAKUZA_FPV|Thibaut|GIETHLEN|
|16|1542|2301855|MATTOON|Matti|ROCHE|
|17|1467|1802994|FRACTALFPV|Aurelien|CAMPS|
|18|1450|2200679||Christophe|ANTOINE|
|19|1405|2101626|DEBAZ|Maxime|CAVICCHI|
|20|1387|2302122||Steven|COLLONGUES|
|21|1366|1802030|20SY|Sylvain|MOGENY|
|22|1345|2100246|RASTAPOPOULOS94|Marc|ONZON|
|23|1288|2401714||Emilie|RISCHARD|
|24|1276|1504811|BABA FPV|Bastien|LEDUC||

# Comment ça marche
Le système de classement Elo est une méthode qui estime la force relative d'un pilote. Dans ce système, battre un adversaire mieux classé vous donne plus de points que de battre un adversaire moins bien classé. En même temps, votre adversaire perd autant de points que vous en gagnez.
Le système de classement Elo, nommé d'après Arpad Elo, joueur d'échecs qui l'a inventé, est un système largement utilisé non seulement dans les Échecs, mais également dans de nombreux autres jeux et sports, y compris le Go, le Scrabble, le football et le tennis, ainsi que dans certains jeux vidéo en ligne, démontrant ainsi sa popularité et sa polyvalence.

## Comment est calculé le classement Elo
Le système de classement ELO repose sur le principe suivant : chaque pilote démarre avec un certain nombre de points ELO, et à chaque course, des points sont échangés entre les joueurs en fonction du résultat attendu et du résultat réel. Plus un pilote bat un adversaire fort, plus il gagne de points, et vice versa.
Dans ce projet, nous avons adapté l'algorithme ELO pour l'utilisation en Drone Racing. Les pilotes sont classés en fonction de leurs performances dans les courses, avec des ajustements en fonction des résultats attendus.

### Le classement Elo est actualisé en suivant ces étapes :

1. **Initialisation des scores :** Chaque pilote démarre la saison avec un score Elo initial de **1500 points**
2. **Recalcul du classement après chaque course** Après la conclusion de chaque course, le classement issu de cette dernière sera utilisé comme référence pour la mise à jour du classement Elo. Dans une course impliquant ***n*** pilotes, le classement de chaque pilote sera ajusté en tenant compte des ***n-1*** duels. Nous supposerons que chaque pilote bat les pilotes classés derrière lui et perd contre ceux ayant terminé la course devant lui.
3. **Etablissement du nouveau classement** Une fois tous les duels calculés, le classement ELO est donc mis a jour et est publié en attendant la prochaine course..

### Méthode de calcul de chaque duel
Chaque duel est calculé de manière indépendante en prennant en compte le classement ELO des deux pilotes ***avant la course***
**Pour trouver le changement de classement Elo entre deux pilotes, A et B :**
1. Prenez la différence de classements : `(B - A)`
2. Divisez la différence de classements par 400 : `(B - A) / 400`
3. Trouvez la valeur de dix à la puissance de cette fraction et ajoutez 1 : `10^[(B - A) / 400] + 1`
4. Le score attendu est l'inverse multiplicatif de ce dernier : `attendu = 1 / (10^[(B - A) / 400] + 1)`
5. Enfin, le facteur K *(20 dans notre cas)* influence le changement du Elo  *(victoire = 1, match nul = 0,5, défaite = 0)* pour obtenir le changement de Classement Elo : `Changement = K × (score - attendu)`
6. Le *Changement* est ajouté au classement précédent pour obtenir le nouveau classement !

Le facteur K a été arbitrairement choisi a 20. Il prend généralement des valeurs entre 10 et 40, en fonction de l'utilisation du classement Elo. 

***Cas particulier :*** Dans le cadre de la mise en place de ce classement pour le Drone Racing different options sont ajoutées au calculateur de classement Elo

 - Un autre multiplicateur pourra être appliqué afin de donner plus de poids à certaines courses importantes. Ainsi l'ensemble des duels d'une même course avec un coefficient 2 recevront un facteur `K = 2x20 = 40` *Cette option n'est pas implémentée actuellement*
 - Un limitateur de perte est mis en place. Ce dernier divise la valeur du *Changement* par un facteur donné en cas de perte. Ceci permet d'éviter aux pilotes de bas de classement de descendre trop bas tout en conservant le haut du classement. *Cette option n'est pas implémentée actuellement*

# Où trouver le classement actuel ? 
Le classement est disponible sur ce repo github, à cette adresse : *TODO: add email*
Le classement est également mis à jour sur le site du groupe de travail drone sport à cette adresse : [drone-sport-france](https://sites.google.com/view/drone-sport-france/accueil)

# Comment soumettre les résultats d'une course
Une fois votre course terminée, veuillez suivre les étapes suivantes pour soumettre les résultats :

1. Remplissez le [template CSV](https://github.com/elodroneracingfr/Elo-Calculator/blob/main/ASSETS/TEMPLATE/YEAR-MONTH-DAY-RACE_NAME.csv) avec l'ensemble des détails de la course et de chaque pilote. 
2. Soumettez le fichier CSV rempli à l'adresse suivante : *TODO: add email*

# Où télécharger le fichier csv vide pour soumettre les résultats
Le template est disponible dans [ASSETS/TEMPLATEYEAR-MONTH-DAY-RACE_NAME.csv](https://github.com/elodroneracingfr/Elo-Calculator/blob/main/ASSETS/TEMPLATE/YEAR-MONTH-DAY-RACE_NAME.csv)

# Comment utiliser l'outil

# Archives
<details>
<summary>2022-2023</summary>
<br>
Ranking with 3 races min, K_FACTOR = 20 | USE_RACE_WEIGHT = False | USE_LOSS_LIMITER = False

CURRENT RANKING with 3 race(s):

|#|ELO|LICENCE|PSEUDO|PRENOM|NOM DE FAMILLE|
|:-|:-|:-:|:-:|:-:|:-:|
|01|1972|1401260|Darkex|Killian|ROUSSEAU|
|02|1868|1700078|SUPER Ewen|Ewen|Goin|
|03|1851|1603508|TRINX|Tristan|Goin|
|04|1837|2102235|Avalt|Arthur|VALTIER|
|05|1822|1303854|DRN FPV|Dorian|COUAILLES |
|06|1786|1702320|Yayou|Swan|VERSMISSEN|
|07|1775|2202387|Ed Fpv|Edwin|HO A CHUCK|
|08|1765|1803004|VioFly|Thibault|Billard|
|09|1750|1900076|Bear Racer|Arthur|POLI|
|10|1723|2000421|Avassin|Lucas|BEAUDOUIN|
|11|1671|1701954|FENOMAN|Bailleau|Guillaume|
|12|1663|1802994|FractalFPV|Aurelien|Camps|
|13|1656|2202173|Oliv|Olivier|MYLLE|
|14|1521|1604142|GPW|Jerome|Ulrich|
|15|1513|2301745|Mathou|Mathias|Alborghetti|
|16|1495|1227815|Fralou|Franck|Alborghetti|
|17|1444|2301934|DRK|goin|stephane|
|18|1407|2100578|U FPV|Pichon|Jules|
|19|1391|1802030|20SY|Sylvain|Mogeny|
|20|1374|2302181|daniel's jack|Daniel|Esteves|
|21|1348|2301855|Mattoon|Matti|Roche|
|22|1348|2201699|Chris FPV|Christophe|Juanole|
|23|1327|2101626|Debaz|Maxime |CAVICCHI|
|24|1323|2100246|Rastapopoulos94 |Marc|ONZON|
|25|1323|1603392|STARZ91|Boisselier|Vincent|
|26|1319|2300281|Yakuza_FPV|Thibaut|Giethlen|
|27|1251|1504811|Baba fpv|Bastien|Leduc|
|28|1226|2201470|Ustrici|Romain|VALTIER|
</details>









