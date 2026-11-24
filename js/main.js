/* ============================================================
   Bu fayl faqat INTERFEYS: server (Python) qaytargan ma'lumotni chizadi.
   Hamma matn esc() orqali xavfsiz ko'rsatiladi.
   ============================================================ */
const $ = id => document.getElementById(id);
const ALPHA = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

/* ---------------- Python backend (Web Worker + Pyodide) ---------------- */
let _worker = null, _seq = 0;
const _pending = new Map();
let _bootResolve, _bootReject;
const booted = new Promise((res, rej) => { _bootResolve = res; _bootReject = rej; });

function startBackend() {
  if (location.protocol === 'file:') {
    _bootReject(new Error('file'));
    return;
  }
  try {
    _worker = new Worker('js/worker.js', { type: 'module' });
  } catch (e) { _bootReject(e); return; }
  _worker.onmessage = (ev) => {
    const m = ev.data;
    if (m.type === 'progress') setBootText(m.text);
    else if (m.type === 'ready') _bootResolve();
    else if (m.type === 'fatal') _bootReject(new Error(m.error));
    else if (m.type === 'result') {
      const cb = _pending.get(m.id); _pending.delete(m.id);
      if (cb) { try { cb(JSON.parse(m.out)); } catch (e) { cb({ error: "Backend javobi noto'g'ri." }); } }
    }
  };
  _worker.onerror = (e) => _bootReject(new Error(e.message || 'worker'));
}

function callBackend(method, path, body) {
  return new Promise((resolve) => {
    const id = ++_seq;
    _pending.set(id, resolve);
    _worker.postMessage({ id, method, path, body: body ? JSON.stringify(body) : '{}' });
  });
}

async function api(path, body) {
  try {
    await booted;
    return await callBackend('POST', path, body || {});
  } catch (e) {
    return { error: "Python backend ishga tushmadi. Sahifani yangilang (F5)." };
  }
}

function setBootText(t) { const el = document.getElementById('boot-text'); if (el) el.textContent = t; }
function hideBoot() { const el = document.getElementById('boot'); if (el) el.classList.add('hidden'); }
function bootError(e) {
  const el = document.getElementById('boot'); if (!el) return;
  const file = String(e && e.message) === 'file';
  el.querySelector('.boot-spin').style.display = 'none';
  el.querySelector('#boot-text').innerHTML = file
    ? "<b>Bu sahifani faylni ikki marta bosib ochib bo'lmaydi.</b><br>Brauzer xavfsizligi Python'ni fayldan yuklashga ruxsat bermaydi. Saytni havola (https://…) orqali oching."
    : "<b>Yuklanmadi.</b><br>Internetni tekshirib, sahifani yangilang (F5). Eski brauzer bo'lsa, Chrome, Edge, Firefox yoki Safari 15+ dan foydalaning.<br><small>" + esc(e && e.message) + "</small>";
}

let CATALOG = { algorithms: [], tools: [], errors: {} };
const algoById = id => CATALOG.algorithms.find(a => a.id === id);
const toolById = id => CATALOG.tools.find(t => t.id === id);

/* ---------------- Navigatsiya ---------------- */
function goHome() { stepPause(); openPage('page-home'); }
function openPage(id) {
  document.querySelectorAll('main > div[id^="page-"]').forEach(p => p.classList.toggle('hidden', p.id !== id));
  window.scrollTo(0, 0);
}

async function init() {
  startBackend();
  try {
    await booted;
    CATALOG = await callBackend('GET', '/api/catalog');
  } catch (e) {
    bootError(e);
    return;
  }
  hideBoot();
  $('cipher-nav').innerHTML = CATALOG.algorithms.map(a =>
    `<div class="nav-btn" onclick="openModule('${esc(a.id)}')">${esc(a.name)}<small>${esc(a.desc.slice(0, 40))}...</small></div>`).join('');
  $('tool-nav').innerHTML = CATALOG.tools.map(t =>
    `<div class="nav-btn" onclick="openTool('${esc(t.id)}')">${esc(t.title)}<small>${esc(t.subtitle || '')}</small></div>`).join('');
  const main = document.querySelector('main');
  CATALOG.tools.forEach(t => {
    if ($('page-tool-' + t.id)) return;
    const d = document.createElement('div');
    d.id = 'page-tool-' + t.id; d.className = 'hidden';
    main.appendChild(d);
  });
  const errs = Object.entries(CATALOG.errors || {});
  $('load-errors').innerHTML = errs.map(([f, m]) => `<div class="err-box load-error"><b>${esc(f)}</b> yuklanmadi: ${esc(m)}</div>`).join('');
}

