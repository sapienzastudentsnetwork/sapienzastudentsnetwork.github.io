(() => {
  'use strict';

  const VERSION = 1;
  const labels = {mc:'mc',ma:'ma',tmc:'tmc',ta:'ta',tc:'tc',optional:'Gruppo opzionale',aiml:'IA e Machine Learning',characterizing:'Caratterizzanti di completamento',related:'Affini di completamento',specialist:'Ambiti specialistici'};
  const makeId = (course) => `${course.code || 'custom'}:${course.name}`;
  const makeCustomId = () => `custom:${Date.now().toString(36)}:${Math.random().toString(36).slice(2,10)}`;

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
        <label class="sp-field">Ordinamento<select data-field="regulation"><option value="new">Nuovo (${this.state.mode==='presenza'?'33503':'33504'})</option><option value="old">Vecchio (${this.state.mode==='presenza'?'29923':'29400'})</option></select></label>
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
      this.root.querySelector('.sp-custom').addEventListener('submit', (event) => { event.preventDefault(); const form = new FormData(event.currentTarget); const item = {name:String(form.get('name')).trim(),cfu:Number(form.get('cfu')),code:String(form.get('code')).trim(),external:true}; if (!item.name || !Number.isFinite(item.cfu)) return; item.id=makeCustomId(); this.state.custom.push(item); this.state.selected.push(item.id); event.currentTarget.reset(); this.persist(); this.render(); });
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

    completionRequirements() {
      if(this.state.mode==='presenza'&&this.state.regulation==='new') return {optional:12,aiml:6};
      if(this.state.mode==='presenza'&&this.state.regulation==='old') {
        if(this.state.curriculum==='methodological') return {mc:12,ma:6};
        if(this.state.curriculum==='technological') return {tmc:6,ta:6,tc:6};
        return {internal:18};
      }
      if(this.state.mode==='teledidattica') return this.state.regulation==='old'?{characterizing:12,related:6}:{related:12,specialist:6};
      return {};
    }

    completionRule(requirements) {
      const descriptions={
        optional:'Gruppo opzionale',
        aiml:'IA e Machine Learning',
        mc:'metodologici caratterizzanti (mc)',
        ma:'metodologici affini (ma)',
        tmc:'tecnologici caratterizzanti (tmc)',
        ta:'tecnologici affini (ta)',
        tc:'tecnologici di completamento (tc)',
        internal:'interni',
        characterizing:'caratterizzanti',
        related:'affini',
        specialist:'ambiti specialistici'
      };
      const parts=Object.entries(requirements).map(([tag,cfu])=>`${cfu} CFU ${descriptions[tag]||tag}`);
      return `Completamento: ${parts.join(' + ')}`;
    }

    allocateCompletion(courses, requirements) {
      const tags=Object.keys(requirements);
      const entries=courses.filter(course=>!course.external&&(tags.includes('internal')||course.tags?.some(tag=>requirements[tag])));
      const search=(index,totals,used)=>{
        if(tags.every(tag=>(totals[tag]||0)>=requirements[tag])) return used;
        if(index>=entries.length) return null;
        const skipped=search(index+1,totals,used);
        if(skipped) return skipped;
        const course=entries[index];
        const eligible=tags.includes('internal')?['internal']:course.tags.filter(tag=>requirements[tag]);
        for(const tag of eligible){
          const found=search(index+1,{...totals,[tag]:(totals[tag]||0)+course.cfu},new Set([...used,course.id]));
          if(found) return found;
        }
        return null;
      };
      return search(0,{},new Set());
    }

    validation() {
      const chosen=this.chosen();
      const requirements=this.completionRequirements();
      const completionIds=this.allocateCompletion(chosen,requirements);
      const completionValid=Boolean(completionIds);
      const completion=completionValid?chosen.filter(item=>completionIds.has(item.id)):[];
      const choice=completionValid?chosen.filter(item=>!completionIds.has(item.id)):chosen;
      const completionCfu=completion.reduce((sum,item)=>sum+item.cfu,0);
      const choiceCfu=choice.reduce((sum,item)=>sum+item.cfu,0);
      const insertedTotal=chosen.reduce((sum,item)=>sum+item.cfu,0);
      const individual=this.state.mode==='presenza'&&this.state.regulation==='old'&&this.state.curriculum==='individual';
      const completionText=individual?'Completamento: almeno 18 CFU interni':this.completionRule(requirements);
      const completionDetail=individual
        ? (completionValid?`${completionCfu} CFU interni assegnati al completamento.`:`Seleziona almeno 18 CFU tra gli insegnamenti interni del corso.`)
        : (completionValid?`${completionCfu} CFU assegnati al completamento. Gli insegnamenti presenti in più gruppi sono conteggiati una sola volta e assegnati a un solo gruppo.`:`Seleziona insegnamenti interni che coprano tutti i gruppi indicati. Alcuni insegnamenti appartengono a più gruppi, ma nel calcolo ciascun insegnamento viene assegnato a un solo gruppo.`);
      const rules=[
        {text:completionText,detail:completionDetail,ok:completionValid},
        {text:'Insegnamenti a scelta: da 12 a 15 CFU',detail:completionValid?`${choiceCfu} CFU a scelta. Possono provenire dal corso di laurea o da altri corsi di laurea triennale; gli insegnamenti interni non usati per il completamento rientrano qui.`:'Il conteggio definitivo dei CFU a scelta sarà disponibile quando risultano soddisfatti i vincoli di completamento. Gli insegnamenti a scelta possono provenire anche da altri corsi di laurea triennale.',ok:completionValid&&choiceCfu>=12&&choiceCfu<=15},
      ];
      const valid=completionValid&&choiceCfu>=12&&choiceCfu<=15;
      return {chosen,completion,choice,completionCfu,choiceCfu,insertedTotal,rules,valid};
    }

    render() {
      this.root.querySelector('[data-field="regulation"]').value=this.state.regulation; this.root.querySelector('[data-field="curriculum"]').value=this.state.curriculum;
      this.root.querySelector('[data-curriculum-field]').classList.toggle('sp-hidden',!(this.state.mode==='presenza'&&this.state.regulation==='old'));
      const result=this.validation(); this.root.querySelector('.sp-summary').innerHTML=`<div class="sp-metric"><span>CFU inseriti</span><strong>${result.insertedTotal} CFU</strong></div><div class="sp-metric"><span>Di completamento</span><strong>${result.completionCfu} CFU</strong></div><div class="sp-metric"><span>A scelta</span><strong>${result.choiceCfu} CFU</strong></div><div class="sp-metric sp-outcome"><span>Vincoli quantitativi</span><strong class="sp-status ${result.valid?'sp-ok':'sp-bad'}">${result.valid?'Rispettati':'Da completare'}</strong></div>`;
      this.root.querySelector('.sp-rules').innerHTML=result.rules.map(rule=>`<div class="sp-rule ${rule.ok?'sp-ok':rule.warning?'sp-warning':'sp-bad'}"><span class="sp-rule-icon" aria-hidden="true">${rule.ok?'✓':rule.warning?'!':'✗'}</span><span class="sp-rule-copy"><strong>${this.escape(rule.text)}</strong>${rule.detail?`<small>${this.escape(rule.detail)}</small>`:''}</span></div>`).join('');
      this.renderCourses(); this.renderPlan();
    }

    renderCourses() {
      const query=this.root.querySelector('.sp-search').value.trim().toLowerCase();
      const selected=new Set(this.state.selected);
      const courses=this.allCourses().filter(course=>`${course.name} ${course.code||''}`.toLowerCase().includes(query));
      this.root.querySelector('.sp-courses').innerHTML=courses.map(course=>{
        const details=course.external
          ? `${this.escape(course.code||'senza codice')} · ${course.cfu} CFU · insegnamento esterno personalizzato`
          : `${this.escape(course.code)} · ${course.cfu} CFU`;
        const semester=course.external?'':`<span class="sp-semester">${course.semester}° sem.</span>`;
        const hideGroups=this.state.mode==='presenza'&&this.state.regulation==='old'&&this.state.curriculum==='individual';
        const groups=course.external
          ? '<span class="sp-tags">A scelta · altro corso triennale</span>'
          : hideGroups?'':`<span class="sp-tags">${course.tags.map(tag=>labels[tag]||tag).join(', ')}</span>`;
        return `<div class="sp-course"><div><strong>${this.escape(course.name)}</strong><small>${details}</small></div>${semester}${groups}<button type="button" data-course="${this.escape(course.id)}" data-selected="${selected.has(course.id)}">${selected.has(course.id)?'Rimuovi':'Aggiungi'}</button></div>`;
      }).join('') || '<p>Nessun insegnamento trovato.</p>';
    }
    renderPlan() { const chosen=this.validation().chosen; this.root.querySelector('.sp-plan').innerHTML=`<h3>Il tuo percorso</h3>${chosen.length?`<table><thead><tr><th>Insegnamento</th><th>Codice</th><th>CFU</th><th>Tipo</th><th></th></tr></thead><tbody>${chosen.map(c=>`<tr><td>${this.escape(c.name)}</td><td>${this.escape(c.code||'—')}</td><td>${c.cfu}</td><td>${c.external?'Esterno':'Interno'}</td><td><button type="button" data-course="${this.escape(c.id)}">Rimuovi</button>${c.external?` <button type="button" data-remove="${this.escape(c.id)}">Elimina definitivamente</button>`:''}</td></tr>`).join('')}</tbody></table>`:'<p>Non hai ancora aggiunto insegnamenti.</p>'}`; }

    action(name) { if(name==='json') this.download('percorso-formativo.json',JSON.stringify({...this.state,exportedAt:new Date().toISOString()},null,2),'application/json'); if(name==='import') this.root.querySelector('[data-import]').click(); if(name==='png') this.exportPng(); if(name==='reset' && window.confirm('Vuoi davvero azzerare questo percorso formativo? Questa operazione rimuoverà le selezioni e gli insegnamenti esterni personalizzati dell’ordinamento corrente.')){this.state.selected=[];this.state.custom=[];this.saveDraft();this.persist();this.render();} }
    importFile(file) { if(!file)return; const reader=new FileReader(); reader.onload=()=>{try{const parsed=JSON.parse(reader.result); if(parsed.version!==VERSION||!['presenza','teledidattica'].includes(parsed.mode)||!Array.isArray(parsed.selected)||!Array.isArray(parsed.custom)) throw new Error('Formato non valido'); this.state={...this.state,...parsed,mode:this.root.dataset.mode||this.state.mode}; this.persist(); this.render();}catch(error){alert(`Importazione non riuscita: ${error.message}`);}}; reader.readAsText(file); }
    exportPng() {
      const result=this.validation();
      const mode=this.state.mode==='presenza'?'In presenza':'Teledidattica';
      const courseCode=this.state.regulation==='old'
        ? (this.state.mode==='presenza'?'29923':'29400')
        : (this.state.mode==='presenza'?'33503':'33504');
      const curriculum=this.state.mode==='presenza'&&this.state.regulation==='old'
        ? ` · ${this.root.querySelector('[data-field="curriculum"] option:checked').textContent}`:'';
      const heading=`${mode} · ${this.state.regulation==='new'?'Nuovo ordinamento':'Vecchio ordinamento'} (${courseCode})${curriculum}`;
      const summary=[
        `CFU inseriti: ${result.insertedTotal}`,
        `Di completamento: ${result.completionCfu}`,
        `A scelta: ${result.choiceCfu}`,
        `Vincoli quantitativi: ${result.valid?'Rispettati':'Da completare'}`
      ];
      const courseRows=result.chosen.map(c=>`${c.name} — ${c.code||'senza codice'} — ${c.cfu} CFU — ${result.completion.some(item=>item.id===c.id)?'di completamento':'a scelta'}`);
      const padding=36, lineHeight=25;
      const measure=document.createElement('canvas').getContext('2d');
      measure.font='16px sans-serif';
      const longest=Math.max(...[heading,...summary,...courseRows,...result.rules.flatMap(rule=>[rule.text,rule.detail])].map(text=>measure.measureText(text||'').width));
      const width=Math.max(680,Math.min(760,Math.ceil(longest*.58+96)));
      const contentWidth=width-padding*2;
      const wrap=(ctx,text,maxWidth)=>{
        const words=String(text||'').split(/\s+/), lines=[]; let line='';
        words.forEach(word=>{const test=line?`${line} ${word}`:word;if(ctx.measureText(test).width>maxWidth&&line){lines.push(line);line=word;}else line=test;});
        if(line) lines.push(line); return lines;
      };
      const sizing=document.createElement('canvas').getContext('2d');
      const wrappedHeading=(()=>{sizing.font='18px sans-serif';return wrap(sizing,heading,contentWidth);})();
      const summaryColumnWidth=(contentWidth-24)/2;
      const wrappedSummary=summary.map(text=>{sizing.font='bold 17px sans-serif';return wrap(sizing,text,summaryColumnWidth);});
      const wrappedRules=result.rules.map(rule=>{
        sizing.font='bold 16px sans-serif';const title=wrap(sizing,`${rule.ok?'✓':'✗'} ${rule.text}`,contentWidth);
        sizing.font='16px sans-serif';const detail=wrap(sizing,rule.detail,contentWidth-70);
        return {rule,title,detail};
      });
      const wrappedCourses=courseRows.map(text=>{sizing.font='16px sans-serif';return wrap(sizing,text,contentWidth);});
      const headingHeight=wrappedHeading.length*lineHeight;
      const summaryRowHeights=[0,1].map(row=>Math.max(wrappedSummary[row*2]?.length||0,wrappedSummary[row*2+1]?.length||0)*lineHeight);
      const rulesHeight=wrappedRules.reduce((total,item)=>total+(item.title.length+item.detail.length)*lineHeight+12,0);
      const coursesHeight=Math.max(1,wrappedCourses.reduce((total,lines)=>total+lines.length,0))*lineHeight;
      const height=72+30+headingHeight+24+summaryRowHeights.reduce((a,b)=>a+b,0)+42+rulesHeight+38+coursesHeight+44;
      const canvas=document.createElement('canvas');canvas.width=width;canvas.height=height;
      const ctx=canvas.getContext('2d');
      ctx.fillStyle='#fff';ctx.fillRect(0,0,width,height);
      ctx.fillStyle='#8b1d41';ctx.fillRect(0,0,width,72);
      ctx.fillStyle='#fff';ctx.font='bold 30px sans-serif';ctx.fillText('Percorso formativo',padding,46);
      let y=102;ctx.fillStyle='#222';ctx.font='18px sans-serif';
      wrappedHeading.forEach(line=>{ctx.fillText(line,padding,y);y+=lineHeight;});
      y+=12;ctx.font='bold 17px sans-serif';
      for(let row=0;row<2;row++){
        const left=wrappedSummary[row*2]||[],right=wrappedSummary[row*2+1]||[];
        const rowTop=y;
        left.forEach((line,index)=>ctx.fillText(line,padding,rowTop+index*lineHeight));
        right.forEach((line,index)=>ctx.fillText(line,padding+summaryColumnWidth+24,rowTop+index*lineHeight));
        y+=summaryRowHeights[row];
      }
      y+=22;ctx.font='bold 19px sans-serif';ctx.fillText('Requisiti',padding,y);
      wrappedRules.forEach(({rule,title,detail})=>{
        y+=lineHeight;ctx.fillStyle=rule.ok?'#16733f':'#b42338';ctx.font='bold 16px sans-serif';
        title.forEach(line=>{ctx.fillText(line,padding,y);y+=lineHeight;});
        ctx.fillStyle='#444';ctx.font='16px sans-serif';
        detail.forEach(line=>{ctx.fillText(line,padding+30,y);y+=lineHeight;});
        y+=12;
      });
      y+=14;ctx.fillStyle='#222';ctx.font='bold 19px sans-serif';ctx.fillText('Insegnamenti',padding,y);
      ctx.font='16px sans-serif';ctx.fillStyle='#222';
      if(!wrappedCourses.length){y+=lineHeight;ctx.fillText('Nessun insegnamento inserito.',padding,y);}else wrappedCourses.forEach(lines=>lines.forEach(line=>{y+=lineHeight;ctx.fillText(line,padding,y);}));
      const a=document.createElement('a');a.download='percorso-formativo.png';a.href=canvas.toDataURL('image/png');a.click();
    }

    download(name,content,type) { const url=URL.createObjectURL(new Blob([content],{type})); const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000); }
    persist() { this.saveDraft(); localStorage.setItem(this.storageKey(),JSON.stringify(this.state)); }
    restoreLocal() { try { const saved=JSON.parse(localStorage.getItem(this.storageKey())); if(saved?.version===VERSION){this.state={...this.state,...saved,mode:this.root.dataset.mode||this.state.mode,drafts:saved.drafts||{}}; if(!saved.drafts)this.saveDraft(); this.loadDraft();} } catch (_) { localStorage.removeItem(this.storageKey()); } }
    storageKey() { return `study-plan-tool:v${VERSION}:${this.root.id||'default'}`; }
    escape(value) { const node=document.createElement('span');node.textContent=String(value);return node.innerHTML; }
  }
  const boot=()=>document.querySelectorAll('[data-study-plan-tool]').forEach((root,index)=>{if(!root.id)root.id=`study-plan-tool-${index+1}`;if(!root.dataset.ready){root.dataset.ready='true';new StudyPlanTool(root);}});
  document.readyState==='loading'?document.addEventListener('DOMContentLoaded',boot):boot();
})();
