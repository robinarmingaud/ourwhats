# OurWhats

Une ébauche d'application de messagerie instantanée s'inspirant de Messenger et WhatsApp


## Authors

- [@robinarmingaud](https://github.com/robinarmingaud)
- [@maxime-cool](https://github.com/maxime-cool)


## Installation 

Cloner le repository

```bash
  git clone https://github.com/robinarmingaud/ourwhats
```
## Structure
Projet séparé en 3 parties :
- La base de donnée constituée des classes Group, User, Message, Upload (pour les pièces jointes), ProfileP et une table de participation participation_table
- Le dossier static regroupant les feuilles de style, le javascript et les dossiers uploads et profile_pics regroupant respectivement les pièces jointes envoyées dans les messages et les photos de profil des utilisateurs
- Le dossier templates qui comprend le code HTML, principalement main_view.jinja2.hmtl qui comprend le HTML du tableau de bord principal avec la vue et la gestion de nos messages
- Les dossiers old et debug comprennent des pages HTML utilisées pour des tests ou plus du tout utilisées
## Fonctionnalités et utilisation
- OurWhats permet en accédant à son localhost d'arriver sur une page de connexion avec la liste des utilisateurs possédant un compte. Si vous n'avez pas de compte vous pouvez en créer un en suivant le lien "s'inscrire". Nous ne nous sommes pas concentrés sur la gestion de l'authentification ni sur le style des pages de connexion et d'inscription. Le nouvel utilisateur aura alors une photo de profil de base "default.png" stockée dans le dossier static/profile_pics et une conversation démarrage avec l'utilisateur par défaut OurWhats est créée.
- Une fois le numéro correspondant à un utilisateur existant entré dans le champ, vous arrivez sur une page de messagerie classique s'inspirant de Messenger
- Il est possible de créer une conversation en cliquant sur le bouton + en haut à gauche, le champ doit être forcément rempli
- Il est possible de voir une autre conversation simplement en cliquant sur celle-ci à gauche. La conversation active est plus foncée.
- L'ordre des conversations est déterminé par l'heure et la date du dernier message envoyé
- De base, une conversation nouvellement créée ne comptient que le compte par défaut "OurWhats" et l'utilisateur créateur, pour ajouter des personnes il faut cliquer sur le bouton + en haut à côté du nom de la conversation. Une fenêtre avec tous les utilisateurs enregistrés s'ouvre avec un champ de recherche.
- Il est possible d'également chercher une conversation par son nom en utilisant le champ de recherche de la gauche ou rechercher un message dans la conversation active dans le champ de recherche de droite
- Le bouton Quitter permet de quitter la conversation active. Attention, si l'utilisateur ne fait partie que d'une seule conversation il ne pourra pas la quitter.
- Enfin le bouton avec les personnes sur l'extrême droite permet de voir les membres de la conversation.
- Pour envoyer un message dans la conversation active, un formulaire est disponible en bas de la page. Pour pouvoir envoyer le message, il est obligatoire que le champ texte doit rempli même si on souhaite envoyer une pièce jointe seule (ce qui est impossible du coup)
- Les messages peuvent être survolés pour afficher l'heure et la date d'envoi
- Les extensions supportées pour les pièces jointes sont 'jpg', 'jpeg', 'png', 'gif', 'pdf', 'zip', 'mp4'. Les images et les gifs s'affichent directement dans la conversation et il est possible de les voir en taille original en cliquant dessus.
- Les conversations sur la gauche indiquent le nombre de messages non lus au dessus de leur nom
- Finalement le bouton en haut à gauche permet de consulter son profil. Il est possible de changer son nom d'utilisateur et sa photo de profil. Les formats supportés sont 'jpg', 'jpeg', 'png', 'gif'. Il n'est pas possible de rentrer un nom d'utilisateur vide.
- Une estimation de la consommation de données est donnée sur cette page. Elle indique le nombre de messages envoyés, le volume de pièces jointes envoyées et leur impact en terme d'emissions de carbone en se basant sur les chiffre de l'ADEME pour l'envoi de mails et l'équivalent en distance parcourue par un véhicule moderne. Sont également affichés : le volume total de pièces jointes envoyées et reçues et enfin le volume total stocké sur le serveur tout utilisateur confondu. Le poids des photos de profil n'est pas pris en compte.
- Il manquerait une meilleure implémentation de l'aspect temps réel puisqu'il est nécessaire d'effectuer une action ou rafraichir la page pour voir l'actualisation de nos messages.
- Des alertes et des retours d'erreurs pourraient aussi être intéressants à ajouter.

