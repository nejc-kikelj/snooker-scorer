import sys,json
from py_mini_racer import MiniRacer
h=open(__import__('os').path.join(__import__('os').path.dirname(__file__),'..','index.html'),encoding='utf8').read()
js=h.split('<script>')[1].split('</script>')[0]
STUB=r"""
var els={},handlers={};
function el(id){return els[id]||(els[id]={id:id,innerHTML:'',textContent:'',value:'',focus(){},setAttribute(){},removeAttribute(){}})}
var document={getElementById:el,activeElement:null,documentElement:{setAttribute(){},removeAttribute(){}},addEventListener(t,f){handlers[t]=f}};
var localStorage={_d:{},getItem(k){return this._d[k]||null},setItem(k,v){this._d[k]=v}};
var timers=[];var clearTimeout=function(){},setTimeout=function(f,ms){timers.push(f);return timers.length};
var claude={use:async()=>null};
"""
HELP=r"""
var errs=[];
function click(act,v){try{handlers.click({target:{closest:()=>({dataset:{act:act,v:v}})}})}catch(e){errs.push(act+': '+e.message+' '+e.stack)}}
function change(ck,checked){try{handlers.change({target:{dataset:{ck:ck},checked:checked}})}catch(e){errs.push('change '+ck+': '+e.message)}}
function strip(h){return h.replace(/<[^>]+>/g,' ').replace(/\s+/g,' ')}
function buttons(){
  const html=els.view.innerHTML+els.layer.innerHTML;
  // if layer has a sheet, only layer buttons are reachable
  const src=els.layer.innerHTML.includes('class="sheet')?els.layer.innerHTML:html;
  const out=[];const re=/<(button|div|input)\b([^>]*)>/g;let m;
  while((m=re.exec(src))){const at=m[2];const a=/data-act="([^"]*)"/.exec(at);const ck=/data-ck="([^"]*)"/.exec(at);
    const dis=/\sdisabled(\s|$|=)/.test(at);
    if(dis)continue;
    if(a){const v=/data-v="([^"]*)"/.exec(at);out.push({act:a[1],v:v?v[1]:undefined})}
    else if(ck){out.push({ck:ck[1],checked:/\schecked/.test(at)})}}
  return out}
"""
PATCH=[]
def new(patch=True):
    j=js
    if patch:
        for a,b in PATCH:
            assert a in j; j=j.replace(a,b)
    c=MiniRacer();c.eval(STUB);c.eval(j);c.eval(HELP);return c
