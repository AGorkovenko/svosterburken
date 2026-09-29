#!/usr/bin/env python3
"""Erzeugt die Seiten der Online-Formulare (src/pages/formular-*.html).
Die Feldnamen entsprechen exakt den Formularfeldern in den Original-PDFs."""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / 'src/pages'


def field(label, attrs, required=True, span='', typ='text'):
    req = ' required' if required else ''
    star = ' <em>*</em>' if required else ''
    return f'<label class="field{span}"><span>{label}{star}</span><input type="{typ}" {attrs}{req}></label>'


def choice(name, pdf, options, required=True, cards=False, kind='radio'):
    req = ' required' if required else ''
    items = ''.join(
        f'<label><input type="{kind}" name="{name}" value="{v}" data-radio="{pdf}"{req}><span>{t}</span></label>'
        for v, t in options)
    return f'<div class="choice{" choice--cards" if cards else ""}">{items}</div>'


GENDER = [('m', 'männlich'), ('w', 'weiblich'), ('d', 'divers'), ('u', 'keine Angabe')]
DEPT = [('f', 'Fußball'), ('t', 'Turnen')]


def person(suffix, title, show_if, adult=False, name_part=False):
    np = ' data-name-part' if name_part else ''
    return f'''<div class="sub-fs" data-show-if="{show_if}">
  <h4>{{{{icon:user_icon}}}}{title}</h4>
  <div class="grid-2">
    {field('Vorname', f'name="vn{suffix}" data-f="txtVorname{suffix}" autocomplete="off"')}
    {field('Nachname', f'name="nn{suffix}" data-f="txtNachname{suffix}" autocomplete="off"{np}')}
    {field('Geburtsdatum' + (' (ab 18)' if adult else ' (unter 18)'), f'name="gb{suffix}" data-f="txtGeburtsdatum{suffix}"', typ='date')}
    <div class="field"><span>Abteilung <em>*</em></span>{choice('ab' + suffix, 'radioAbteilung' + suffix, DEPT)}</div>
    <div class="field span-2"><span>Geschlecht</span>{choice('ge' + suffix, 'radioGeschlecht' + suffix, GENDER, required=False)}</div>
  </div>
</div>'''.replace('{{icon:user_icon}}', '{{icon:users}}' if adult else '{{icon:child}}')


def page(meta, hero, body, aside, pdf, filename, submit_note):
    return f'''{meta}
---
<section class="page-hero">
  {{{{motif:stripes}}}}
  <div class="wrap">
    <nav class="crumbs" aria-label="Brotkrumen"><a href="downloads.html">Formulare</a><span>/</span><span>Online ausfüllen</span></nav>
    {hero}
  </div>
</section>
<section class="section section--tight">
  <div class="wrap form-layout">
    <form data-pdf-form data-pdf="assets/docs/{pdf}" data-filename="{filename}">
{body}
      <div class="form-submit">
        <p>{{{{icon:lock}}}}<span>{submit_note}</span></p>
        <button class="btn btn--light" type="submit">{{{{icon:download}}}}PDF erstellen</button>
      </div>
      <p class="form-error" data-error hidden role="alert"></p>
      <div class="form-result" data-result hidden role="status">
        <h3>{{{{icon:check}}}}Fertig: <span data-file></span></h3>
        <p>Das ausgefüllte PDF wurde heruntergeladen. So geht es weiter:</p>
        <ol>
          <li>PDF prüfen – du kannst es bei Bedarf noch bearbeiten.</li>
          <li>Unterschreiben, falls noch nicht geschehen.</li>
          <li>Beim Training abgeben oder per E-Mail an <a href="mailto:info@svosterburken.de">info@svosterburken.de</a> schicken.</li>
        </ol>
        <a class="btn btn--sm btn--ghost" data-open href="#" target="_blank">{{{{icon:file}}}}PDF öffnen</a>
      </div>
    </form>
    <aside class="form-aside">
{aside}
    </aside>
  </div>
</section>
'''