/* ---------------- Vizual spetsifikatsiya chizuvchisi ---------------- */
const COLORS = { gold: '#fbbf24', blue: '#60a5fa', red: '#f87171', green: '#4ade80', lime: '#86efac', violet: '#a78bfa', pink: '#f472b6', cyan: '#38bdf8', orange: '#fb923c', slate: '#94a3b8', dim: '#64748b', white: '#fff' };
const HL = ['#16a34a', '#2563eb', '#7c3aed', '#ea580c'];
const col = c => COLORS[c] || 'inherit';
function sp(p) {
  if (typeof p === 'string') return esc(p);
  return `<span style="${p.c ? 'color:' + col(p.c) + ';' : ''}${p.b ? 'font-weight:bold;' : ''}">${esc(p.t)}</span>`;
}
const sps = a => (a || []).map(sp).join('');

function stateGrid(it) {
  const bg = it.hl != null ? HL[it.hl % 4] : '#1e3a5f';
  let rows = '';
  for (let r = 0; r < 4; r++) {
    rows += '<tr>' + [0, 1, 2, 3].map(c => {
      const b = it.bytes[c * 4 + r];
      return `<td style="background:${bg};color:#fff;padding:3px 6px;border:1px solid #0f172a;text-align:center;font-weight:bold">${b === undefined ? '' : b.toString(16).toUpperCase().padStart(2, '0')}</td>`;
    }).join('') + '</tr>';
  }
  return `<div style="text-align:center"><div style="font-size:10px;color:#94a3b8;font-family:Arial;margin-bottom:3px">${esc(it.label)}</div><table style="border-collapse:collapse;margin:0">${rows}</table></div>`;
}

function renderBlock(b) {
  switch (b.k) {
    case 'line': return `<div style="margin-top:${b.gap ? 8 : 2}px">${sps(b.parts)}</div>`;
    case 'chips': return `<div style="display:flex;flex-wrap:wrap;gap:6px;margin:6px 0">${b.items.map(i =>
      `<span style="background:#1e3a5f;padding:3px 7px;border-radius:4px;${i.c ? 'color:' + col(i.c) : ''}">${esc(i.t)}</span>`).join('')}</div>`;
    case 'table': {
      const head = b.head ? `<tr>${b.head.map(h => `<th>${esc(h)}</th>`).join('')}</tr>` : '';
      return `<div style="overflow-x:auto"><table>${head}${b.rows.map(r => `<tr>${r.map(c => `<td>${sp(c)}</td>`).join('')}</tr>`).join('')}</table></div>`;
    }
    case 'states': return `<div style="display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:center;margin:8px 0">${b.items.map(it =>
      it.op ? `<span style="font-size:18px;color:#fbbf24;font-weight:bold">${esc(it.op)}</span>` : stateGrid(it)).join('')}</div>`;
    case 'cols': return `<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:8px 0">${b.items.map(it =>
      `<div style="background:#0f172a;border-left:3px solid ${col(it.color)};padding:8px 10px;border-radius:4px">
        <div style="font-size:10.5px;color:${col(it.color)};font-family:Arial;margin-bottom:4px">${esc(it.title)}</div>
        ${it.lines.map(l => `<div>${sps(l)}</div>`).join('')}
        ${it.result ? `<div style="border-top:1px solid #334155;margin-top:4px;padding-top:4px">${sps(it.result)}</div>` : ''}</div>`).join('')}</div>`;
    case 'note': return `<div style="background:#0f172a;border-left:3px solid ${col(b.color)};padding:8px 10px;margin-top:8px;font-size:11px;line-height:1.6;border-radius:4px">${b.lines.map(l => `<div>${sps(l)}</div>`).join('')}</div>`;
  }
  return '';
}

