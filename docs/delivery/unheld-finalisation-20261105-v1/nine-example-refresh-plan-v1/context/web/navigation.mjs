// Navigation remains available while the numerical laboratories initialize.
import {catalogueRoute} from './catalogue.mjs';
const titles={home:'Constitutive Atlas',laboratory:'Model testing',ensemble:'Ensemble explorer',catalogue:'Model catalogue',methods:'Methods & evidence'};
function navigate(){
 const {page}=catalogueRoute(location.hash);
 document.querySelectorAll('.page').forEach(el=>el.hidden=el.id!==page);
 document.querySelectorAll('.rail nav a').forEach(el=>{
  const active=el.hash==='#'+page;el.classList.toggle('active',active);
  if(active)el.setAttribute('aria-current','page');else el.removeAttribute('aria-current');
 });
 document.body.dataset.page=page;
 document.title=page==='home'?titles.home:titles[page]+' · Constitutive Atlas';
 if(location.hash==='#explore-atlas')document.getElementById('explore-atlas').scrollIntoView();
 if(['','#home','#laboratory','#ensemble','#catalogue','#methods'].includes(location.hash))window.scrollTo(0,0);
}
window.addEventListener('hashchange',navigate);
navigate();
