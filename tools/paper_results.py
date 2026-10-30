"""Generate the manuscript's table and scientific figure from a benchmark report."""
import argparse
import json
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR',str(Path(__file__).resolve().parents[1]/'.cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--report',type=Path,default=ROOT/'artifacts/kfs-drained.json');args=parser.parse_args()
    report=json.loads(args.report.read_text());out=ROOT/'paper/article';(out/'images').mkdir(parents=True,exist_ok=True)
    table=[]
    for c in report['comparisons']:
        if not c['ok']:raise ValueError('paper table requires completed comparisons; report failures explicitly')
        label=c['experiment'].replace('KFS-','')
        if not label.isalnum():raise ValueError('unsafe table label')
        table.append(f"{label} & {c['q_metrics']['rmse']/1000:.2f} & {c['volumetric_metrics']['rmse']*100:.3f} " + chr(92)*2)
    (out/'results.tex').write_text('\n'.join(table)+'\n'+chr(92)+'bottomrule\n')
    fig,axes=plt.subplots(1,2,figsize=(9,3.5),layout='constrained');colors=['#b45d35','#376858','#5d789c']
    for color,index in zip(colors,[0,2,4]):
        c=report['comparisons'][index];raw=json.loads((ROOT/'data/normalized'/f"{c['experiment']}.json").read_text())
        measured=[r for r in raw['rows'] if r['axial_strain']<=.02];pred=c['simulation']['points']
        axes[0].plot([p['strain'][0]*100 for p in pred],[p['q_signed']/1000 for p in pred],color=color,label=c['experiment'].replace('KFS-',''))
        axes[0].scatter([r['axial_strain']*100 for r in measured],[r['q']/1000 for r in measured],s=6,color=color,alpha=.6)
        axes[1].plot([p['strain'][0]*100 for p in pred],[sum(p['strain'][:3])*100 for p in pred],color=color)
        axes[1].scatter([r['axial_strain']*100 for r in measured],[r['volumetric_strain']*100 for r in measured],s=6,color=color,alpha=.6)
    for ax in axes:
        ax.set_xlabel('Axial strain (%)');ax.grid(alpha=.2);ax.spines[['top','right']].set_visible(False);ax.set_xlim(0,2)
    axes[0].set_ylabel('Signed deviator stress (kPa)');axes[1].set_ylabel('Volumetric strain (%)');axes[0].legend(frameon=False)
    fig.savefig(out/'images/transfer.png',dpi=220);plt.close(fig)
    print(f'Generated manuscript figure and table in {out}')


if __name__=='__main__':main()
