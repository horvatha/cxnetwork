# encoding: utf-8
from __future__ import division
from __future__ import print_function
from django.http import HttpResponse, HttpResponseNotFound
import itertools
import igraph
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from random import randint
import numpy as np

from cxnetwork import settings

def main(request):
    return HttpResponse("""<h1>Köszöntünk a hálózatok weboldalon</h1>
    <p> <a href="dobokocka/12/">Véletlen kockadobások a hálózat előállításához</a></p>
    <p> <a href="dobokocka/30">Egy 30 csúcsú véletlen hálózat és fokszámeloszlása ábrázolva</a></p>
    <p> <a href="dobokocka/900">Egy 900 csúcsszámú véletlen hálózat fokszámeloszlása</a></p>
    """)


def throws(num, dice_sides=6):
    cmb = itertools.combinations(range(1,num+1), 2)
    throws = {key: randint(1,dice_sides) for key in cmb}
    return throws

def dice(request, num=12, flags=None):
    """flags:
        W: without the throws
        G: plot graph
        D: degree distribution
        """
    good_values = set([5,6])
    num = int(num)
    if flags is None:
        if num < 15:
            flags = ""
        elif num < 35:
            flags = "WGD"
        elif num <= 1000:
            flags = "WD"
        else:
            return HttpResponse("Túl nagy szám, 1000-nél kisebb kell.")
    lines = [
        """<html>
<style>
td, tr {
  padding: 3px 20px;
  text-align: center;
}
.connected {
  color: red;
}
.unconnected {
  color: blue;
}
</style>
<body>
<h1>Véletlen hálózat generálása dobókockával</h1>
<p>Dobókockával kisorsoljuk, hogy húzzunk-e élt két csúcs között. Ha 5-öst vagy 6-ost dobunk, húzunk élt, különben nem.</p>""",
"""<p><b>Paraméterek:</b> A véletlen hálózatban <i>N</i>&nbsp;=&nbsp;{num} csúcs lesz, az élvalószínűség <i>p</i>&nbsp;=&nbsp;1/3.</p>""".format(num=num),
]
    dice_dict = throws(num=num)
    if "W" not in flags:
        lines.append("""<table>\n\t<tr><th>innen-ide</th><th>dobás értéke</th></tr>""")
        lines.extend(["<tr class={connected}>\n\t<td>{key[0]}-{key[1]}</td><td>{dice}</td>\n</tr>".format(
          dice=dice_dict[key], key=key, connected = "connected" if dice_dict[key] in good_values else "unconnected")
          for key in sorted(dice_dict)]
        )
    M = [dice_dict[key] in good_values for key in dice_dict].count(True)
    Mc = int(num*(num-1)/2)
    lines.append("""</table>
<p><b>A kapott hálózatban</b> a {Mc} lehetséges élből {M} ({p:4.2f}%) létezik.</p>
""".format(Mc=Mc, M=M, p=M/Mc*100))
    if "G" in flags or "D" in flags:
        edges = [key for key in dice_dict if dice_dict[key] in good_values]
        edges = [(i-1, j-1) for i, j in edges]
        net = igraph.Graph(num, edges=edges)
        assert M == net.ecount(), "The number of edges in the plotted network should agree with the 'diced' one."
    if "G" in flags:
        net.vs["label"] = range(1, num+1)
        degs = reversed(np.linspace(2*3.1415, 0,num=num,endpoint=0) - np.pi/2)
        lo = igraph.Layout([(np.cos(d), np.sin(d)) for d in degs])
        filename = "igraph.png"
        igraph.plot(net, "{0}igraph.png".format(settings.MEDIA_ROOT), layout=lo, vertex_color="lightblue",bbox=(500,500))
        fileurl = "{}{}".format(settings.MEDIA_URL, filename)
        lines.append('<p>A kapott hálózat:<br><img src="{0}"></p>'.format(fileurl))
    if "D" in flags:
        deg = net.degree()
        dd = [deg.count(k) for k in range(max(deg)+1)]
        p_k = [d/num for d in dd]
        plt.plot(dd, "x")
        plt.title(u"A hálózat fokszámeloszlása")
        plt.xlabel(u"fokszám (k)")
        plt.ylabel(u"hányad p(k)")
        filename = "degdist.png"
        plt.xlim([min(deg)-1, max(deg)+1])
        plt.ylim(ymin=0-max(dd)*.1, ymax = max(dd)*1.1)
        plt.savefig("{}{}".format(settings.MEDIA_ROOT, filename))
        plt.close()
        fileurl = "{}{}".format(settings.MEDIA_URL, filename)
        lines.append('<p>A fokszámeloszlás:<br><img src="{0}"></p>'.format(fileurl))
        lines.append("<table>\n<tr><th>fokszám</th><th>darab</th><th>hányad</th></tr>")
        lines.append("<tr><th><i>k</i></th><th><i>N<sub>k</sub></i></th><th><i>p(k)</i></th></tr>")
        for k, N_k in enumerate(dd):
            p_k = N_k/num
            lines.append("<tr><td>{k}</td><td>{N_k}</td><td>{p_k:.3f}</td></tr>".
                    format(k=k, N_k=N_k, p_k=p_k))
        lines.append('</table>')
    lines.append('</body>')
    return HttpResponse("\n".join(lines))