def sig(label, spots, show_if='', required=False):
    si = f' data-show-if="{show_if}"' if show_if else ''
    rq = ' data-required' if required else ''
    return f'''<div class="field span-2"{si}><span>{label}</span>
  <div class="sig" data-sig='{spots}'{rq}><canvas aria-label="{label}: mit Maus oder Finger unterschreiben"></canvas><span class="sig__line"></span>
  <div class="sig__bar"><span>Mit Maus oder Finger unterschreiben (optional)</span><button type="button" data-sig-clear>Löschen</button></div></div>
</div>'''


def aside(pdf_file, steps, extra=''):
    lis = ''.join(f'<li>{s}</li>' for s in steps)
    return f'''      <div class="card"><h3>{{{{icon:check}}}}So geht's</h3><ol>{lis}</ol></div>
      <div class="card"><h3>{{{{icon:lock}}}}Deine Daten</h3><p>Das Formular wird nur in deinem Browser ausgefüllt. Es wird nichts an die Website oder an Dritte übertragen.</p></div>
      <div class="card"><h3>{{{{icon:download}}}}Lieber auf Papier?</h3><p>Lade das leere PDF herunter und fülle es von Hand aus.</p><a class="btn btn--sm btn--ghost" href="assets/docs/{pdf_file}" download>{{{{icon:file}}}}Leeres PDF</a></div>{extra}'''


