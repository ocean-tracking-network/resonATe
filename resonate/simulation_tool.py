from __future__ import division
import pandas as pd
import numpy as np
import math
import sys
import plotly.offline as py
import plotly.graph_objs as go
from shapely.geometry import Point, Polygon


def transmit_along_path(path=None, vel=0.5, delay_rng=[60,180], burst_dir=5.0):

    """
    Simulate tag signal transmission along a pre-defined path (x, y coords)
   based on constant movement velocity, transmitter delay range, and duration
   of signal.

    :param path: A two-column data frame with at least two rows and columns
    x and y with coordinates that define path.

    :param vel: A numeric scalar with movement velocity along track; assumed
    constant.

    :param delay_rng:delayRng A 2-element numeric vector with minimum and maximum delay
   (time in seconds from end of one coded burst to beginning of next).

    :param burst_dir:burstDur  A numeric scalar with duration (in seconds) of each coded
    burst (i.e., pulse train).

    :return: A three-column data frame containing:

    * trns_id {Unique signal transmission ID]
    * recv_id {Unique receiver ID}
    * et {elapsed time to start of each transmission}

    """

    if len(np.setdiff1d(["x", "y"], path.columns)) > 0:
        sys.exit('Error: argument \'path\' must contain the columns x and y')

    path['cumdistm'] = np.insert(np.cumsum(np.sqrt(np.diff(path.x.values)**2 + np.diff(path.x.values)**2)),0, 0, axis=0)
    path['etime'] = path['cumdistm']/vel
    ntrns = int(path['etime'].max()/(delay_rng[0]+burst_dir))
    ints = np.random.uniform(delay_rng[0]+burst_dir, delay_rng[1]+burst_dir,ntrns)
    ints[0] = np.random.uniform(0,ints[0],1)

    etime = np.cumsum(ints)
    etime = etime[etime <= path['etime'].max()]

    x = np.interp(etime,path['etime'].values,path['x'])
    y = np.interp(etime, path['etime'].values, path['y'])
    trns = pd.DataFrame({'x':x, 'y':y,'etime':etime}, columns =['x','y','etime'])

    return trns


