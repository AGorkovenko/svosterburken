/* Trainingszeiten des SV 1919 Osterburken e.V.
   Einzige Datenquelle für "Heute beim SVO", Wochenpläne, Team- und Gruppenkarten.
   slots: [Wochentag (0 = Montag … 6 = Sonntag), Beginn, Ende]
   months: aktive Monate (1–12), fehlt = ganzjährig
   age: 'kids' | 'adults' (für die Turnen-Unterseiten) */

const PLACES = {
  sportplatz: { name: 'Sportplatz Osterburken', q: 'Sportplatzweg 1, 74706 Osterburken' },
  sportheim:  { name: 'Start am Sportheim',     q: 'Sportplatzweg 1, 74706 Osterburken' },
  limes:      { name: 'Halle Schule am Limes',  q: 'Schule am Limes Osterburken' },
  aula:       { name: 'Aula Grundschule am Limes', q: 'Grundschule am Limes Osterburken' },
  rso:        { name: 'Sporthalle Realschule',  q: 'Realschule Osterburken' },
  gto:        { name: 'Sportplatz GTO',         q: 'Ganztagsgymnasium Osterburken' },
  sg:         { name: 'Osterburken, Adelsheim, Sennfeld oder Roigheim', q: 'Osterburken' },
};

const DEPTS = {
  fussball: { name: 'Fußball', mail: 'fussball@svosterburken.de', url: 'fussball.html' },
  turnen:   { name: 'Turnen',  mail: 'turnen@svosterburken.de',   url: 'turnen.html' },
  fitness:  { name: 'Fitness', mail: 'fitnesskurse@svosterburken.de', url: 'fitness.html' },
};