# ---------------- Mitgliedsantrag ----------------
ma_body = f'''      <fieldset class="fs">
        <legend><span class="num">1</span>Mitgliedschaft</legend>
        <div class="choice choice--cards">
          <label><input type="radio" name="art" value="E" data-radio="radioMitgliedschaft" required><span><b>69 €</b>Für mich<small>ab 18 Jahren, pro Jahr</small></span></label>
          <label><input type="radio" name="art" value="K" data-radio="radioMitgliedschaft"><span><b>59 €</b>Für mein Kind<small>bis 17 Jahre, pro Jahr</small></span></label>
          <label><input type="radio" name="art" value="F" data-radio="radioMitgliedschaft"><span><b>110 €</b>Familie<small>mich, Partner/-in und Kinder</small></span></label>
        </div>
        <div class="grid-2" style="margin-top:16px">
          {field('Eintrittsdatum', 'name="eintritt" data-f="txtEintrittsdatum"', typ='date')}
        </div>
      </fieldset>

      <fieldset class="fs">
        <legend><span class="num">2</span>Antragsteller/-in</legend>
        <p class="fs__hint" data-show-if="art=K">Du beantragst die Mitgliedschaft für dein Kind. Trag hier deine Daten als erziehungsberechtigte Person ein.</p>
        <div class="grid-2">
          {field('Vorname', 'name="vn" data-f="txtVornameAntragsteller" autocomplete="given-name"')}
          {field('Nachname', 'name="nn" data-f="txtNachnameAntragsteller" autocomplete="family-name" data-name-part')}
          {field('Geburtsdatum (ab 18)', 'name="gb" data-f="txtGeburtsdatumAntragsteller" autocomplete="bday"', typ='date')}
          <div class="field"><span>Geschlecht</span>{choice('ge', 'radioGeschlechtAntragsteller', GENDER, required=False)}</div>
        </div>
        <div class="grid-3" style="margin-top:14px">
          {field('Straße', 'name="str" data-f="txtStrasseAntragsteller" autocomplete="address-line1"')}
          {field('Hausnr.', 'name="hnr" data-f="txtHausNrAntragsteller"')}
          {field('PLZ', 'name="plz" data-f="txtPLZAntragsteller" autocomplete="postal-code" inputmode="numeric"')}
          {field('Ort', 'name="ort" data-f="txtOrtAntragsteller" autocomplete="address-level2"')}
          {field('Land', 'name="land" data-f="txtLandAntragsteller" value="Deutschland" autocomplete="country-name"')}
        </div>
        <div class="grid-2" style="margin-top:14px">
          {field('E-Mail', 'name="mail" data-f="txtEMail" autocomplete="email"', typ='email')}
          {field('Telefon', 'name="tel" data-f="txtTelefon" autocomplete="tel"', typ='tel')}
        </div>
        <div class="sub-fs" data-show-if="art=E,F">
          <h4>{{{{icon:ball}}}}Deine Abteilung</h4>
          {choice('ab', 'radioAbteilungAntragsteller', DEPT)}
        </div>
      </fieldset>

      <fieldset class="fs" data-show-if="art=K">
        <legend><span class="num">3</span>Dein Kind</legend>
        {person('Kind', 'Kind', 'art=K')}
      </fieldset>

      <fieldset class="fs" data-show-if="art=F">
        <legend><span class="num">3</span>Familie</legend>
        <label class="check"><input type="checkbox" name="partner" data-check="checkPartner"><span>Partner/-in wird Mitglied</span></label>
        <div class="field" style="margin-top:16px"><span>Anzahl Kinder <em>*</em></span>
          {choice('kids', 'choiceKinder', [(str(i), str(i)) for i in range(5)])}
        </div>
        {person('Partner', 'Partner/-in', 'partner', adult=True)}
        {person('Kind0', '1. Kind', 'kids>=1')}
        {person('Kind1', '2. Kind', 'kids>=2')}
        {person('Kind2', '3. Kind', 'kids>=3')}
        {person('Kind3', '4. Kind', 'kids>=4')}
      </fieldset>

      <fieldset class="fs">
        <legend><span class="num">4</span>SEPA-Lastschrift</legend>
        <p class="fs__hint">Der Beitrag wird jährlich per Lastschrift eingezogen. Gläubiger-ID des Vereins: DE59ZZZ00000614954.</p>
        <div class="field"><span>Wer zahlt? <em>*</em></span>
          {choice('zahler', 'checkSVOZahler', [('A', 'Antragsteller/-in'), ('N', 'Andere Person')])}
        </div>
        <div class="sub-fs" data-show-if="zahler=N">
          <h4>{{{{icon:users}}}}Kontoinhaber/-in</h4>
          <div class="grid-2">
            {field('Vorname', 'name="zvn" data-f="txtVornameZahler"')}
            {field('Nachname', 'name="znn" data-f="txtNachnameZahler"')}
            {field('Geburtsdatum (ab 18)', 'name="zgb" data-f="txtGeburtsdatumZahler"', typ='date')}
          </div>
          <div class="grid-3" style="margin-top:14px">
            {field('Straße', 'name="zstr" data-f="txtStrasseZahler"')}
            {field('Hausnr.', 'name="zhnr" data-f="txtHausNrZahler"')}
            {field('PLZ', 'name="zplz" data-f="txtPLZZahler" inputmode="numeric"')}
            {field('Ort', 'name="zort" data-f="txtOrtZahler"')}
            {field('Land', 'name="zland" data-f="txtLandZahler" value="Deutschland"')}
          </div>
        </div>
        <div class="grid-2" style="margin-top:14px">
          {field('IBAN', 'name="iban" data-f="txtIBANZahler" autocomplete="off" maxlength="42" pattern="[A-Za-z]{2}[0-9 ]{2}[A-Za-z0-9 ]{10,38}" placeholder="DE00 0000 0000 0000 0000 00"')}
          {field('BIC', 'name="bic" data-f="txtBICZahler" autocomplete="off" maxlength="11"', required=False)}
        </div>
        <label class="check" style="margin-top:16px"><input type="checkbox" name="sepa" required><span>Ich ermächtige den SV 1919 Osterburken e.V., den Beitrag von meinem Konto per Lastschrift einzuziehen. <small>Ich kann innerhalb von acht Wochen ab Belastungsdatum die Erstattung verlangen.</small></span></label>
      </fieldset>

      <fieldset class="fs">
        <legend><span class="num">5</span>Einverständnis &amp; Unterschrift</legend>
        <label class="check"><input type="checkbox" name="satzung" required><span>Ich erkenne die <a href="assets/docs/Vereinssatzung_2017.pdf" target="_blank">Vereinssatzung</a> an und bin einverstanden, Informationen und Einladungen des Vereins per E-Mail, Telefon und Messenger zu erhalten.</span></label>
        <div class="grid-2" style="margin-top:16px">
          {field('Ort', 'name="uort" data-f="txtOrtEinverstaendnis|txtOrtUnterschreiber" value="Osterburken"')}
          <input type="hidden" data-today="txtDatumEinverstaendnis|txtDatumUnterschreiber">
          {sig('Unterschrift Antragsteller/-in', '[[0,282,87,240,34],[3,278,76,240,34,"zahler=A"]]')}
          {sig('Unterschrift Kontoinhaber/-in (SEPA)', '[[3,278,76,240,34]]', show_if='zahler=N')}
        </div>
      </fieldset>'''

