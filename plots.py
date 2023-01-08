import numpy as np
import plotly_express as px

basic_tick = np.arange(2, 10)
minor_ticks = np.concatenate((10*basic_tick[1:], 100*basic_tick, 1e3*basic_tick, 1e4*basic_tick), axis=0)


def get_plot(plot_type='absolute'):
    plot = px.line(labels={'x': 'frequency in Hz', 'y': ''}, log_x=True, range_x=[20, 20e3])
    plot.update_xaxes(
        showgrid=True, gridwidth=1, gridcolor='white',
        minor=dict(tickvals=minor_ticks, showgrid=True, gridwidth=1, gridcolor='#262626'),
        showline=True, mirror=True, linewidth=1, linecolor='white'
    )
    plot.update_yaxes(
        showgrid=True, gridwidth=1, gridcolor='white',
        zeroline=True, zerolinewidth=1, zerolinecolor='white',
        minor=dict(showgrid=True, gridwidth=1, gridcolor='#262626'),
        showline=True, mirror=True, linewidth=1, linecolor='white'
    )
    plot.update_layout(
        xaxis=dict(
            tickvals=[20, 100, 1e3, 10e3, 20e3],
            ticktext=['20', '100', '1k', '10k', '20k'],
            tickfont=dict(size=16),
            titlefont=dict(size=16),
            ticks="outside"
        ),
        yaxis=dict(
            tickfont=dict(size=16),
            ticks="outside"
        ),
        showlegend=False,
        margin=dict(pad=0)
    )
    if plot_type == 'absolute':
        plot.update_yaxes(
            range=[0, 18]
        )
        plot.update_layout(
            yaxis=dict(
                tickvals=[0, 3, 6, 9, 12, 15, 18],
                ticktext=['0dB', '3dB', '6dB', '9dB','12dB', '15dB', '18dB']
            )
        )
    if plot_type == 'relative':
        plot.update_yaxes(
            range=[-6, 6]
        )
        plot.update_layout(
            yaxis=dict(
                tickvals=[-6, -3, 0, 3, 6],
                ticktext=['-6dB', '-3dB', '0dB', '3dB', '6dB']
            )
        )

    return plot
