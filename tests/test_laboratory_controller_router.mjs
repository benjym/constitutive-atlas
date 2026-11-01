import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createLaboratoryControllerRouter} from '../web/laboratory-controller-router.mjs';
test('switching clears all interfaces before activating only the target',()=>{
 const events=[];let shared='ordinary';
 const make=modelId=>({modelId,active:false,select(id){this.active=id===modelId;shared=this.active?modelId:'ordinary';events.push([modelId,id]);return this.active;},run(){return modelId;},showEquations(){return this.active;}});
 const a=make('a'),b=make('b'),r=createLaboratoryControllerRouter([a,b]);
 assert.equal(r.select('a'),true);assert.equal(shared,'a');assert.equal(r.run(),'a');assert.ok(r.active);
 events.length=0;assert.equal(r.select('a'),true);assert.deepEqual(events,[['a','a']]);
 events.length=0;assert.equal(r.select('b'),true);assert.deepEqual(events,[['a',null],['b',null],['b','b']]);assert.equal(shared,'b');assert.equal(a.active,false);assert.ok(b.active);assert.ok(r.showEquations());
 assert.equal(r.select('linear-elastic'),false);assert.equal(shared,'ordinary');assert.equal(r.active,false);assert.equal(r.showEquations(),false);assert.equal(r.run(),undefined);
 assert.equal(r.supports('a'),true);assert.equal(r.supports('linear-elastic'),false);
});
test('ambiguous model identities fail instead of selecting the wrong engine',()=>{
 assert.throws(()=>createLaboratoryControllerRouter([{modelId:'a'},{modelId:'a'}]),/Duplicate/);
 assert.throws(()=>createLaboratoryControllerRouter([{}]),/missing/);
});