ma = page(
    'title: Mitgliedsantrag online ausfüllen – SV 1919 Osterburken e.V.\n'
    'description: Aufnahmeantrag des SV 1919 Osterburken e.V. online ausfüllen und als PDF speichern.\n'
    'theme: verein\nnav: verein\nscripts: vendor/pdf-lib.min.js, js/forms.js',
    '<p class="eyebrow">Aufnahmeantrag 2026</p><h1 class="display">Mitglied werden</h1>'
    '<p class="lead">Füll den Antrag hier aus – am Ende bekommst du das offizielle Vereins-PDF mit all deinen Angaben zum Speichern oder Ausdrucken.</p>',
    ma_body,
    aside('SVO_Mitgliedsantrag_2026.pdf', ['Formular ausfüllen und optional unterschreiben.', '„PDF erstellen“ klicken – die Datei wird gespeichert.',
          'Unterschrieben beim Training abgeben oder an info@svosterburken.de schicken.']),
    'SVO_Mitgliedsantrag_2026.pdf', 'SVO_Mitgliedsantrag',
    'Das PDF wird in deinem Browser erstellt. Deine Angaben – auch die IBAN – werden nirgendwohin übertragen.')

# ---------------- Erstmalige Spielerlaubnis ----------------
sp_body = f'''      <input type="hidden" data-f="Antragstellender Verein" value="SV 1919 Osterburken e.V.">
      <fieldset class="fs">
        <legend><span class="num">1</span>Spielberechtigung</legend>
        <div class="choice">
          <label><input type="checkbox" name="fb" data-check="Fußball" checked><span>Fußball</span></label>
          <label><input type="checkbox" name="fs" data-check="Futsal"><span>Futsal</span></label>
        </div>
      </fieldset>
      <fieldset class="fs">
        <legend><span class="num">2</span>Spieler/-in</legend>
        <div class="grid-2">
          {field('Nachname', 'name="nn" data-f="Name des Spielers" data-name-part')}
          {field('Vorname(n)', 'name="vn" data-f="Vorname des Spielers"')}
          {field('Geburtsdatum', 'name="gb" data-f="Geburtsdatum_af_date"', typ='date')}
          <div class="field"><span>Geschlecht <em>*</em></span><div class="choice">
            <label><input type="radio" name="ge" value="Geschlecht männlich" data-check-value required><span>männlich</span></label>
            <label><input type="radio" name="ge" value="Geschlecht weiblich" data-check-value><span>weiblich</span></label>
            <label><input type="radio" name="ge" value="Geschlecht divers" data-check-value><span>divers</span></label>
          </div></div>
          {field('Anschrift (Straße, PLZ, Ort)', 'name="adr" data-f="Anschrift"', span=' span-2')}
          {field('Nationalität', 'name="nat" data-f="Nationalität" value="deutsch"')}
          {field('Geburtsort (nur bei ausländischen Spielern)', 'name="gort" data-f="Geburtsort"', required=False)}
        </div>
        <p class="fs__hint" style="margin-top:16px">Spieler ohne deutsche Staatsbürgerschaft, die bisher nirgends registriert waren, brauchen zusätzlich eine Ausweiskopie – Jugendliche zwischen 10 und 18 Jahren außerdem eine Meldebescheinigung.</p>
      </fieldset>
      <fieldset class="fs">
        <legend><span class="num">3</span>Einwilligungen (freiwillig)</legend>
        <label class="check"><input type="checkbox" data-check="dass das für den Spielerpass zur Verfügung gestellte Lichtbild auch zur Veröffentlichung auf den"><span>Das Passfoto darf auf den Internetseiten des Verbands und auf FUSSBALL.DE veröffentlicht werden. <small>Jederzeit widerrufbar.</small></span></label>
        <label class="check" style="margin-top:12px"><input type="checkbox" data-check="Hiermit stimmt der Spieler  bei Minderjährigen derdie gesetzlichen Vertreter  der Nutzung und"><span>Meine Adressdaten dürfen für Marketingzwecke des DFB, seiner Verbände und Partner genutzt werden. <small>Jederzeit widerrufbar.</small></span></label>
      </fieldset>
      <fieldset class="fs">
        <legend><span class="num">4</span>Unterschriften</legend>
        <p class="fs__hint">Mit der Unterschrift wird die Richtigkeit der Angaben bestätigt. Bei Minderjährigen unterschreiben zusätzlich die gesetzlichen Vertreter.</p>
        <div class="grid-2">
          {field('Ort', 'name="ort" data-f="Ort Datum" data-append-date value="Osterburken"')}
          {sig('Unterschrift Spieler/-in', '[[1,205,199,108,28]]')}
          {sig('Unterschrift gesetzl. Vertreter (bei Minderjährigen)', '[[1,330,198,180,28]]')}
        </div>
      </fieldset>'''

