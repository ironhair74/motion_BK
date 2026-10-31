const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1280,height:900}});
await p.goto("file://"+require("path").join(__dirname,"index.html"),{waitUntil:'networkidle'});
await p.addStyleTag({content:`*{animation:none!important;transition:none!important}
.reveal{opacity:1!important;transform:none!important}
.card,.iso-chart,.hbars,table.tbl,.callout,.tile,.flow,ol.timeline li,.iso-stack{break-inside:avoid}
h3.sub,.sec-head{break-after:avoid}
.section{break-before:page;border:0;padding-top:20px}
.hero{-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{-webkit-print-color-adjust:exact;print-color-adjust:exact}
.hero{min-height:1760px;display:flex;flex-direction:column;justify-content:center}
.hero h1 em{background:none!important;color:#f2c14e!important;-webkit-text-fill-color:#f2c14e}
.toc{max-width:1180px;margin:0 auto;padding:0 20px 40px;width:100%;box-sizing:border-box;color:#dbe3ff}
.toc h4{font-size:20px;color:#fff;margin:0 0 14px}
.toc ol{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:1fr 1fr;gap:12px}
.toc li{background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.15);border-radius:12px;padding:14px 18px;font-size:16px}
.toc li b{color:#9fc1ff;margin-right:10px}`});
await p.evaluate(()=>{const t=document.createElement('div');t.className='toc';t.innerHTML='<h4>목차</h4><ol>'+[...document.querySelectorAll('section.section')].map(s=>'<li><b>'+s.querySelector('.sec-no').textContent+'</b>'+s.querySelector('h2').textContent+'</li>').join('')+'</ol>';document.querySelector('.hero').appendChild(t)});
await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(500);
await p.pdf({path:require("path").join(__dirname,"snu-business-guide.pdf"),width:'1280px',height:'1810px',printBackground:true,margin:{top:'24px',bottom:'24px',left:'0',right:'0'}});
await b.close()})();