function renderVisual(v) {
  if (!v) return '';
  switch (v.type) {
    case 'flow': return `<div class="flow">${v.items.map(i => `<div class="fbox ${esc(i.cls || '')}">${esc(i.text)}</div>`).join('<span class="farrow">→</span>')}</div>`;
    case 'grid': {
      const head = v.header ? `<tr>${v.header.map(h => `<th>${esc(h)}</th>`).join('')}</tr>` : '';
      return `<div style="overflow-x:auto"><table class="grid-table" style="margin:0 auto">${head}${v.rows.map(r => `<tr>${r.map(c => `<td class="${esc(c.cls)}">${esc(c.v)}</td>`).join('')}</tr>`).join('')}</table></div>`;
    }
    case 'text': return `<div class="vtext">${esc(v.text)}</div>`;
    case 'panel': return `<div class="vpanel"><div class="vt">${esc(v.title)}</div>${v.blocks.map(renderBlock).join('')}</div>`;
  }
  return '';
}

/* ---------------- Shifr moduli (barcha algoritmlar uchun umumiy) ---------------- */
let cur = null, curMode = 'learn', steps = [], stepIdx = -1, tableCols = [], playTimer = null, speedMs = 900, runToken = 0, liveTimer = null;

function openModule(id) {
  cur = algoById(id);
  if (!cur) return;
  $('m-title').textContent = cur.name;
  $('m-desc').textContent = cur.desc;
  $('m-formulas').innerHTML =
    `<div class="formula-box"><span>ENCRYPT FORMULA</span>${esc(cur.formula_enc)}</div>` +
    `<div class="formula-box"><span>DECRYPT FORMULA</span>${esc(cur.formula_dec)}</div>`;
  $('m-map').textContent = cur.map;
  $('m-weak').innerHTML = `<b>Zaiflik / Attack:</b> ${esc(cur.weak)}`;
  const ex = cur.explainer || {};
  $('m-explainer').innerHTML =
    `<div><b>Nima uchun?</b>${esc(ex.why)}</div><div><b>Qanday ishlaydi?</b>${esc(ex.how)}</div>` +
    `<div><b>Matematik amal</b>${esc(ex.math)}</div><div><b>Zaifligi</b>${esc(ex.weak)}</div>`;

  $('m-inputs').innerHTML = cur.inputs.map(f => {
    let el;
    if (f.type === 'select') el = `<select id="inp-${esc(f.id)}">${f.options.map(o => `<option value="${esc(o.value)}"${String(o.value) === String(f.default) ? ' selected' : ''}>${esc(o.label)}</option>`).join('')}</select>`;
    else el = `<input id="inp-${esc(f.id)}" type="${f.type === 'number' ? 'number' : 'text'}" value="${esc(f.default)}" spellcheck="false" autocomplete="off">`;
    return `<div class="field"><label>${esc(f.label)}</label>${el}</div>`;
  }).join('') + ((cur.actions || []).length ? `<div class="field-actions">${cur.actions.map(a =>
    `<button class="btn btn-outline btn-sm" onclick="runAction('${esc(a.id)}')">${esc(a.label)}</button>`).join('')}</div>` : '');

  $('m-examples').innerHTML = '<div style="font-size:11.5px;color:var(--slate);margin-bottom:4px;">Tayyor misollar:</div>' +
    (cur.examples || []).map((e, i) => `<button class="btn btn-sm" onclick="loadExample(${i})">Misol ${i + 1}</button>`).join('');
  $('m-live').innerHTML = '';
  $('m-inputs').oninput = $('m-inputs').onchange = scheduleLive;

  setMode('learn');
  resetModule();
  openPage('page-module');
  scheduleLive();
}