const GROUPS = [
  // Fußball – code = Aufdruck auf dem Trikot-Icon
  { dept: 'fussball', code: 'G', title: 'Bambini', who: 'bis 6 Jahre', place: 'sportplatz',
    slots: [[4, '16:30', '17:30']], coaches: 'Janina Gedik, Mathias Gruhl, Sven Merz, Marco Frodl' },
  { dept: 'fussball', code: 'F', title: 'F-Jugend', who: '7–8 Jahre', place: 'sportplatz',
    slots: [[4, '16:30', '18:00']], coaches: 'Thorsten Klein, Ricardo Lamas, Heiko Gakstatter, Erik Flaum' },
  { dept: 'fussball', code: 'E', title: 'E-Jugend', who: '9–10 Jahre', place: 'sportplatz',
    slots: [[2, '17:30', '19:00'], [4, '16:30', '18:00']], coaches: 'Patrick Oldenburg, Markus Gakstatter, Holger Karle' },
  { dept: 'fussball', code: 'D', title: 'D-Jugend', who: '11–12 Jahre', place: 'sportplatz',
    slots: [[1, '18:00', '19:30'], [3, '18:00', '19:30']], coaches: 'Patrick Mackert, Rolf Hofmann, Eugen Fot, Alex Sager, Adrian Laska' },
  { dept: 'fussball', code: 'C', title: 'C-Jugend', who: '13–14 Jahre', place: 'sg', note: 'Ort nach Absprache',
    slots: [[1, '18:00', '20:00'], [3, '18:00', '20:00']], coaches: 'Wladi Bichler, Alex Dück, Joao Dias, Robert Makowski' },
  { dept: 'fussball', code: 'B', title: 'B-Jugend', who: '15–16 Jahre', place: 'sg', note: 'Ort nach Absprache',
    slots: [[0, '18:30', '20:00'], [3, '18:30', '20:00']], coaches: 'Robby Kiss, Gregor Englert' },
  { dept: 'fussball', code: '2', title: 'Zweite Mannschaft', who: 'Aktive', place: 'sportplatz',
    slots: [[1, '18:00', '21:00'], [4, '18:00', '21:00']], coaches: 'Michael Gutenberg' },
  { dept: 'fussball', code: '1', title: 'Erste Mannschaft', who: 'Aktive', place: 'sportplatz',
    slots: [[1, '18:00', '21:00'], [4, '18:00', '21:00']], coaches: 'Dominik Reichert' },

  // Turnen · Kinder
  { dept: 'turnen', age: 'kids', icon: 'family', title: 'Eltern-Kind-Turnen', who: '2 Jahre bis Einschulung', place: 'limes',
    slots: [[3, '17:00', '18:30']],
    desc: 'Kinder entdecken zusammen mit Mama oder Papa Bewegung, Koordination und Gemeinschaft.' },
  { dept: 'turnen', age: 'kids', icon: 'family', title: 'Eltern-Kind-Turnen', who: '2 Jahre bis Einschulung', place: 'rso',
    slots: [[2, '16:00', '17:15'], [2, '17:15', '18:30']], note: 'Zwei Gruppen nacheinander',
    desc: 'Wie am Donnerstag – in zwei kleineren Gruppen in der Realschul-Halle.' },
  { dept: 'turnen', age: 'kids', icon: 'child', title: 'Sport, Spiel und Spaß', who: 'Vorschule bis 2. Klasse', place: 'limes',
    slots: [[1, '17:30', '19:00']],
    desc: 'Jungen und Mädchen sammeln erste sportliche Erfahrungen – mit Spielen, Parcours und viel Bewegung.' },
  { dept: 'turnen', age: 'kids', icon: 'dance', title: 'Mädchenturnen & Tanz', who: '1. bis 3. Klasse', place: 'limes',
    slots: [[0, '17:00', '18:30']],
    desc: 'Turnerische Grundlagen und kreative Tanzelemente.' },
  { dept: 'turnen', age: 'kids', icon: 'volleyball', title: 'Mädchenturnen, Volleyball & Tanz', who: 'ab 4. Klasse', place: 'limes',
    slots: [[2, '17:30', '19:00']],
    desc: 'Turnen, Tanz und die ersten Schritte im Volleyball.' },
  { dept: 'turnen', age: 'kids', icon: 'medal', title: 'Sportabzeichen', who: 'Familien, Kinder ab 6 Jahre', place: 'gto',
    slots: [[4, '18:30', '20:30']], months: [5, 6, 7, 8, 9, 10],
    desc: 'Laufen, Springen, Werfen – Training und Abnahme für die ganze Familie.' },
  // Turnen · Erwachsene
  { dept: 'turnen', age: 'adults', icon: 'stretch', title: 'Frauen-Gymnastik', who: 'Freizeit- und Gesundheitssport', place: 'rso',
    slots: [[0, '18:30', '19:45']], desc: 'Gemeinsam fit bleiben, Spaß haben und neue Kontakte knüpfen.' },
  { dept: 'turnen', age: 'adults', icon: 'stretch', title: 'Frauen-Gymnastik', who: 'Walken, Gymnastik, Aerobic', place: 'rso',
    slots: [[1, '20:00', '21:30']], desc: 'Abwechslungsreich: je nach Jahreszeit draußen walken oder in der Halle trainieren.' },
  { dept: 'turnen', age: 'adults', icon: 'walk', title: 'Walking & Nordic Walking', who: 'Erwachsene', place: 'sportheim',
    slots: [[1, '18:00', '19:00'], [3, '18:00', '19:00']], img: 'gen/walking.jpg',
    desc: 'Eine Stunde an der frischen Luft rund um Osterburken. Treffpunkt ist das Sportheim.' },
  { dept: 'turnen', age: 'adults', icon: 'fistball', title: 'Männer-Faustball', who: 'Erwachsene', place: 'limes',
    slots: [[3, '19:00', '20:30']], img: 'gen/faustball.jpg',
    desc: 'Schnelligkeit trifft Taktik – Ballsport mal anders.' },
  { dept: 'turnen', age: 'adults', icon: 'dumbbell', title: 'Männer-Fitness', who: 'Funktionsgymnastik & Volleyball', place: 'rso',
    slots: [[3, '20:00', '22:00']], desc: 'Erst Funktionsgymnastik, dann Volleyball.' },
  { dept: 'turnen', age: 'adults', icon: 'couple', title: 'Tanztreff', who: 'Paare, ohne Trainer', place: null, note: 'alle 2 Wochen',
    slots: [[6, '18:00', '20:00']], months: [10, 11, 12, 1, 2, 3], desc: 'Gemeinsam üben und tanzen – ohne Tanzlehrer, in lockerer Runde.' },

  // Fitness
  { dept: 'fitness', icon: 'music', title: 'Zumba Gold', who: 'Einsteiger & ruhigeres Tempo', place: 'limes', note: 'im Winter in der Aula',
    slots: [[0, '18:30', '19:30']] },
  { dept: 'fitness', icon: 'music', title: 'Zumba Fitness', who: 'Sportlich Aktive', place: 'limes', note: 'im Winter in der Aula',
    slots: [[0, '19:30', '20:30']] },
  { dept: 'fitness', icon: 'glove', title: 'Bodycombat', who: 'alle Fitnesslevel', place: 'sportplatz', note: 'bei Regen: Sporthalle Realschule',
    slots: [[0, '20:00', '21:00'], [2, '20:00', '21:00']] },
];
