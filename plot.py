import matplotlib.pyplot as plt
from matplotlib.widgets import LassoSelector
from matplotlib.path import Path
import matplotlib.dates as mdates

import numpy as np
from functools import partial

class LegendPickablePlot():
    fig = None
    ax = None
    lined = {}

    def __init__ (self):
        self.fig = plt.figure(figsize=(14, 8))
        self.ax = self.fig.add_subplot()

    def get_plot_props (self):
        return self.fig, self.ax

    def get_lined (self):
        return self.lined

    def define_legend_items (self, legend, plot_lines, plot_markers=None):
        if not plot_markers:
            for legline, origline in zip(legend.get_lines(), plot_lines):
                legline.set_picker(True)  # Enable picking on the legend line.
                self.lined[legline] = origline
        else:
            for legline, origline, origmark in zip(legend.get_lines(), plot_lines, plot_markers):
                legline.set_picker(True)  # Enable picking on the legend line.
                self.lined[legline] = (origline, origmark)

    @staticmethod
    def change_legend_alpha (legend):
        for legline in legend.get_lines():
            legline.set_alpha(1)

    @staticmethod
    def on_pick(event, fig, lined):
        # On the pick event, find the original line corresponding to the legend
        # proxy line, and toggle its visibility.
        legline = event.artist
        try:
            origline, origmark = lined[legline]
            visible = not origline.get_visible()
            origline.set_visible(visible)
            origmark.set_visible(visible)
        except TypeError:
            origline = lined[legline]
            visible = not origline.get_visible()
            origline.set_visible(visible)
        # Change the alpha on the line in the legend so we can see what lines
        # have been toggled.
        legline.set_alpha(1.0 if visible else 0.2)
        fig.canvas.draw()


class PickPointsPlot:
    @staticmethod
    def plot(x, y):
        class SelectFromCollection:
            def __init__(self, ax, collection, alpha_other=0.3):
                self.canvas = ax.figure.canvas
                self.collection = collection
                self.alpha_other = alpha_other

                self.xys = collection.get_offsets()
                self.Npts = len(self.xys)

                # Ensure that we have separate colors for each object
                self.fc = collection.get_facecolors()
                if len(self.fc) == 0:
                    raise ValueError('Collection must have a facecolor')
                elif len(self.fc) == 1:
                    self.fc = np.tile(self.fc, (self.Npts, 1))

                self.lasso = LassoSelector(ax, onselect=self.onselect)
                self.ind = []

            def onselect(self, verts):
                path = Path(verts)
                self.ind = np.nonzero(path.contains_points(self.xys))[0]
                self.fc[:, -1] = self.alpha_other
                self.fc[self.ind, -1] = 1
                self.collection.set_facecolors(self.fc)
                self.canvas.draw_idle()

            def disconnect(self):
                self.lasso.disconnect_events()
                self.fc[:, -1] = 1
                self.collection.set_facecolors(self.fc)
                self.canvas.draw_idle()
        
        fig, ax = plt.subplots(figsize=(15,7))

        pts = ax.scatter(x, y, s=4000/len(y))

        selector = SelectFromCollection(ax, pts)

        selected_pts = []

        def accept(event, selected_pts):
            if event.key == "enter":
                print("Selected points:")
                print(selector.xys[selector.ind])
                for point in selector.xys[selector.ind].data:
                    selected_pts.append(point)
                fig.canvas.draw()
            
        

        fig.canvas.mpl_connect("key_press_event", partial(accept, selected_pts=selected_pts))
        ax.set_title("Press enter to accept selected points.")
        
        plt.show(block=True)

        return selected_pts
        

def plot_timeseries(xy_pais: dict):
    _, ax_perim = plt.subplots(figsize=(15,7))
    ax_rf = ax_perim.twinx()
    
    plot1 = ax_perim.plot(xy_pais['perimeter'][0], xy_pais['perimeter'][1], color='darkorange', label='Perímetro')
    plot2 = ax_rf.plot(xy_pais['rf'][0], xy_pais['rf'][1], color='darkblue', label='RF')
    plot3 = ax_rf.plot(xy_pais['resíduo'][0], xy_pais['resíduo'][1], color='green', label='Resíduo')

    ax_perim.set_ylabel(u"\u03bcm")
    ax_rf.set_ylabel('Hz')

    ax_perim.set_ylim(-800, 800)
    ax_rf.set_ylim(-800, 800)
    
    plots = plot1 + plot2 + plot3
    # plots = plot1
    labs = [p.get_label() for p in plots]
    ax_perim.legend(plots, labs)


    ax_perim.yaxis.labelpad = 10
    locator = mdates.AutoDateLocator(minticks=5, maxticks=10)
    formatter = mdates.ConciseDateFormatter(locator)
    ax_perim.xaxis.set_major_locator(locator)
    ax_perim.xaxis.set_major_formatter(formatter)
    ax_perim.tick_params(axis='both')
    ax_perim.grid()
    plt.show()

def plot_rf(xy_pais: dict):
    fig, ax = plt.subplots(figsize=(15,7))
    
    ax.plot(xy_pais['temp'][0], xy_pais['temp'][1], color='darkorange', label='Efeito da temperatura + maré')
    ax.plot(xy_pais['poço'][0], xy_pais['poço'][1], color='green', label='Efeito do poço')
    ax.plot(xy_pais['rf'][0], xy_pais['rf'][1], color='darkblue', label='RF')

    ax.set_ylabel('Hz')

    ax.legend()


    ax.yaxis.labelpad = 10
    locator = mdates.AutoDateLocator(minticks=5, maxticks=10)
    formatter = mdates.ConciseDateFormatter(locator)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    ax.tick_params(axis='both')
    ax.grid()
    fig.tight_layout()
    plt.show()

def plot_fft(fft_data: list, labels: list):
    fig, ax = plt.subplots()
    for i, data in enumerate(fft_data):
        color = 'darkorange' if labels[i] == 'Perímetro' else 'darkblue'
        ax.plot(data[0], data[1], label=labels[i], c=color)
    ax.legend()
    plt.show()