function collectVals() {
  const v = {};
  cur.inputs.forEach(f => { v[f.id] = $('inp-' + f.id).value; });
  return v;
}
function loadExample(i) {
  const ex = cur.examples[i];
  cur.inputs.forEach((f, idx) => { $('inp-' + f.id).value = ex[idx] !== undefined ? ex[idx] : f.default; });
  scheduleLive();
}
function scheduleLive() {
  if (!cur || !cur.has_live) return;
  clearTimeout(liveTimer);
  const id = cur.id;
  liveTimer = setTimeout(async () => {
    const out = await api(`/api/algo/${id}/live`, { vals: collectVals() });
    if (cur && cur.id === id && out.visual) $('m-live').innerHTML = renderVisual(out.visual);
  }, 200);
}
async function runAction(actionId) {
  const out = await api(`/api/algo/${cur.id}/action`, { action: actionId, vals: collectVals() });
  if (out.error) { $('m-error').innerHTML = `<div class="err-box">${esc(out.error)}</div>`; return; }
  $('m-error').innerHTML = '';
  Object.entries(out.fill || {}).forEach(([k, v]) => { if ($('inp-' + k)) $('inp-' + k).value = v; });
  scheduleLive();
}

function setMode(m) {
  curMode = m;
  $('mode-learn').classList.toggle('active', m === 'learn');
  $('mode-practice').classList.toggle('active', m === 'practice');
  $('predict-area').innerHTML = '';
}

async function runCipher(mode) {
  const be = $('btn-enc'), bd = $('btn-dec');
  [be, bd].forEach(b => b.classList.remove('btn-active-enc', 'btn-active-dec'));
  (mode === 'enc' ? be : bd).classList.add(mode === 'enc' ? 'btn-active-enc' : 'btn-active-dec');
  stepPause();
  const token = ++runToken;
  const out = await api(`/api/algo/${cur.id}/run`, { mode, vals: collectVals() });
  if (token !== runToken) return;                 // eskirgan javob
  $('m-error').innerHTML = ''; $('m-result').innerHTML = '';
  if (out.error) {
    $('m-error').innerHTML = `<div class="err-box">${esc(out.error)}</div>`;
    steps = []; tableCols = []; renderTable(); renderStage(-1);
    return;
  }
  steps = out.steps; tableCols = out.table_cols || []; stepIdx = -1;
  $('m-result').innerHTML = renderVisual(out.extra) + `<div class="result-box">Natija: ${esc(out.result)}</div>`;
  renderTable();
  stepNext();
}
function resetModule() {
  stepPause(); runToken++;
  steps = []; stepIdx = -1; tableCols = [];
  $('m-error').innerHTML = ''; $('m-result').innerHTML = ''; $('predict-area').innerHTML = '';
  ['btn-enc', 'btn-dec'].forEach(i => $(i).classList.remove('btn-active-enc', 'btn-active-dec'));
  renderTable(); renderStage(-1);
}