sp = page(
    'title: Spielerlaubnis online beantragen – SV 1919 Osterburken e.V.\n'
    'description: Antrag auf erstmalige Spielerlaubnis für den SV 1919 Osterburken online ausfüllen.\n'
    'theme: fussball\nnav: fussball\nscripts: vendor/pdf-lib.min.js, js/forms.js',
    '<p class="eyebrow">Fußball</p><h1 class="display">Spieler&shy;erlaubnis</h1>'
    '<p class="lead">Für alle, die zum ersten Mal einen Spielerpass bekommen – noch nie für einen anderen Verein gemeldet, auch nicht im Ausland.</p>',
    sp_body,
    aside('Antrag-erstmalige-Spielerlaubnis_beschreibbar.pdf', ['Formular ausfüllen und unterschreiben.', '„PDF erstellen“ klicken.',
          'PDF an fussball@svosterburken.de schicken oder beim Training abgeben.']),
    'Antrag-erstmalige-Spielerlaubnis_beschreibbar.pdf', 'SVO_Spielerlaubnis',
    'Das PDF wird in deinem Browser erstellt. Deine Angaben werden nirgendwohin übertragen.')

# ---------------- Vereinswechsel ----------------
P = 'Fußball Futsal Freizeit nur beim wfv'
vw_body = f'''      <input type="hidden" data-f="Antragstellender Verein" value="SV 1919 Osterburken e.V.">
      <fieldset class="fs">
        <legend><span class="num">1</span>Spielberechtigung</legend>
        {choice('art', 'Gruppe1', [('Auswahl1', 'Fußball'), ('Auswahl2', 'Futsal')])}
      </fieldset>
      <fieldset class="fs">
        <legend><span class="num">2</span>Spieler/-in</legend>
        <div class="grid-2">
          {field('Nachname', f'name="nn" data-f="{P}Nachname des Spielersin" data-name-part')}
          {field('Vorname', f'name="vn" data-f="{P}Vorname des Spielersin"')}
          {field('Geburtsdatum', f'name="gb" data-f="{P}Geburtsdatum"', typ='date')}
          {field('Passnummer', f'name="pass" data-f="{P}Passnummer"', required=False)}
          {field('Anschrift (Straße, PLZ, Ort)', f'name="adr" data-f="{P}Anschrift Straße PLZ Ort"', span=' span-2')}
          {field('Nationalität', f'name="nat" data-f="{P}Nationalität" value="deutsch"')}
        </div>
      </fieldset>
      <fieldset class="fs">
        <legend><span class="num">3</span>Bisheriger Verein</legend>
        <div class="grid-2">
          {field('Abgebender Verein', f'name="alt" data-f="{P}Abgebender Verein"')}
          {field('Abgebender National-/Landesverband', f'name="verband" data-f="{P}Abgebender NationalLandesverband" value="bfv"')}
        </div>
        <div class="field" style="margin-top:16px"><span>Abmeldung beim bisherigen Verein <em>*</em></span>
          <div class="choice" style="display:grid;gap:8px">
            <label><input type="radio" name="abm" value="Auswahl1" data-radio="Abmeldung" required><span>Ich habe mich bereits schriftlich abgemeldet (Kündigung oder Bestätigung liegt vor).</span></label>
            <label><input type="radio" name="abm" value="Auswahl2" data-radio="Abmeldung"><span>Ich bin noch nicht abgemeldet und beauftrage den SVO, mich über DFBnet abzumelden.</span></label>
          </div>
        </div>
      </fieldset>
      <fieldset class="fs">
        <legend><span class="num">4</span>Einwilligungen (freiwillig)</legend>
        <label class="check"><input type="checkbox" data-check="Kontrollkästchen5"><span>Das Passfoto darf auf den Internetseiten des Verbands und auf FUSSBALL.DE veröffentlicht werden. <small>Jederzeit widerrufbar.</small></span></label>
        <label class="check" style="margin-top:12px"><input type="checkbox" data-check="Kontrollkästchen6"><span>Meine Adressdaten dürfen für Marketingzwecke des DFB, seiner Verbände und Partner genutzt werden. <small>Jederzeit widerrufbar.</small></span></label>
      </fieldset>
      <fieldset class="fs">
        <legend><span class="num">5</span>Unterschriften</legend>
        <div class="grid-2">
          {field('Ort', 'name="ort" data-f="Ort Datum" data-append-date value="Osterburken"')}
          {sig('Unterschrift Spieler/-in', '[[1,205,268,108,28]]')}
          {sig('Unterschrift gesetzl. Vertreter (bei Minderjährigen)', '[[1,332,268,180,28]]')}
        </div>
      </fieldset>'''

