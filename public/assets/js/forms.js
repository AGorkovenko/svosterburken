/* Online-Formulare: füllt die Original-PDFs des Vereins direkt im Browser aus.
   Es werden keine Daten an einen Server geschickt – das fertige PDF wird nur heruntergeladen.

   Markup-Konventionen im <form data-pdf-form data-pdf="…pdf" data-filename="…">:
   data-f="Feld1|Feld2"        Textfeld(er) im PDF; <input type="date"> wird als TT.MM.JJJJ eingetragen
   data-radio="Gruppe"         Radiogruppe im PDF, value = Exportwert (z. B. E, K, F)
   data-check="Feld"           Checkbox im PDF wird angehakt, wenn das Eingabefeld angehakt ist
   data-check-value            bei <input type="radio">: value = Name der PDF-Checkbox
   data-append-date            hängt das heutige Datum an (für Felder „Ort, Datum“)
   data-today="Feld1|Feld2"    (versteckt) heutiges Datum
   data-show-if="name=A,B" | "name>=2" | "name"   Abschnitt nur bei passender Auswahl zeigen
   <div class="sig" data-sig="[[seite,x,y,breite,höhe,bedingung?], …]">  Unterschriftsfeld */

(() => {
  const form = document.querySelector('[data-pdf-form]');
  if (!form) return;
  const { PDFDocument, StandardFonts, PDFName, PDFDict } = window.PDFLib;
  const norm = (s) => String(s).replace(/[^\x21-\x7e]/g, '');
  const pad = (n) => String(n).padStart(2, '0');
  const today = () => { const d = new Date(); return `${pad(d.getDate())}.${pad(d.getMonth() + 1)}.${d.getFullYear()}`; };
  const deDate = (v) => (/^\d{4}-\d{2}-\d{2}$/.test(v) ? v.split('-').reverse().join('.') : v);

  /* ---------- Bedingte Abschnitte ---------- */
  const value = (name) => {
    const els = form.querySelectorAll(`[name="${name}"]`);
    if (!els.length) return '';
    if (els[0].type === 'radio') return [...els].find((e) => e.checked)?.value || '';
    if (els[0].type === 'checkbox') return els[0].checked ? 'on' : '';
    return els[0].value;
  };
  const test = (cond) => {
    let m = cond.match(/^(\w+)>=(\d+)$/);
    if (m) return Number(value(m[1]) || 0) >= Number(m[2]);
    m = cond.match(/^(\w+)=(.+)$/);
    if (m) return m[2].split(',').includes(value(m[1]));
    return !!value(cond);
  };
  const update = () => {
    form.querySelectorAll('[data-show-if]').forEach((el) => {
      const show = el.dataset.showIf.split('&').every(test);
      el.hidden = !show;
      el.querySelectorAll('input, select, textarea').forEach((i) => { i.disabled = !show || !!i.closest('[hidden]'); });
    });
  };
  form.addEventListener('change', update);
  update();

  /* ---------- Unterschriften ---------- */
  const pads = [...form.querySelectorAll('[data-sig]')].map((box) => {
    const canvas = box.querySelector('canvas');
    const ctx = canvas.getContext('2d');
    let drawing = false; let empty = true;
    const fit = () => {
      const r = canvas.getBoundingClientRect(); const dpr = window.devicePixelRatio || 1;
      canvas.width = r.width * dpr; canvas.height = r.height * dpr;
      ctx.scale(dpr, dpr); ctx.lineWidth = 2.2; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.strokeStyle = '#0A1638';
      empty = true;
    };
    const pos = (e) => { const r = canvas.getBoundingClientRect(); return [e.clientX - r.left, e.clientY - r.top]; };
    canvas.addEventListener('pointerdown', (e) => { drawing = true; canvas.setPointerCapture(e.pointerId); ctx.beginPath(); ctx.moveTo(...pos(e)); });
    canvas.addEventListener('pointermove', (e) => { if (!drawing) return; ctx.lineTo(...pos(e)); ctx.stroke(); empty = false; });
    ['pointerup', 'pointercancel'].forEach((t) => canvas.addEventListener(t, () => { drawing = false; }));
    box.querySelector('[data-sig-clear]')?.addEventListener('click', fit);
    new ResizeObserver(() => { if (empty) fit(); }).observe(canvas);
    return { box, canvas, isEmpty: () => empty, spots: JSON.parse(box.dataset.sig) };
  });

  // Unterschrift auf den gezeichneten Bereich zuschneiden, damit sie im PDF groß genug erscheint
  function trimmedPng(canvas) {
    const { width: w, height: h } = canvas;
    const data = canvas.getContext('2d').getImageData(0, 0, w, h).data;
    let x0 = w, y0 = h, x1 = 0, y1 = 0;
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      if (data[(y * w + x) * 4 + 3] > 10) { if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y; }
    }
    const pad = 6; x0 = Math.max(0, x0 - pad); y0 = Math.max(0, y0 - pad); x1 = Math.min(w - 1, x1 + pad); y1 = Math.min(h - 1, y1 + pad);
    const out = document.createElement('canvas'); out.width = x1 - x0 + 1; out.height = y1 - y0 + 1;
    out.getContext('2d').drawImage(canvas, x0, y0, out.width, out.height, 0, 0, out.width, out.height);
    return out.toDataURL('image/png');
  }

  /* ---------- PDF ausfüllen ---------- */
  async function fill() {
    const bytes = await fetch(form.dataset.pdf).then((r) => { if (!r.ok) throw new Error('PDF nicht gefunden'); return r.arrayBuffer(); });
    const pdf = await PDFDocument.load(bytes);
    const pdfForm = pdf.getForm();
    const warn = (what, err) => console.warn('Feld nicht gesetzt:', what, err?.message || err);
    const setText = (name, v) => {
      try {
        const tf = pdfForm.getTextField(name);
        tf.setText(v);
        // Felder mit automatischer Schriftgröße (0 Tf) würden riesig – auf 11 pt festlegen
        if (/\s0(\.0+)?\s+Tf/.test(tf.acroField.getDefaultAppearance() || '')) tf.setFontSize(11);
      } catch (e) { warn(name, e); }
    };

    form.querySelectorAll('[data-f]').forEach((el) => {
      if (el.disabled || (el.type === 'radio' && !el.checked)) return;
      let v = deDate(el.value.trim());
      if (v && el.hasAttribute('data-append-date')) v += ', ' + today();
      if (v) el.dataset.f.split('|').forEach((n) => setText(n, v));
    });
    form.querySelectorAll('[data-today]').forEach((el) => {
      if (!el.disabled) el.dataset.today.split('|').forEach((n) => setText(n, today()));
    });
    // Radio-Optionen direkt über die Widgets der Seiten setzen: Einige Vereins-PDFs speichern jede
    // Option als eigenes Feld gleichen Namens, manche Widgets fehlen sogar im Feldverzeichnis.
    const N = (s) => PDFName.of(s);
    const widgetsNamed = (name) => {
      const out = [];
      for (const page of pdf.getPages()) {
        const annots = page.node.Annots();
        if (!annots) continue;
        for (let i = 0; i < annots.size(); i++) {
          const a = annots.lookup(i, PDFDict);
          if (!a || String(a.get(N('Subtype'))) !== '/Widget') continue;
          let field = a; let t = a.lookup(N('T'));
          if (!t) { field = a.lookup(N('Parent')); t = field && field.lookup(N('T')); }
          if (t && t.decodeText() === name) out.push({ a, field });
        }
      }
      return out;
    };
    const onState = (a) => {
      const ap = a.lookup(N('AP'), PDFDict); const n = ap && ap.lookup(N('N'));
      return n instanceof PDFDict ? n.keys().find((k) => k.decodeText() !== 'Off') : null;
    };
    form.querySelectorAll('[data-radio]:checked').forEach((el) => {
      if (el.disabled) return;
      const widgets = widgetsNamed(el.dataset.radio);
      const hit = widgets.find(({ a }) => { const k = onState(a); return k && norm(k.decodeText()).endsWith(el.value); });
      if (!hit) { warn(el.dataset.radio + '=' + el.value, 'Option fehlt'); return; }
      const chosen = onState(hit.a);
      for (const { a, field } of widgets) {
        a.set(N('AS'), a === hit.a ? chosen : N('Off'));
        field.set(N('V'), chosen);
      }
    });
    form.querySelectorAll('[data-check]:checked, [data-check-value]:checked').forEach((el) => {
      if (el.disabled) return;
      const name = el.dataset.check || el.value;
      try { pdfForm.getCheckBox(name).check(); } catch (e) { warn(name, e); }
    });

    const font = await pdf.embedFont(StandardFonts.Helvetica);
    try { pdfForm.updateFieldAppearances(font); } catch (e) { warn('Darstellung', e); }

    for (const p of pads) {
      if (p.isEmpty() || p.box.closest('[hidden]')) continue;
      const png = await pdf.embedPng(trimmedPng(p.canvas));
      for (const [page, x, y, w, h, cond] of p.spots) {
        if (cond && !cond.split('&').every(test)) continue;
        const s = Math.min(w / png.width, h / png.height);
        pdf.getPage(page).drawImage(png, { x, y, width: png.width * s, height: png.height * s });
      }
    }
    return pdf.save();
  }

  /* ---------- Absenden ---------- */
  const result = form.querySelector('[data-result]');
  const errorBox = form.querySelector('[data-error]');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    errorBox.hidden = true;
    const missingSig = pads.find((p) => p.box.hasAttribute('data-required') && !p.box.closest('[hidden]') && p.isEmpty());
    if (missingSig) {
      errorBox.textContent = 'Bitte unterschreibe im markierten Feld – oder lass die Unterschrift weg und unterschreibe den Ausdruck.';
      errorBox.hidden = false; missingSig.box.scrollIntoView({ block: 'center' }); return;
    }
    const btn = form.querySelector('[type="submit"]');
    btn.disabled = true; const label = btn.innerHTML; btn.textContent = 'PDF wird erstellt …';
    try {
      const out = await fill();
      const name = (form.querySelector('[data-name-part]')?.value || '').trim().replace(/[^\wäöüÄÖÜß-]+/g, '_');
      const file = `${form.dataset.filename}${name ? '_' + name : ''}.pdf`;
      const url = URL.createObjectURL(new Blob([out], { type: 'application/pdf' }));
      const a = document.createElement('a'); a.href = url; a.download = file; document.body.appendChild(a); a.click(); a.remove();
      result.querySelector('[data-file]').textContent = file;
      result.querySelector('[data-open]').href = url;
      result.hidden = false; result.scrollIntoView({ behavior: 'smooth', block: 'center' });
    } catch (err) {
      console.error(err);
      errorBox.textContent = 'Das PDF konnte nicht erstellt werden. Bitte lade das leere PDF herunter und fülle es von Hand aus.';
      errorBox.hidden = false;
    } finally {
      btn.disabled = false; btn.innerHTML = label;
    }
  });
})();