function showStep(step) {
  $('m-stage').innerHTML = renderVisual(step.visual) + `<div class="step-desc">${esc(step.desc)}</div>`;
}
function renderStage(idx) {
  const total = steps.length;
  if (idx < 0 || total === 0) {
    $('m-stage').innerHTML = '<div class="step-desc">Encrypt yoki Decrypt tugmasini bosing.</div>';
    $('m-progress-label').textContent = `Step 0 / ${total}`;
    $('m-progress-fill').style.width = '0%';
    return;
  }
  const step = steps[idx];
  $('m-progress-label').textContent = `Step ${idx + 1} / ${total}`;
  $('m-progress-fill').style.width = ((idx + 1) / total * 100) + '%';
  if (curMode === 'practice' && step.answer) renderPredict(step); else showStep(step);
  highlightRow(idx);
}
function renderPredict(step) {
  const correct = step.answer, opts = new Set([correct]);
  while (opts.size < 4) opts.add(ALPHA[Math.floor(Math.random() * 26)]);
  const arr = Array.from(opts).sort(() => Math.random() - 0.5);
  $('m-stage').innerHTML = `<div class="predict-box"><b>Men keyingi qadamni topaman:</b> natija harfi qaysi?
    <div class="predict-opts">${arr.map(o => `<button data-o="${esc(o)}" onclick="checkPredict(this,'${esc(correct)}')">${esc(o)}</button>`).join('')}</div>
    <div id="predict-feedback"></div></div>`;
}
function checkPredict(btn, correct) {
  const chosen = btn.dataset.o, fb = $('predict-feedback');
  if (chosen === correct) { btn.classList.add('correct'); fb.innerHTML = '<div class="feedback ok">✓ To\'g\'ri!</div>'; }
  else { btn.classList.add('wrong'); fb.innerHTML = `<div class="feedback bad">✗ Noto'g'ri. To'g'ri javob: ${esc(correct)}. Formula va joriy qadamni tekshiring.</div>`; }
  const at = stepIdx;
  setTimeout(() => { if (stepIdx === at && steps[at]) showStep(steps[at]); }, 1200);
}
function renderTable() {
  const t = $('m-table');
  if (!steps.length || !tableCols.length) { t.innerHTML = ''; return; }
  let h = '<tr>' + tableCols.map(c => `<th>${esc(c)}</th>`).join('') + '</tr>';
  steps.forEach((s, i) => { if (s.row) h += `<tr data-idx="${i}">${s.row.map(v => `<td>${esc(v)}</td>`).join('')}</tr>`; });
  t.innerHTML = h;
}
function highlightRow(idx) {
  document.querySelectorAll('#m-table tr').forEach(tr => tr.classList.remove('current'));
  const tr = document.querySelector(`#m-table tr[data-idx="${idx}"]`);
  if (tr) tr.classList.add('current');
}
function stepNext() { if (stepIdx < steps.length - 1) { stepIdx++; renderStage(stepIdx); } else stepPause(); }
function stepPrev() { if (stepIdx > 0) { stepIdx--; renderStage(stepIdx); } }
function stepPlay() {
  if (!steps.length) return;
  stepPause();
  playTimer = setInterval(() => { if (stepIdx >= steps.length - 1) { stepPause(); return; } stepNext(); }, speedMs);
}
function stepPause() { if (playTimer) { clearInterval(playTimer); playTimer = null; } }
function setSpeed(v) {
  speedMs = { 1: 1600, 2: 900, 3: 400 }[v];
  $('speed-label').textContent = { 1: 'Slow', 2: 'Normal', 3: 'Fast' }[v];
  if (playTimer) stepPlay();
}

/* ---------------- Yordamchi funksiyalar (tools/) ---------------- */
async function openTool(id) {
  const t = toolById(id);
  if (!t) return;
  stepPause();
  openPage('page-tool-' + id);
  const box = $('page-tool-' + id);
  const renderer = { table: toolTable, tasks: toolTasks, quiz: toolQuiz, form: toolForm }[t.kind];
  if (!renderer) { box.innerHTML = `<div class="err-box">Noma'lum turdagi sahifa: ${esc(t.kind)}</div>`; return; }
  await renderer(t, box);
}
const toolApi = (t, action, payload) => api(`/api/tool/${t.id}`, { action, payload });
const titleH2 = t => `<h2 style="color:var(--navy);font-family:Arial,sans-serif;">${esc(t.title)}</h2>`;

/* --- kind: table --- */
async function toolTable(t, box) {
  const d = await toolApi(t, 'load', {});
  if (d.error) { box.innerHTML = titleH2(t) + `<div class="err-box">${esc(d.error)}</div>`; return; }
  const cell = c => typeof c === 'object' ? (c.b ? `<b>${esc(c.t)}</b>` : esc(c.t)) : esc(c);
  box.innerHTML = titleH2(t) + `<table class="cmp"><tr>${d.head.map(h => `<th>${esc(h)}</th>`).join('')}</tr>` +
    d.rows.map(r => `<tr>${r.map(c => `<td>${cell(c)}</td>`).join('')}</tr>`).join('') + '</table>';
}