vw = page(
    'title: Vereinswechsel online beantragen – SV 1919 Osterburken e.V.\n'
    'description: Antrag auf Vereinswechsel zum SV 1919 Osterburken online ausfüllen.\n'
    'theme: fussball\nnav: fussball\nscripts: vendor/pdf-lib.min.js, js/forms.js',
    '<p class="eyebrow">Fußball</p><h1 class="display">Vereins&shy;wechsel</h1>'
    '<p class="lead">Du spielst schon in einem anderen Verein und willst zum SVO wechseln? Dann füll diesen Antrag aus.</p>',
    vw_body,
    aside('Antrag-Vereinswechsel_beschreibbar.pdf', ['Formular ausfüllen und unterschreiben.', '„PDF erstellen“ klicken.',
          'PDF an fussball@svosterburken.de schicken oder beim Training abgeben.']),
    'Antrag-Vereinswechsel_beschreibbar.pdf', 'SVO_Vereinswechsel',
    'Das PDF wird in deinem Browser erstellt. Deine Angaben werden nirgendwohin übertragen.')

(OUT / 'formular-mitgliedsantrag.html').write_text(ma)
(OUT / 'formular-spielerlaubnis.html').write_text(sp)
(OUT / 'formular-vereinswechsel.html').write_text(vw)
print('3 Formularseiten erzeugt')