def receiver_line_det_sim(rng_fun, vel=1, delay_rng=[120, 360], burst_dur=5.0, rec_spc=[1000], max_dist=2000,
                          outer_lim=[0, 0], nsim=1000, show_plot=False, ipython_display=False):
    """
        Estimate, by simulation, the probability of detecting an acoustic-tagged
        fish on a receiver line, given constant fish velocity (ground speed),
        receiver spacing, number of receivers, and detection range curve.

        :param rng_fun A function that defines detection range curve; must accept a
        numeric vector of distances and return a numeric vector of detection
        probabilities at each distance.

        :param vel A numeric scalar with fish velocity in meters per second.

        :param delay_rng A 2-element numeric vector with minimum and maximum delay
        (time in seconds from end of one coded burst to beginning of next)

        :param burst_dur A numeric scalar with duration (in seconds) of each coded
        burst (i.e., pulse train).

        :param rec_spc A numeric vector with distances (in meters) between receivers.
        The length of vector is N-1, where N is number of receivers. One receiver
        is simulated when recSpc = NA (default).

        :param max_dist A numeric scalar with maximum distance between tagged fish
        and any receiver during simulation (i.e., sets spatial boundaries)

        :param outer_lim A two-element numeric vector with space (in meters) in which
        simulated fish are allowed to pass to left (first element) and right (second element) of the receiver line.

        :param nsim Integer scalar with the number of crossings (fish) to simulate

        :param show_plot A logical scalar. Should a plot be drawn showing receivers
        and fish paths?


        :return:  The proportion of simulated fish that were detected more
        than once on any single receiver.

        """

    if not callable(rng_fun):
        sys.exit('Error: argument \'rngFun\' must be a function')

    if any(elem is None for elem in rec_spc):
        rec_spc = 0

    x_lim = [0, np.sum(rec_spc) + sum(outer_lim)]
    rec_loc = [outer_lim[0]]
    rec_loc.extend(outer_lim[0] + np.cumsum(rec_spc))
    y_lim = [-max_dist, max_dist]

    n_trns = np.floor((np.diff(y_lim) / vel) / delay_rng[0])

    delay = np.random.uniform(delay_rng[0], delay_rng[1], (nsim, int(n_trns))) + burst_dur

    trans = np.cumsum(delay, axis=1)
    trans = trans - np.random.uniform(trans[:, int(math.floor(n_trns / 2) - 1)], trans[:, int(math.floor(n_trns / 2))],
                                      (nsim, int(n_trns)))

    fsh_x_holder_list = np.random.uniform(x_lim[0], x_lim[1], nsim)
    fsh_x = np.ndarray(shape=(nsim, int(n_trns)))
    for j in range(nsim):
        fsh_x[j, :] = fsh_x_holder_list[j]
    fsh_y = trans * vel

    if show_plot:
        data = []
        for i in range(len(fsh_x)):
            trace = go.Scatter(
                x=fsh_x[i],
                y=fsh_y[i],
                line=dict(
                    color=('grey'),
                ),
                mode='lines+markers',
                showlegend=False
            )
            data.append(trace)

        legendEntry1 = go.Scatter(
            x=[0],
            y=[0],
            line=dict(
                color=('grey'),
            ),
            mode='lines',
            name='Sim. fish path'
        )
        data.append(legendEntry1)
        legendEntry2 = go.Scatter(
            x=[0],
            y=[0],
            line=dict(
                color=('grey'),
            ),
            mode='markers',
            name='tag transmit'
        )
        data.append(legendEntry2)
        trace2 = go.Scatter(

            x=rec_loc,
            y=np.zeros(len(rec_loc)),
            marker={'color': 'red', 'size': "20"},
            mode='markers',
            name='Receiver'
        )
        data.append(trace2)
        layout = dict(
            xaxis=dict(title='Distance (in meters) along receiver line', range=x_lim),
            yaxis=dict(title='Distance (in meters) along fish path', range=y_lim, automargin=True),
        )
        fig = dict(data=data, layout=layout)

        py.plot(fig)

    succ = [None] * len(rec_loc)
    det_p = [None] * len(rec_loc)
    dist_m = [None] * len(rec_loc)
    n_dets = np.full((nsim, len(rec_loc)), None)

    for i in range(len(rec_loc)):
        dist_m[i] = np.sqrt((fsh_x - rec_loc[i]) ** 2 + fsh_y ** 2)
        det_p[i] = rng_fun(dist_m[i])
        succ[i] = np.random.binomial(1, det_p[i], (nsim, int(n_trns)))
        n_dets[:, i] = np.sum(succ[i], axis=1)

    max_dets = np.max(n_dets, axis=1)
    det_probs = np.mean(max_dets > 1)

    return det_probs