/* --- kind: tasks --- */
async function toolTasks(t, box) {
  const d = await toolApi(t, 'list', {});
  if (d.error) { box.innerHTML = titleH2(t) + `<div class="err-box">${esc(d.error)}</div>`; return; }
  box.innerHTML = titleH2(t) + d.tasks.map((k, i) => `
    <div class="task-card">
      <span class="lvl">${esc(k.lvl)}</span>
      <h4>${i + 1}. ${esc(k.text)}</h4>
      <input type="text" id="task-ans-${i}" placeholder="Javobingiz" autocomplete="off">
      <button class="btn btn-primary btn-sm" onclick="taskCheck('${esc(t.id)}','${esc(k.id)}',${i})">Tekshirish</button>
      <button class="btn btn-outline btn-sm" onclick="taskReveal('${esc(t.id)}','${esc(k.id)}',${i})">Javobni ko'rish</button>
      <div id="task-fb-${i}" style="margin-top:8px;font-weight:bold;font-family:Arial,sans-serif;font-size:13px;"></div>
    </div>`).join('');
}
async function taskCheck(tid, id, i) {
  const r = await toolApi(toolById(tid), 'check', { id, answer: $('task-ans-' + i).value });
  $('task-fb-' + i).innerHTML = r.error ? `<span style="color:var(--red)">${esc(r.error)}</span>` :
    r.ok ? '<span style="color:var(--green);">✓ To\'g\'ri!</span>' : '<span style="color:var(--red);">✗ Noto\'g\'ri. Qayta urinib ko\'ring yoki javobni ko\'ring.</span>';
}
async function taskReveal(tid, id, i) {
  const r = await toolApi(toolById(tid), 'reveal', { id });
  $('task-fb-' + i).innerHTML = `<span style="color:var(--navy);">${r.error ? esc(r.error) : "To'g'ri javob: " + esc(r.answer)}</span>`;
}

/* --- kind: quiz --- */
let quizState = { tool: null, answers: [], n: 0 };
async function toolQuiz(t, box) {
  const d = await toolApi(t, 'list', {});
  if (d.error) { box.innerHTML = titleH2(t) + `<div class="err-box">${esc(d.error)}</div>`; return; }
  quizState = { tool: t, answers: Array(d.questions.length).fill(null), n: d.questions.length };
  box.innerHTML = titleH2(t) + d.questions.map((q, i) => `
    <div class="quiz-q"><h4>${i + 1}. ${esc(q.q)}</h4>
      ${q.opts.map((o, j) => `<button class="quiz-opt" id="qopt-${i}-${j}" onclick="quizAnswer(${i},${j})">${esc(o)}</button>`).join('')}
      <div id="qfb-${i}" style="margin-top:6px;font-size:12.5px;font-weight:bold;"></div></div>`).join('') +
    `<div style="text-align:center;"><button class="btn btn-gold" onclick="quizFinish()">Yakunlash</button></div><div id="quiz-final"></div>`;
}
async function quizAnswer(i, j) {
  if (quizState.answers[i] !== null) return;
  quizState.answers[i] = j;
  const r = await toolApi(quizState.tool, 'answer', { i });
  if (r.error) { $('qfb-' + i).innerHTML = `<span style="color:var(--red)">${esc(r.error)}</span>`; return; }
  $(`qopt-${i}-${j}`).classList.add(j === r.correct ? 'sel-correct' : 'sel-wrong');
  if (j !== r.correct) $(`qopt-${i}-${r.correct}`).classList.add('sel-correct');
  $('qfb-' + i).innerHTML = j === r.correct ? '<span style="color:var(--green);">✓ To\'g\'ri</span>' : '<span style="color:var(--red);">✗ Noto\'g\'ri</span>';
}
async function quizFinish() {
  const r = await toolApi(quizState.tool, 'finish', { answers: quizState.answers });
  $('quiz-final').innerHTML = r.error ? `<div class="err-box">${esc(r.error)}</div>` :
    `<div class="quiz-score">Natija: ${r.score} / ${r.total}<br>${r.pct}%</div>`;
}

