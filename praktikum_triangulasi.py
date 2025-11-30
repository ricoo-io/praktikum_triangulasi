import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay, Voronoi, voronoi_plot_2d
from matplotlib.widgets import Button
from shapely.geometry import Polygon
from shapely.ops import triangulate

#Set up variabel
points = []
voronoi = None
tri = None
current_view = "none"  

fig, ax = plt.subplots(figsize=(10, 8))
plt.subplots_adjust(bottom=0.22, top=0.88)
desc_text = fig.text(0.5, 0.94, "Klik area canvas untuk menambah titik.", ha='center', fontsize=11, color='blue')

#Setup canvas dengan skala 10 x 10
def setup_canvas():
    ax.set_xlim(0, 10); ax.set_ylim(0, 10)
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.set_aspect('equal')

#Fungsi untuk membersihkan canvas
def clear_canvas():
    ax.clear(); setup_canvas()

#Fungsi perhitungan untuk digram voronoi dan triangulasi
def calculate_voronoi_triangulation():
    global voronoi, tri
    if len(points) < 3:
        voronoi = tri = None
        return False
    pts = np.array(points)
    try:
        tri = Delaunay(pts)
        voronoi = Voronoi(pts)
        return True
    except Exception:
        voronoi = tri = None
        return False

#Fungsi untuk menggambar titik
def draw_points():
    if not points: return
    pts = np.array(points)
    ax.plot(pts[:,0], pts[:,1], 'ro', zorder=5)
    for i,p in enumerate(pts): ax.text(p[0], p[1]+0.12, str(i+1), ha='center', fontsize=9)

#Fungsi untuk mengkonversi digram voronoi ke poligon dan menggambar poligon
def voronoi_to_poligon(voronoi):
    polys = []
    for region_idx in voronoi.point_region:
        region = voronoi.regions[region_idx]
        if not region or -1 in region: continue
        coords = [tuple(voronoi.vertices[i]) for i in region]
        try:
            poly = Polygon(coords)
            if poly.is_valid and poly.area > 1e-9:
                polys.append(poly)
        except Exception:
            continue
    return polys

#Fungsi untuk merender tampilan canvas berdasarkan tombol yang diclick
def render_view(view):
    clear_canvas()
    draw_points()
    ok = calculate_voronoi_triangulation()
    if not ok:
        desc_text.set_text("Butuh minimal 3 titik valid untuk Voronoi/Delaunay.")
        plt.draw(); return
    ax.set_title(view)
    if view == "Voronoi Diagram (Thiessen Polygons)":
        x0, x1 = ax.get_xlim()
        y0, y1 = ax.get_ylim()
        voronoi_plot_2d(voronoi, ax=ax, show_vertices=False, line_colors='blue', line_width=1.5, point_size=0)
        ax.set_xlim(x0, x1)
        ax.set_ylim(y0, y1)
        
    elif view == "Thiessen Polygon":
        polys = voronoi_to_poligon(voronoi)
        for poly in polys:
            x, y = poly.exterior.xy
            ax.plot(x, y, color='blue', linewidth=1.5, zorder=3)
    elif view == "Monoton Polygon":
        polys = voronoi_to_poligon(voronoi)
        for poly in polys:
            tris = triangulate(poly)
            for t in tris:
                tx,ty = t.exterior.xy
                ax.plot(tx, ty, color='purple', linewidth=1)
                ax.fill(tx, ty, alpha=0.25, color='purple')
    plt.draw()

#Fungsi untuk menambah titik secara realtime berdasarkan click mouse
def onclick_add(event):
    if event.inaxes != ax: return
    if event.xdata is None or event.ydata is None: return
    points.append([event.xdata, event.ydata])
    clear_canvas(); draw_points()
    desc_text.set_text(f"{len(points)} titik (klik untuk tambah).")
    plt.draw()

#Deklarasi fungsi untuk masing-masing tombol
def btn_voronoi(event):
    global current_view
    current_view = "Voronoi Diagram (Thiessen Polygons)"; render_view(current_view)

def btn_thiessen(event):
    global current_view
    current_view = "Thiessen Polygon"; render_view(current_view)

def btn_monoton(event):
    global current_view
    current_view = "Monoton Polygon"; render_view(current_view)

def btn_reset(event):
    points.clear()
    clear_canvas()
    plt.draw()
    desc_text.set_text(f"{len(points)} titik (Reset).")

#Atur posisi tombol berdasarkan layout window
CENTER_X = 0.5; BTN_W = 0.20; BTN_H = 0.07; GAP = 0.02
total_w = 4*BTN_W + 3*GAP
start_x = CENTER_X - total_w/2

ax_b1 = plt.axes([start_x, 0.05, BTN_W, BTN_H])
ax_b2 = plt.axes([start_x + (BTN_W+GAP), 0.05, BTN_W, BTN_H])
ax_b3 = plt.axes([start_x + 2*(BTN_W+GAP), 0.05, BTN_W, BTN_H])
ax_b4 = plt.axes([start_x + 3*(BTN_W+GAP), 0.05, BTN_W, BTN_H])

#Deklarasi tombol dan hubungkan dengan posisi ax yg ditentukan sebelumnya
button_reset = Button(ax_b1, 'Reset')
button_voronoi = Button(ax_b2, 'Voronoi Diagram')
button_thiessen = Button(ax_b3, 'Thiessen Polygon')
button_monoton = Button(ax_b4, 'Monoton Polygon')

#Hubungkan tombol dengan fungsinya
button_reset.on_clicked(btn_reset)
button_voronoi.on_clicked(btn_voronoi)
button_thiessen.on_clicked(btn_thiessen)
button_monoton.on_clicked(btn_monoton)

fig.canvas.mpl_connect('button_press_event', onclick_add)
setup_canvas(); draw_points()
plt.show()