def calc_collision_prob(delay_rng=[60, 180], burst_dur=5.0, max_tags=50, n_trans=10000):

    """
    Estimate (by simulation) probability of collision for co-located telemetry
    transmitters with pulse-period-modulation type encoding

    :param delay_rng A 2-element list with minimum and maximum delay
    (time in seconds from end of one coded burst to beginning of next).

    :param burst_dur A numeric scalar with duration (in seconds) of each coded
    burst (i.e., pulse train).

    :param max_tags A numeric scalar with maximum number of co-located
    transmitters (within detection range at same time).

    :param n_trans A numeric scalar with the number of transmissions to simulate
    for each co-located transmitter.

    :return:  A data frame containing summary statistics:
    """

    ping_hist = [None] * max_tags
    collide = [[]] * max_tags

    det_probs = pd.DataFrame(None, index=np.arange(max_tags), columns=['nTags', 'min', 'q1', 'med', 'q3', 'max', 'mean'])

    for i in range(max_tags):

        ping_start = np.cumsum(np.random.uniform(delay_rng[0], delay_rng[1], n_trans) + burst_dur)
        ping_hist[i] = np.sort(np.concatenate((ping_start, ping_start + burst_dur)))

        if i == 0:
            det_probs.iloc[0] = 1
        else:
            for j in range(i):

                ping_ints = np.searchsorted(ping_hist[j], ping_hist[i])
                collisions = ping_ints / 2.0 != np.floor(ping_ints / 2.0)
                collide[j] = np.unique(np.append(collide[j], np.ceil(ping_ints[collisions] / 2.0)))
                collide[i] = np.unique(np.append(collide[i], np.ceil((np.where(collisions)[0]+1) / 2.0)))

            det_prob_k = [1 - (len(collide[x]) / float(n_trans)) for x in range(i + 1)]

            fivenum = [i+1, np.min(det_prob_k), np.percentile(det_prob_k, 25, interpolation='midpoint'),
                     np.median(det_prob_k),
                     np.percentile(det_prob_k, 75, interpolation='midpoint'),
                     np.max(det_prob_k), np.mean(det_prob_k)]

            det_probs.at[i] = fivenum

    nom_delay = np.median(delay_rng)

    exp_dets_per_tag_per_hr = (3600 / (nom_delay + burst_dur))
    det_probs['exp_dets_per_hr'] = np.round([i*exp_dets_per_tag_per_hr for i in range(1, max_tags+1)], 1)
    det_probs['tot_dets_per_hr'] = np.round([det_probs.iloc[i]['mean'] * det_probs.iloc[i]['exp_dets_per_hr'] for i in range(max_tags)])
    det_probs['eff_delay'] = np.round([nom_delay * (1 / det_probs.iloc[i]['mean']) for i in range(max_tags)])
    det_probs['dets_per_tag_per_hr'] = np.round([det_probs.iloc[i - 1]['tot_dets_per_hr'] / i for i in range(1, max_tags + 1)])

    return det_probs


def dectect_transmissions(trns_loc=None, rec_loc=None, det_rng_fun=None):

    """
        Simulates detection of transmitter signals in a receiver network based on
        detection range curve (detection probability as a function of distance),
        location of transmitter, and location of receivers.

        :param trns_loc A three-column data frame with locations (numeric columns
        named 'x' and 'y') and timestamps (numeric or POSIXct column named 'et')
        where signals were transmitted.

        :param rec_loc A two-column data frame with receiver locations (numeric
        columns named 'x' and 'y').

        :param det_rng_fun A function that defines detection range curve;
        must accept a numeric vector of distances and return a numeric vector of
        detection probabilities at each distance.

         :return: dectection transmissions dataframe with the following columns

        * trns_id {Unique signal transmission ID]
        * recv_id {Unique receiver ID}
        * recv_x {Receiver x coordinate}
        * recv_y {Receiver y coordinate}
        * trns_x {Transmitter x coordinate}
        * trns_y {Transmitter y coordinate}
        * etime {Elapsed time}

    """

    if len(np.setdiff1d(["x","y","et"],trns_loc.columns)) > 0:
        sys.exit('Error: argument \'trns_loc\' must contain the columns x, y, and et')

    if len(np.setdiff1d(["x","y"],rec_loc.columns)) > 0:
        sys.exit('Error: argument \'rec_loc\' must contain the columns x and y')

    trns_id_list = []
    recv_id_list = []
    recv_x_list = []
    recv_y_list = []
    trns_x_list = []
    trns_y_list = []
    etime_list = []

    for i, row in rec_loc.iterrows():
        progress(i, rec_loc.shape[0])
        dist_m_g = np.sqrt((trns_loc.x - rec_loc.x[i])**2 + (trns_loc.y - rec_loc.y[i])**2)
        det_p_g = det_rng_fun(dist_m_g)
        succ_g= np.random.binomial(1, det_p_g, det_p_g.shape[0])

        if 1 in succ_g:
            trns_id = np.where(succ_g)[0]
            recv_id = np.full((len(trns_id), 1), i)
            recv_x = np.full((len(trns_id), 1), rec_loc.x[i])
            recv_y = np.full((len(trns_id), 1), rec_loc.y[i])
            trns_x = trns_loc.x.values[trns_id]
            trns_y = trns_loc.y.values[trns_id]
            etime = trns_loc.et.values[trns_id]

            trns_id_list = np.append(trns_id_list, trns_id)
            recv_id_list = np.append(recv_id_list, recv_id)
            recv_x_list = np.append(recv_x_list, recv_x)
            recv_y_list = np.append(recv_y_list, recv_y)
            trns_x_list = np.append(trns_x_list, trns_x)
            trns_y_list = np.append(trns_y_list, trns_y)
            etime_list = np.append(etime_list, etime)

    dtc = pd.DataFrame({'trns_id': trns_id_list, 'recv_id': recv_id_list, 'recv_x': recv_x_list, 'recv_y': recv_y_list,
                        'trns_x':trns_x_list, 'trns_y': trns_y_list, 'etime':etime_list},
                       columns=['trns_id','recv_id','recv_x','recv_y','trns_x','trns_y','etime'])
    progress(rec_loc.shape[0], rec_loc.shape[0])
    dtc = dtc.sort_values('etime')
    return dtc



