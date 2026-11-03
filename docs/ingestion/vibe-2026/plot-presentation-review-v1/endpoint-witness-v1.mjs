// Pure source presentation witness; no DOM, material or compiled module.
import {formatTickLabels} from '../../../../web/plot-labels.mjs';
const values=Array.from({length:5},(_,i)=>1+i*Number.EPSILON);
const labels=formatTickLabels(values),rightTickX=454,viewBoxWidth=480,glyphEstimate=7;
const estimatedRight=rightTickX+labels.at(-1).length*glyphEstimate/2;
console.log(JSON.stringify({source_freeze:'bbcabb646e109cfedd4dd479a58209590bdf7050000ae8282b73cceb4db5c8bc',values,labels,rightTickX,viewBoxWidth,glyphEstimate,estimatedRight,clippedByEstimate:estimatedRight>viewBoxWidth,compiled_calls:0},null,2));
