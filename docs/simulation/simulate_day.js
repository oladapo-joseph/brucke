// A simulated learner: answers mostly right, makes realistic mistakes on purpose, narrates each step.
const { chromium } = require('playwright');
const SP = process.argv[2] || __dirname, BASE = process.env.BASE || "http://localhost:8000";
const log = (...a) => console.log(...a);
let shotN = 0;
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1280, height: 800 }, recordVideo: { dir: SP + '/video', size: { width: 1280, height: 800 } } });
  // Fake microphone: the "learner" says whatever window.__say holds.
  await ctx.addInitScript(() => {
    class FakeSR { start() { setTimeout(() => { const t = window.__say ?? ''; const r = [{ transcript: t }]; r.isFinal = true;
        this.onresult?.({ resultIndex: 0, results: [r] }); this.onend?.(); }, 1600); } stop() {} }
    for (const k of ['SpeechRecognition', 'webkitSpeechRecognition']) Object.defineProperty(window, k, { value: FakeSR, configurable: true, writable: true });
  });
  const p = await ctx.newPage();
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  const shot = async (name, caption) => { shotN++; const f = `${String(shotN).padStart(2, '0')}-${name}.png`; await p.screenshot({ path: `${SP}/shots/${f}` }); log(`   📸 ${f}  ${caption || ''}`); };
  const item = async (id) => (await p.request.get(`${BASE}/api/item/${encodeURIComponent(id)}`)).json();
  const cont = async () => { await p.click('.p-foot .inner > .btn.big:last-child'); await p.waitForTimeout(700); };
  const fb = async () => { await p.waitForSelector('.fb', { timeout: 8000 }); await p.waitForTimeout(900);
    return p.evaluate(() => { const f = document.querySelector('.fb'); return f.querySelector('.head').innerText.split('\n')[0] + ' | ' + [...f.querySelectorAll('.ans,.cat,.small')].map(x => x.innerText).join(' · ').slice(0, 170); }); };

  // mistakes the learner will make: key → how
  const plan = { mistakes: new Set(), seen: {} };
  async function play(label, mistakeFn, maxSteps = 60, shotsFor = []) {
    const shotTaken = {};
    for (let k = 0; k < maxSteps; k++) {
      await p.waitForTimeout(500);
      if (await p.locator('.done-screen').count()) { await p.waitForTimeout(1500); await shot(label + '-done', 'session summary'); await cont(); return; }
      const st = await p.evaluate(() => { const n = document.querySelector('.p-stage .enter'); return n ? { item: n.dataset.item, type: n.dataset.type } : null; });
      if (!st) continue;
      const it = st.item ? await item(st.item) : null;
      const wrong = mistakeFn(st, it);
      const tag = `${st.type}${it ? ' · ' + it.text : ''}`;
      const takeShot = shotsFor.includes(st.type) && !shotTaken[st.type];
      if (st.type === 'grammar' || st.type === 'teach') {
        log(`  ▸ ${st.type === 'grammar' ? 'Grammar idea' : 'Teach card'}: ${it ? it.text + ' = ' + it.en : await p.locator('.p-prompt').innerText()}`);
        if (takeShot) { shotTaken[st.type] = 1; await p.waitForTimeout(600); await shot(`${label}-${st.type}`); }
        await p.waitForTimeout(900); await cont(); continue;
      }
      if (takeShot) { await p.waitForTimeout(500); await shot(`${label}-${st.type}-q`); }
      // answer
      if (['listen_choose', 'read_choose', 'listen_spell'].includes(st.type)) {
        const target = st.type === 'listen_spell' ? it.text : it.en;
        const opts = p.locator('.opt'); const n = await opts.count(); let idx = 0;
        for (let i = 0; i < n; i++) { const t = (await opts.nth(i).innerText()).replace(/^\d\n?/, '').trim(); if ((t === target) !== wrong) { idx = i; break; } }
        await p.waitForTimeout(700); await opts.nth(idx).click();
      } else if (st.type === 'gender') {
        const art = it.text.split(' ')[0].toLowerCase();
        const g = p.locator('.gopt'); const n = await g.count(); let idx = 0;
        for (let i = 0; i < n; i++) { const t = (await g.nth(i).innerText()).trim(); if ((t === art) !== wrong) { idx = i; break; } }
        await p.waitForTimeout(800); await g.nth(idx).click();
      } else if (st.type === 'speak' || st.type === 'speak_translate') {
        const say = wrong ? (typeof wrong === 'string' ? wrong : it.text.split(' ').slice(0, -1).join(' ')) : it.text;
        await p.evaluate((s) => { window.__say = s; }, say);
        await p.waitForTimeout(600); await p.click('.mic'); await p.waitForTimeout(700);
        if (takeShot) await shot(`${label}-speak-listening`, 'mic live');
      } else if (st.type === 'dictation' || st.type === 'translate') {
        const ans = wrong ? (typeof wrong === 'string' ? wrong : it.text.replace(/^(der|die|das|le|la) /i, '')) : it.text;
        await p.locator('.answer-input').pressSequentially(ans, { delay: 45 }); await p.waitForTimeout(400); await cont(); // Check
      } else if (st.type === 'build') {
        const words = it.tags.filter(t => t.pos !== 'punct').map(t => t.t);
        const order = wrong ? [...words.slice(1, 2), words[0], ...words.slice(2)] : words;
        for (const w of order) { await p.locator('.bank .tile:not(.ghost)', { hasText: new RegExp(`^${w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}$`) }).first().click(); await p.waitForTimeout(250); }
        await p.waitForTimeout(400); await cont();
      } else { log('  ? unhandled', st.type); await cont(); continue; }
      const result = await fb();
      log(`  ${wrong ? '✗' : '✓'} ${tag}  →  ${result}`);
      if (takeShot) { shotTaken[st.type] = 1; await shot(`${label}-${st.type}-feedback`); }
      await cont();
    }
  }

  // ---------------------------------------------------------------- DAY 1
  log('\n══ DAY 1 · Week 1 · Saturday ══');
  await p.goto(BASE + '/#/today'); await p.waitForTimeout(1500); await shot('today-fresh', 'first open');

  log('\n── Lesson 1: Sounds & Letters · part 1 (German) ──');
  await p.click('text=Continue lesson'); await p.waitForTimeout(900);
  let n = 0;
  await play('L1', (st, it) => {
    if (st.type === 'listen_spell' && it.text === 'müde') return true;          // mishears ü
    if (st.type === 'speak' && it.text === 'schön') return 'schon';              // drops the umlaut when speaking
    return false;
  }, 80, ['grammar', 'teach', 'listen_spell', 'speak']);

  log('\n── Lesson 2: Things & their gender · part 1 (skipping ahead to show gender colours) ──');
  await p.goto(BASE + '/#/unit/de-03'); await p.waitForTimeout(1200); await shot('unit-de03', 'unit page');
  await p.locator('.part').nth(0).locator('button').click(); await p.waitForTimeout(900);
  await play('L2', (st, it) => {
    if (st.type === 'gender' && ['der Tisch', 'der Stuhl'].includes(it.text) && !(plan.seen[it.text] = (plan.seen[it.text] || 0) + 1, plan.seen[it.text] > 1)) return true; // first try wrong
    if (st.type === 'listen_choose' && it.text === 'der Apfel') return true;
    return false;
  }, 80, ['teach', 'gender', 'listen_choose']);

  log('\n── Lesson 3: Things & their gender · Sentences 1 ──');
  await p.goto(BASE + '/#/unit/de-03'); await p.waitForTimeout(900);
  await p.locator('.part').nth(4).locator('button').click(); await p.waitForTimeout(900);
  let builds = 0;
  await play('L3', (st, it) => {
    if (st.type === 'build' && builds++ === 0) return true;                       // word-order slip
    if (st.type === 'speak' && /Lampe/.test(it.text)) return true;                 // swallows the last word
    return false;
  }, 80, ['build', 'speak']);

  log('\n── Insights after Day 1 ──');
  await p.goto(BASE + '/#/insights'); await p.waitForTimeout(1600); await shot('insights-day1', 'patterns found');
  await p.evaluate(() => window.scrollTo(0, 900)); await p.waitForTimeout(700); await shot('insights-day1-gaps');

  log('\n── Daily mix (adaptive: notice the targeted drills) ──');
  await p.goto(BASE + '/#/practice'); await p.waitForTimeout(900);
  const sess = p.waitForResponse(r => r.url().includes('/api/session'));
  await p.click('text=Start mix');
  const sj = await (await sess).json();
  log('  Mix composition:', sj.exercises.map(e => `${e.type}${e.why?.startsWith('focus') ? '[' + e.why.slice(6) + ']' : e.why === 'retry' ? '' : ''}`).join(', '));
  log('  Focus categories chosen by the coach:', sj.focus_categories.join(', ') || 'none');
  let typed = 0;
  await play('MIX', (st, it) => (st.type === 'translate' && typed++ === 0) ? true : false, 60, ['gender', 'translate', 'build', 'read_choose']);

  await p.goto(BASE + '/#/today'); await p.waitForTimeout(1600); await shot('today-end', 'end of day 1');
  await p.evaluate(() => window.scrollTo(0, 2000)); await p.waitForTimeout(600); await shot('today-end-coach');
  log('\nJS errors:', errs.length ? errs : 'none');
  await ctx.close(); await b.close();
})();