/* --- kind: form (kalkulyator va shunga o'xshash yordamchilar) --- */
function renderSpans(a) {
  return (a || []).map(s => {
    if (typeof s === 'string') return esc(s);
    const c = s.cls ? ` class="${esc(s.cls)}"` : '';
    return s.sup ? `<sup>${esc(s.t)}</sup>` : (s.cls ? `<span${c}>${esc(s.t)}</span>` : esc(s.t));
  }).join('');
}
function renderCell(c) {
  if (c && c.bits) return `<div class="char-bit-row">${[...c.bits].map(b => `<span class="char-bit ${b === '1' ? 'one' : 'zero'}">${b}</span>`).join('')}</div>`;
  if (Array.isArray(c)) return renderSpans(c);
  if (c && typeof c === 'object') return c.cls || c.sup ? renderSpans([c]) : (c.b ? `<b>${esc(c.t)}</b>` : esc(c.t));
  return esc(c);
}
function renderTbl(tb, plain) {
  const cells = r => r.map(c => {
    const span = c && c.colspan ? ` colspan="${c.colspan}"` : '';
    const al = c && c.align === 'right' ? ' class="r"' : '';
    return `<td${span}${al}>${renderCell(c)}</td>`;
  }).join('');
  return `<div style="overflow-x:auto"><table class="calc-bits-table${plain ? ' plain' : ''}"><thead><tr>${tb.head.map(h => `<th>${esc(h)}</th>`).join('')}</tr></thead><tbody>${tb.rows.map(r => `<tr>${cells(r)}</tr>`).join('')}</tbody></table></div>`;
}
const copyBtn = (txt, style) => `<button class="copy-btn" style="${style || ''}" data-text="${esc(txt)}" onclick="copyText(this)">📋 Nusxa olish</button>`;
function renderBlocks(blocks) {
  return (blocks || []).map(b => {
    switch (b.k) {
      case 'error': return `<div class="calc-err err-box">${esc(b.t)}</div>`;
      case 'bar': return `<div class="calc-result-box"><span class="calc-res-label">${esc(b.from)}</span><span style="color:var(--navy);">${esc(b.input)}</span><span style="color:var(--slate);">→</span><span class="calc-res-label">${esc(b.to)}</span><span>${esc(b.output)}</span>${copyBtn(b.output, 'margin-left:auto;')}</div>`;
      case 'boxes': return `<div class="calc-all-row">${b.items.map(i => `<div class="calc-all-box"><small>${esc(i.label)}</small><b${b.small ? ' style="font-size:12px;word-break:break-all;"' : ''}>${esc(i.value)}</b></div>`).join('')}</div>`;
      case 'box': return `<div class="calc-result-box" style="flex-direction:column;align-items:stretch;gap:8px;"><div style="display:flex;justify-content:space-between;align-items:center;"><span class="calc-res-label">${esc(b.title)}</span>${copyBtn(b.value)}</div><div style="word-break:break-all;color:var(--navy);font-size:15px;line-height:1.6;user-select:all;background:#fff;padding:10px 14px;border-radius:6px;border:1px solid var(--line);">${esc(b.value)}</div></div>`;
      case 'heading': return `<div class="calc-steps-title"${b.mt ? ' style="margin-top:16px;"' : ''}>${esc(b.t)}</div>`;
      case 'step': return `<div class="calc-step-item"><div class="calc-step-num">${esc(b.num)}</div><div class="calc-step-body">${b.lines.map(l => `<div>${renderSpans(l)}</div>`).join('')}${b.table ? renderTbl(b.table, false) : ''}</div></div>`;
      case 'table': return `<div class="calc-steps-title" style="margin-top:18px;">${esc(b.title)}</div>${renderTbl(b, true)}`;
    }
    return '';
  }).join('');
}
function copyText(btn) {
  const txt = btn.dataset.text, orig = btn.innerText;
  const done = () => { btn.innerText = '✓ Nusxalandi!'; btn.style.background = 'var(--green)'; btn.style.color = '#fff'; setTimeout(() => { btn.innerText = orig; btn.style.background = ''; btn.style.color = ''; }, 1500); };
  if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(txt).then(done, () => { });
  else { const ta = document.createElement('textarea'); ta.value = txt; document.body.appendChild(ta); ta.select(); try { document.execCommand('copy'); done(); } catch (e) { } ta.remove(); }
}