def crw_in_polygon(polyg=Polygon([(0, 0), (0, 2000), (1000, 2000), (1000, 500), (4000, 500), (0, 400)]),
                   theta=[0, 10], step_len=100,
                   init_pos=[None, None], init_heading=None, nsteps=30):
    """
     Uses crw to simulate a random walk as series of equal-length steps
     with turning angles drawn from a normal distribution inside a polygon.

    :param polyg: A polygon defined as data frame with columns x and y.

    :param theta: A 2-element numeric vector with turn angle parameters
    (theta[1] = mean; theta[2] = sd) from normal distribution.

    :param step_len: A numeric scalar with total distance moved in each step.

    :param init_pos: A 2-element numeric vector with nital position (initPos[1]=x,
    initPos[2]=y).

    :param init_heading: A numeric scalar with initial heading in degrees.

    :param nsteps: A numeric scalar with number of steps to simulate.

    :return: A two-column data frame containing:
    * x {x coordinates]
    * y {y coordinates}

    """

    if any(elem is None for elem in init_pos):
        in_poly = False
        while not in_poly:
            bound_values = polyg.bounds
            init = Point(np.random.uniform(bound_values[0], bound_values[2], 1),
                         np.random.uniform(bound_values[1], bound_values[3], 1))
            in_poly = init.within(polyg)

    if not all(v is None for v in init_pos):
        init = init_pos
        if not Point(init_pos[0], init_pos[1]).intersects(polyg):
            sys.exit('init_pos is outside polygon boundary.')

    if init_heading is None:
        init_heading = np.random.uniform(0, 360, 1)

    window_size = 1000

    loop_number = int(math.floor(nsteps/window_size))

    remainder = nsteps % window_size

    path_fwd = pd.DataFrame({'x': [None for i in range(nsteps+1)], 'y':[None for i in range(nsteps+1)]}, columns=['x', 'y'])
    path_fwd.iloc[0] = init

    rows_i = [0]

    nwin = loop_number+(remainder > 0)

    for i in range(nwin):
        init = path_fwd.iloc[0].values

        if i > 1:
            init_heading = vector_heading(path_fwd.x.iloc[max(rows_i)], path_fwd.y.iloc[max(rows_i)])

        if i+1 == nwin and remainder > 0:
            window_size = remainder

        rows_i = max(rows_i) + np.arange(1, window_size+1)

        test = crw(theta=theta, step_len=step_len, init_pos=init, init_heading=init_heading, nsteps=window_size)

        path_fwd.iloc[rows_i,] = test.values
        in_poly = Polygon(path_fwd.values).within(polyg)
        print in_poly

        while in_poly  == False:
            outside = None

            for i in range(len(path_fwd.values)):
                if not Point(path_fwd.iloc[i].values).within(polyg):
                    outside = i
                    break

            def constrain_theta_to_polygon(x, y, slen, polyg, theta):
                heading_deg = vector_heading(x, y)
                heading_deg2 = [(heading_deg + i) % 360 for i in range(-180, 181)]
                heading_rad = np.asarray(heading_deg2) * (3.141593/180)
                xlen = np.sin(heading_rad)*slen
                ylen = np.cos(heading_rad)*slen

                bar = pd.DataFrame({'x':x[1]+xlen, "y":y[1]+ylen, 'theta':[i for i in range(-180, 181)]})
                points = [1 for i in range(len(bar))]

                for i in range(len(points)):
                    if not Point(bar.x.iloc[i], bar.y.iloc[i]).within(polyg):
                        points[i] = 0

                if points.count(1) == 0:
                    sys.exit("Path stuck at boundary.")

                chance = (1/points.count(1))
                prob = [i*chance for i in points]

                theta2 = np.random.choice(bar.theta, 1, p=prob)
                return theta2

            print(outside)

            if outside is not None:
                theta2 = constrain_theta_to_polygon([path_fwd.x.iloc[outside-2], path_fwd.x.iloc[outside-1]],
                                        [path_fwd.y.iloc[outside-2], path_fwd.y.iloc[outside-1]], step_len, polyg, theta)

                pos = path_fwd.copy(deep=True)
                pos = rotate_points(pos.iloc[outside:], theta2, path_fwd.iloc[rows_i[outside - 2]].values)
                path_fwd.x.iloc[outside:] = np.squeeze(np.asarray(pos[0]))
                path_fwd.y.iloc[outside:] = np.squeeze(np.asarray(pos[1]))

            in_poly = Polygon(path_fwd.values).within(polyg)

    return path_fwd

