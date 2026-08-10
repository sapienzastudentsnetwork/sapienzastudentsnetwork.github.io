(() => {
  'use strict';

  const VERSION = 1;
  const labels = {mc:'mc',ma:'ma',tmc:'tmc',ta:'ta',tc:'tc',optional:'Gruppo opzionale',aiml:'IA e Machine Learning',characterizing:'Caratterizzanti di completamento',related:'Affini di completamento',specialist:'Ambiti specialistici'};
  const makeId = (course) => `${course.code || 'custom'}:${course.name}`;

  class StudyPlanTool {
    constructor(root) {
      this.root = root;
      this.state = {version: VERSION, mode: root.dataset.mode || 'presenza', regulation: 'old', curriculum: 'methodological', selected: [], custom: [], drafts: {}};
      this.renderShell();
      this.bind();
      this.restoreLocal();
      this.render();
    }

    renderShell() {
      this.root.innerHTML = `<div class="sp-toolbar">
        <label class="sp-field">Modalità<select data-field="mode"><option value="presenza">In presenza</option><option value="teledidattica">Teledidattica</option></select></label>
        <label class="sp-field">Ordinamento<select data-field="regulation"><option value="new">Nuovo (3350x)</option><option value="old">Vecchio (29xyz)</option></select></label>
        <label class="sp-field" data-curriculum-field>Curriculum<select data-field="curriculum"><option value="methodological">Metodologico</option><option value="technological">Tecnologico</option><option value="individual">Individuale</option></select></label>
        <label class="sp-field">Cerca<input class="sp-search" type="search" placeholder="Nome o codice"></label>
      </div>
      <div class="sp-summary" aria-live="polite"></div><div class="sp-rules"></div><div class="sp-courses"></div>
      <h3>Aggiungi un insegnamento esterno</h3><form class="sp-custom"><label class="sp-field">Nome<input name="name" required maxlength="160"></label><label class="sp-field">CFU<input name="cfu" type="number" required min="1" max="30" step="1"></label><label class="sp-field">Codice (facoltativo)<input name="code" maxlength="30"></label><button type="submit">Aggiungi</button></form>
      <p class="sp-note">Gli insegnamenti esterni richiedono comunque la valutazione della Commissione. Il tool controlla i vincoli quantitativi, non l'inerenza o l'approvabilità del singolo insegnamento.</p>
      <div class="sp-plan"></div><div class="sp-actions"><button data-action="json">Esporta JSON</button><button data-action="import">Importa JSON</button><button data-action="png">Esporta immagine PNG</button><button data-action="reset">Azzera</button><input class="sp-hidden" data-import type="file" accept="application/json,.json"></div>`;
    }

    bind() {
      this.root.addEventListener('change', (event) => {
        const field = event.target.dataset.field;
        if (field) { if (field === 'mode' || field === 'regulation') { this.saveDraft(); this.state[field] = event.target.value; this.loadDraft(); } else { this.state[field] = event.target.value; } this.persist(); this.render(); }
      });
      this.root.querySelector('.sp-search').addEventListener('input', () => this.renderCourses());
      this.root.querySelector('.sp-custom').addEventListener('submit', (event) => { event.preventDefault(); const form = new FormData(event.currentTarget); const item = {name:String(form.get('name')).trim(),cfu:Number(form.get('cfu')),code:String(form.get('code')).trim(),external:true}; if (!item.name || !Number.isFinite(item.cfu)) return; item.id=makeId(item); this.state.custom.push(item); this.state.selected.push(item.id); event.currentTarget.reset(); this.persist(); this.render(); });
      this.root.addEventListener('click', (event) => { const button=event.target.closest('button'); if(!button) return; if(button.dataset.course) this.toggle(button.dataset.course); if(button.dataset.remove) this.removeCustom(button.dataset.remove); if(button.dataset.action) this.action(button.dataset.action); });
      this.root.querySelector('[data-import]').addEventListener('change', (event) => this.importFile(event.target.files[0]));
    }

    draftKey() { return `${this.state.mode}:${this.state.regulation}`; }
    saveDraft() { this.state.drafts ||= {}; this.state.drafts[this.draftKey()] = {selected: [...this.state.selected], custom: this.state.custom.map(item => ({...item}))}; }
    loadDraft() { const draft=this.state.drafts?.[this.draftKey()]; this.state.selected=Array.isArray(draft?.selected)?[...draft.selected]:[]; this.state.custom=Array.isArray(draft?.custom)?draft.custom.map(item=>({...item})):[]; }

    catalog() { return (window.STUDY_PLAN_CATALOG?.[this.state.mode]?.[this.state.regulation] || []).map(([name,code,cfu,semester,tags]) => ({name,code,cfu,semester,tags,external:false,id:`${code}:${name}`})); }
    allCourses() { return [...this.catalog(), ...this.state.custom]; }
    chosen() { const ids=new Set(this.state.selected); return this.allCourses().filter(course => ids.has(course.id)); }
    toggle(id) { this.state.selected = this.state.selected.includes(id) ? this.state.selected.filter(value => value !== id) : [...this.state.selected,id]; this.persist(); this.render(); }
    removeCustom(id) { this.state.custom=this.state.custom.filter(item=>item.id!==id); this.state.selected=this.state.selected.filter(value=>value!==id); this.persist(); this.render(); }

    validation() {
      const chosen=this.chosen(), total=chosen.reduce((sum,item)=>sum+item.cfu,0), externalRaw=chosen.filter(item=>item.external).reduce((sum,item)=>sum+item.cfu,0), internal=total-externalRaw;
      const rules=[{text:'30 CFU complessivi',ok:total===30},{text:'Massimo 15 CFU esterni selezionati',ok:externalRaw<=15},{text:'Massimo 12 CFU esterni riconoscibili',ok:externalRaw<=12,warning:externalRaw>12&&externalRaw<=15}];
      const sumTag=(tag)=>chosen.filter(item=>!item.external&&item.tags?.includes(tag)).reduce((sum,item)=>sum+item.cfu,0);
      if(this.state.mode==='presenza'&&this.state.regulation==='new'){rules.push({text:'Almeno 12 CFU dal Gruppo opzionale',ok:sumTag('optional')>=12},{text:'Almeno 6 CFU da IA e Machine Learning',ok:sumTag('aiml')>=6});}
      if(this.state.mode==='presenza'&&this.state.regulation==='old'){
        if(this.state.curriculum==='methodological') rules.push({text:'Almeno 12 CFU metodologici caratterizzanti (mc)',ok:sumTag('mc')>=12},{text:'Almeno 6 CFU metodologici affini (ma)',ok:sumTag('ma')>=6});
        if(this.state.curriculum==='technological') rules.push({text:'Almeno 6 CFU metodologici di completamento (tmc)',ok:sumTag('tmc')>=6},{text:'Almeno 6 CFU tecnologici affini (ta)',ok:sumTag('ta')>=6},{text:'Almeno 6 CFU tecnologici di completamento (tc)',ok:sumTag('tc')>=6});
        if(this.state.curriculum==='individual') rules.push({text:'Almeno 18 CFU interni nel percorso individuale',ok:internal>=18});
      }
      if(this.state.mode==='teledidattica'){
        const a=this.state.regulation==='old'?'characterizing':'related', b=this.state.regulation==='old'?'related':'specialist';
        rules.push({text:`Almeno 12 CFU: ${labels[a]}`,ok:sumTag(a)>=12},{text:`Almeno 6 CFU: ${labels[b]}`,ok:sumTag(b)>=6});
      }
      return {chosen,total,externalRaw,internal,rules,valid:rules.every(rule=>rule.ok||rule.warning)};
    }

    render() {
      this.root.querySelector('[data-field="mode"]').value=this.state.mode; this.root.querySelector('[data-field="regulation"]').value=this.state.regulation; this.root.querySelector('[data-field="curriculum"]').value=this.state.curriculum;
      this.root.querySelector('[data-curriculum-field]').classList.toggle('sp-hidden',!(this.state.mode==='presenza'&&this.state.regulation==='old'));
      const result=this.validation(); this.root.querySelector('.sp-summary').innerHTML=`<div class="sp-metric"><span>Totale</span><strong>${result.total}/30 CFU</strong></div><div class="sp-metric"><span>Interni</span><strong>${result.internal} CFU</strong></div><div class="sp-metric"><span>Esterni</span><strong>${result.externalRaw} CFU</strong></div><div class="sp-metric"><span>Esito quantitativo</span><strong class="${result.valid?'sp-ok':'sp-bad'}">${result.valid?'Conforme':'Da completare'}</strong></div>`;
      this.root.querySelector('.sp-rules').innerHTML=result.rules.map(rule=>`<div class="sp-rule ${rule.ok?'sp-ok':'sp-bad'}">${rule.ok?'✓':rule.warning?'⚠':'✗'} ${rule.text}${rule.warning?' (saranno riconosciuti 12 CFU)':''}</div>`).join('');
      this.renderCourses(); this.renderPlan();
    }

    renderCourses() { const query=this.root.querySelector('.sp-search').value.trim().toLowerCase(); const selected=new Set(this.state.selected); this.root.querySelector('.sp-courses').innerHTML=this.catalog().filter(c=>`${c.name} ${c.code}`.toLowerCase().includes(query)).map(c=>`<div class="sp-course"><div><strong>${this.escape(c.name)}</strong><small>${this.escape(c.code)} · ${c.cfu} CFU</small></div><span class="sp-semester">${c.semester}° sem.</span><span class="sp-tags">${c.tags.map(t=>labels[t]||t).join(', ')}</span><button type="button" data-course="${this.escape(c.id)}" data-selected="${selected.has(c.id)}">${selected.has(c.id)?'Rimuovi':'Aggiungi'}</button></div>`).join('') || '<p>Nessun insegnamento trovato.</p>'; }
    renderPlan() { const chosen=this.validation().chosen; this.root.querySelector('.sp-plan').innerHTML=`<h3>Il tuo percorso</h3>${chosen.length?`<table><thead><tr><th>Insegnamento</th><th>Codice</th><th>CFU</th><th>Tipo</th><th></th></tr></thead><tbody>${chosen.map(c=>`<tr><td>${this.escape(c.name)}</td><td>${this.escape(c.code||'—')}</td><td>${c.cfu}</td><td>${c.external?'Esterno':'Interno'}</td><td><button type="button" data-course="${this.escape(c.id)}">Rimuovi</button>${c.external?` <button type="button" data-remove="${this.escape(c.id)}">Elimina definitivamente</button>`:''}</td></tr>`).join('')}</tbody></table>`:'<p>Non hai ancora aggiunto insegnamenti.</p>'}`; }

    action(name) { if(name==='json') this.download('percorso-formativo.json',JSON.stringify({...this.state,exportedAt:new Date().toISOString()},null,2),'application/json'); if(name==='import') this.root.querySelector('[data-import]').click(); if(name==='png') this.exportPng(); if(name==='reset' && window.confirm('Vuoi davvero azzerare questo percorso formativo? Questa operazione rimuoverà le selezioni e gli insegnamenti esterni personalizzati dell’ordinamento corrente.')){this.state.selected=[];this.state.custom=[];this.saveDraft();this.persist();this.render();} }
    importFile(file) { if(!file)return; const reader=new FileReader(); reader.onload=()=>{try{const parsed=JSON.parse(reader.result); if(parsed.version!==VERSION||!['presenza','teledidattica'].includes(parsed.mode)||!Array.isArray(parsed.selected)||!Array.isArray(parsed.custom)) throw new Error('Formato non valido'); this.state={...this.state,...parsed}; this.persist(); this.render();}catch(error){alert(`Importazione non riuscita: ${error.message}`);}}; reader.readAsText(file); }
    exportPng() { const result=this.validation(), width=1200, line=38, height=180+result.chosen.length*line; const canvas=document.createElement('canvas'); canvas.width=width; canvas.height=height; const ctx=canvas.getContext('2d'); ctx.fillStyle='#fff';ctx.fillRect(0,0,width,height);ctx.fillStyle='#8b1d41';ctx.fillRect(0,0,width,72);ctx.fillStyle='#fff';ctx.font='bold 30px sans-serif';ctx.fillText('Percorso formativo',36,46);ctx.fillStyle='#222';ctx.font='18px sans-serif';ctx.fillText(`${this.state.mode==='presenza'?'In presenza':'Teledidattica'} · ${this.state.regulation==='new'?'dal 2025/26':'prima del 2025/26'} · ${result.total}/30 CFU`,36,108);ctx.font='16px sans-serif'; result.chosen.forEach((c,i)=>{const y=158+i*line;ctx.fillText(`${c.name} — ${c.code||'senza codice'} — ${c.cfu} CFU${c.external?' — esterno':''}`,36,y);}); const a=document.createElement('a');a.download='percorso-formativo.png';a.href=canvas.toDataURL('image/png');a.click(); }
    download(name,content,type) { const url=URL.createObjectURL(new Blob([content],{type})); const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000); }
    persist() { this.saveDraft(); localStorage.setItem(this.storageKey(),JSON.stringify(this.state)); }
    restoreLocal() { try { const saved=JSON.parse(localStorage.getItem(this.storageKey())); if(saved?.version===VERSION){this.state={...this.state,...saved,drafts:saved.drafts||{}}; if(!saved.drafts)this.saveDraft(); this.loadDraft();} } catch (_) { localStorage.removeItem(this.storageKey()); } }
    storageKey() { return `study-plan-tool:v${VERSION}:${this.root.id||'default'}`; }
    escape(value) { const node=document.createElement('span');node.textContent=String(value);return node.innerHTML; }
  }
  const boot=()=>document.querySelectorAll('[data-study-plan-tool]').forEach((root,index)=>{if(!root.id)root.id=`study-plan-tool-${index+1}`;if(!root.dataset.ready){root.dataset.ready='true';new StudyPlanTool(root);}});
  document.readyState==='loading'?document.addEventListener('DOMContentLoaded',boot):boot();
})();