const fid = (t, s, f) => `f-${t.id}-${s.id}-${f.id}`;
function toolForm(t, box) {
  const secs = t.sections || [];
  box.innerHTML = `<div class="calc-page-wrap"><div class="calc-head"><h2>${esc(t.heading || t.title)}</h2><p>${esc(t.intro || '')}</p></div><div class="calc-body">
    <div class="calc-tabs">${secs.map((s, i) => `<button id="f-tab-${t.id}-${s.id}" class="calc-tab-btn${i ? '' : ' active'}" onclick="formTab('${esc(t.id)}','${esc(s.id)}')">${esc(s.tab)}</button>`).join('')}</div>
    ${secs.map((s, i) => {
      const inline = s.fields.filter(f => f.type !== 'textarea'), areas = s.fields.filter(f => f.type === 'textarea');
      const fld = f => {
        if (f.type === 'arrow') return '<div class="calc-arrow-badge">&rarr;</div>';
        const id = fid(t, s, f), ev = s.auto ? `oninput="formAuto('${esc(t.id)}','${esc(s.id)}')" onchange="formAuto('${esc(t.id)}','${esc(s.id)}')"` : `oninput="formClear('${esc(t.id)}','${esc(s.id)}')" onchange="formClear('${esc(t.id)}','${esc(s.id)}')" onkeydown="if(event.key==='Enter')formRun('${esc(t.id)}','${esc(s.id)}')"`;
        let el;
        if (f.type === 'select') el = `<select id="${id}" ${ev}>${f.options.map(o => `<option value="${esc(o.value)}"${String(o.value) === String(f.default) ? ' selected' : ''}>${esc(o.label)}</option>`).join('')}</select>`;
        else if (f.type === 'textarea') el = `<textarea id="${id}" class="text-calc-box" placeholder="${esc(f.placeholder || '')}" ${ev}>${esc(f.default || '')}</textarea>`;
        else el = `<input type="text" id="${id}" value="${esc(f.default || '')}" placeholder="${esc(f.placeholder || '')}" autocomplete="off" ${ev}>`;
        return `<div class="calc-field"${f.wide ? ' style="min-width:240px;flex:1;"' : ''}><label>${esc(f.label)}</label>${el}</div>`;
      };
      return `<div id="f-sec-${t.id}-${s.id}" class="${i ? 'hidden' : ''}">
        <div class="calc-row">${inline.map(fld).join('')}<div class="calc-field"><label>&nbsp;</label><button class="btn btn-primary" onclick="formRun('${esc(t.id)}','${esc(s.id)}')" style="padding:9px 22px;font-size:14px;">${esc(s.button || '= Hisobla')}</button></div></div>
        ${areas.map(a => `<div style="margin-bottom:14px;">${fld(a)}</div>`).join('')}
        <div style="margin-bottom:14px;display:flex;gap:8px;flex-wrap:wrap;align-items:center;"><span style="font-size:11.5px;color:var(--slate);font-family:Arial,sans-serif;">Namunalar:</span>
          ${(s.examples || []).map((e, k) => `<button class="btn btn-sm" style="background:var(--ice);color:var(--navy);" onclick="formExample('${esc(t.id)}','${esc(s.id)}',${k})">${esc(e.label)}</button>`).join('')}</div>
        <div id="f-out-${t.id}-${s.id}"></div></div>`;
    }).join('')}
  </div></div>`;
  secs.filter(s => s.auto).forEach(s => formRun(t.id, s.id));
}
function formTab(tid, sid) {
  const t = toolById(tid);
  t.sections.forEach(s => {
    $(`f-sec-${tid}-${s.id}`).classList.toggle('hidden', s.id !== sid);
    $(`f-tab-${tid}-${s.id}`).classList.toggle('active', s.id === sid);
  });
}
const formVals = (t, s) => Object.fromEntries(s.fields.filter(f => f.id).map(f => [f.id, $(fid(t, s, f)).value]));
const formClear = (tid, sid) => { $(`f-out-${tid}-${sid}`).innerHTML = ''; };
let formTimers = {};
function formAuto(tid, sid) { clearTimeout(formTimers[tid + sid]); formTimers[tid + sid] = setTimeout(() => formRun(tid, sid), 200); }
async function formRun(tid, sid) {
  const t = toolById(tid), s = t.sections.find(x => x.id === sid);
  const r = await api(`/api/tool/${tid}`, { action: 'run', payload: { section: sid, vals: formVals(t, s) } });
  $(`f-out-${tid}-${sid}`).innerHTML = r.error ? `<div class="calc-err err-box">${esc(r.error)}</div>` : renderBlocks(r.blocks);
}
function formExample(tid, sid, k) {
  const t = toolById(tid), s = t.sections.find(x => x.id === sid);
  Object.entries(s.examples[k].vals).forEach(([f, v]) => { const el = $(`f-${tid}-${sid}-${f}`); if (el) el.value = v; });
  formRun(tid, sid);
}

init();