"""
These are function that are part of crw_in_polygon
"""
def vector_heading(x, y):
    """
    Calculate direction (heading) of a vector (in degrees)

    :param x: A numeric vector of x coordinates; minimum of 2.

    :param y:  A numeric vector of y coordinates; minimum of 2.

    :return:A numeric scalar with heading in degrees or a numeric vector of
    headings if \code{length(x) > 2}.

    """
    theta_rad = math.atan2(np.diff(x), np.diff(y))
    theta_deg = theta_rad * 180 / 3.141593
    theta_deg = theta_deg - 360 * (theta_deg > 360)
    return theta_deg


def crw(theta=[0, 5], step_len=10, init_pos=[0, 0], init_heading=0, nsteps=10000):
    """
    Simulate a random walk as series of equal-length steps with turning angles
    drawn from a normal distribution.

    :param theta:A numeric vector of x (first element) and y (second element)
    coordinates for the point around which \code{x} and \code{y} will rotate.

    :param step_len: A numeric scalar with total distance moved in each step.

    :param init_pos: A 2-element numeric vector with nital position (initPos[1]=x,
    initPos[2]=y).

    :param init_heading: A numeric scalar with initial heading in degrees.

    :param nsteps: A numeric scalar with number of steps to simulate.

    :return: A two-column data frame containing:
    * x {x coordinates]
    * y {y coordinates}
    """
    heading = np.random.normal(theta[0], theta[1], nsteps)
    heading = np.cumsum(heading) + init_heading
    heading = heading % 360

    heading_rad = heading * (3.141593 / 180)

    xlen = np.sin(heading_rad) * step_len
    xlen = np.cumsum(xlen) + init_pos[0]

    ylen = np.cos(heading_rad) * step_len
    ylen = np.cumsum(ylen) + init_pos[1]

    path = pd.DataFrame({'x': xlen, 'y': ylen})

    return path


def rotate_points(pos, theta, focus):
    """
     Rotate points around a point in a 2-d plane

    :param pos: A dataframe containing the x and y coordinates; minunumum of 2.

    :param theta: A numeric scalar with the angle of rotation in degrees;
    positive is clockwise.

    :param focus:A numeric vector of x (first element) and y (second element)
    coordinates for the point around which \code{x} and \code{y} will rotate.

    :return: a two column matrix of x and y coordinates
    """
    theta_rad = theta * (3.141593 / 180)

    rot = np.matrix([[math.cos(theta_rad), math.sin(theta_rad)], [-math.sin(theta_rad), math.cos(theta_rad)]])

    pos.x = pos.x - focus[0]
    pos.y = pos.y - focus[1]

    pos = rot * np.transpose(pos.values)

    pos[0] = pos[0] + focus[0]
    pos[1] = pos[1] + focus[1]

    return pos